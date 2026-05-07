from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import random
import re
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import RLock
from typing import Any
from urllib.parse import parse_qs, urlparse

DEFAULT_JWT_SECRET = "Y2FtcHVzZmxvdy1kZW1vLXNlY3JldC1mb3ItamF2YS1iYWNrZW5kLTIwMjY="
JWT_HMAC_ALGORITHMS = {
    "HS256": hashlib.sha256,
    "HS384": hashlib.sha384,
    "HS512": hashlib.sha512,
}
TOKEN_JSON_KEYS = ("token", "accessToken", "access_token", "jwt", "idToken", "id_token")


class BusinessError(Exception):
    def __init__(self, message: str, code: int = 400, http_status: int | None = None):
        super().__init__(message)
        self.code = code
        self.http_status = http_status or (code if 400 <= code < 600 else 400)


def _now() -> datetime:
    return datetime.now().replace(microsecond=0)


def _iso(value: datetime | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.replace(microsecond=0).isoformat()
    return value


def _dt(value: datetime | str | None) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.replace(microsecond=0)
    text = str(value).replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is not None:
        parsed = parsed.replace(tzinfo=None)
    return parsed.replace(microsecond=0)


def _tags(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [part.strip() for part in str(value).split(",") if part.strip()]


def _int(value: Any, default: int | None = None) -> int | None:
    if value is None or value == "":
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _bool(value: Any, default: bool | None = None) -> bool | None:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    return str(value).lower() in {"1", "true", "yes", "on"}


def _urlsafe_b64decode(value: str) -> bytes:
    padded = value + "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(padded.encode())


def _decode_json_segment(value: str) -> dict[str, Any]:
    data = json.loads(_urlsafe_b64decode(value).decode())
    if not isinstance(data, dict):
        raise ValueError("JWT segment must decode to a JSON object")
    return data


def _jwt_secret() -> bytes:
    secret = os.environ.get("CAMPUSFLOW_JWT_SECRET", DEFAULT_JWT_SECRET)
    try:
        return base64.b64decode(secret, validate=True)
    except Exception:
        return secret.encode()


def _strip_token_quotes(token: str) -> str:
    token = token.strip()
    while len(token) >= 2 and token[0] == token[-1] and token[0] in {"'", '"'}:
        token = token[1:-1].strip()
    return token


def _normalize_token(value: str | None) -> str | None:
    token = _strip_token_quotes(str(value or ""))
    for _ in range(4):
        parts = token.split(None, 1)
        if len(parts) != 2 or parts[0].lower() not in {"bearer", "token"}:
            break
        token = _strip_token_quotes(parts[1])
    if token.startswith("{"):
        try:
            data = json.loads(token)
            if isinstance(data, dict):
                for key in TOKEN_JSON_KEYS:
                    nested = data.get(key)
                    if nested:
                        return _normalize_token(str(nested))
        except Exception:
            pass
    return token or None


def _decode_legacy_jwt(token: str) -> dict[str, Any] | None:
    try:
        header_segment, payload_segment, signature_segment = token.split(".")
        header = _decode_json_segment(header_segment)
        digestmod = JWT_HMAC_ALGORITHMS.get(str(header.get("alg") or ""))
        if digestmod is None:
            return None
        signing_input = f"{header_segment}.{payload_segment}".encode()
        expected_signature = hmac.new(_jwt_secret(), signing_input, digestmod).digest()
        actual_signature = _urlsafe_b64decode(signature_segment)
        if not hmac.compare_digest(expected_signature, actual_signature):
            return None
        payload = _decode_json_segment(payload_segment)
        now_ts = datetime.now().timestamp()
        exp = _int(payload.get("exp"))
        nbf = _int(payload.get("nbf"))
        if exp is not None and now_ts >= exp:
            return None
        if nbf is not None and now_ts < nbf:
            return None
        return payload
    except Exception:
        return None


def _page(records: list[dict[str, Any]], params: dict[str, Any]) -> dict[str, Any]:
    page_num = max(_int(params.get("pageNum"), 1) or 1, 1)
    page_size = max(_int(params.get("pageSize"), 10) or 10, 1)
    start = (page_num - 1) * page_size
    return {"total": len(records), "records": records[start : start + page_size]}


class CampusFlowStore:
    def __init__(self) -> None:
        self.lock = RLock()
        self._ids: defaultdict[str, int] = defaultdict(lambda: 1)
        self.users: list[dict[str, Any]] = []
        self.activities: list[dict[str, Any]] = []
        self.teams: list[dict[str, Any]] = []
        self.team_members: list[dict[str, Any]] = []
        self.applications: list[dict[str, Any]] = []
        self.notifications: list[dict[str, Any]] = []
        self.sign_records: list[dict[str, Any]] = []
        self.feedbacks: list[dict[str, Any]] = []
        self.announcements: list[dict[str, Any]] = []
        self.seed()

    def next_id(self, table: str) -> int:
        value = self._ids[table]
        self._ids[table] += 1
        return value

    def seed(self) -> None:
        student01 = self.add_user("student01", "Alice", "alice@campusflow.local", "student")
        student02 = self.add_user("student02", "Brian", "brian@campusflow.local", "student")
        student03 = self.add_user("student03", "Clara", "clara@campusflow.local", "student")
        captain = self.add_user("captain01", "Bob", "bob@campusflow.local", "captain")
        organizer = self.add_user("organizer01", "Cindy", "cindy@campusflow.local", "organizer")
        admin = self.add_user("admin01", "David", "david@campusflow.local", "admin")

        now = _now()
        innovation = self.add_activity(
            title="校园创新挑战赛",
            coverUrl="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1200&q=80",
            description="面向全校学生的跨学科创新协作活动，聚焦校园服务、可持续发展与数字化场景。",
            organizerId=organizer["id"],
            type="创新竞赛",
            location="图书馆报告厅",
            startTime=now + timedelta(days=7),
            endTime=now + timedelta(days=7, hours=4),
            signupDeadline=now + timedelta(days=3),
            requireTeam=True,
            minTeamSize=3,
            maxTeamSize=5,
            status="signup_open",
            tags=["创新", "协作", "路演"],
            signCode="SIGN2026",
            signStartTime=now + timedelta(days=7, hours=-1),
            signEndTime=now + timedelta(days=7, hours=1),
        )
        workshop = self.add_activity(
            title="志愿服务培训营",
            coverUrl="https://images.unsplash.com/photo-1529156069898-49953e39b3ac?auto=format&fit=crop&w=1200&q=80",
            description="面向志愿者的服务流程培训与现场协同演练，帮助同学熟悉大型活动服务规范。",
            organizerId=organizer["id"],
            type="志愿服务",
            location="学生活动中心 201",
            startTime=now - timedelta(days=5),
            endTime=now - timedelta(days=5, hours=-3),
            signupDeadline=now - timedelta(days=8),
            requireTeam=False,
            minTeamSize=1,
            maxTeamSize=1,
            status="finished",
            tags=["培训", "志愿", "服务"],
            signCode="SERVICE26",
            signStartTime=now - timedelta(days=5, hours=1),
            signEndTime=now - timedelta(days=5, hours=-2),
            resultSummary="培训营顺利完成，共有 86 名同学完成现场签到，反馈平均分 4.8。",
        )
        hack_night = self.add_activity(
            title="AI Hack Night",
            coverUrl="https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1200&q=80",
            description="围绕校园应用场景开展一晚上的 AI 原型共创，强调快速协作与创意实现。",
            organizerId=organizer["id"],
            type="技术沙龙",
            location="信息楼 A301",
            startTime=now + timedelta(days=14),
            endTime=now + timedelta(days=14, hours=6),
            signupDeadline=now + timedelta(days=10),
            requireTeam=True,
            minTeamSize=2,
            maxTeamSize=4,
            status="signup_open",
            tags=["AI", "原型", "黑客松"],
            signCode="HACK2026",
            signStartTime=now + timedelta(days=14, hours=-1),
            signEndTime=now + timedelta(days=14, hours=2),
        )

        submitted = self.add_team(
            innovation["id"],
            "Campus Masters",
            captain["id"],
            "协作赢未来",
            "专注创新方案与执行落地",
            "submitted",
        )
        self.add_member(submitted["id"], captain["id"], "leader", "approved", now - timedelta(days=1))
        self.add_member(submitted["id"], student02["id"], "member", "approved", now - timedelta(hours=20))
        self.add_member(submitted["id"], student03["id"], "member", "approved", now - timedelta(hours=18))
        self.add_application(
            innovation["id"],
            submitted["id"],
            captain["id"],
            "signup_team",
            "pending",
            "我们已完成队伍组建，希望参加创新挑战赛。",
        )

        forming = self.add_team(
            hack_night["id"],
            "Idea Spark",
            student02["id"],
            "今晚就把想法做出来",
            "欢迎擅长产品、前端和算法的同学加入",
            "forming",
        )
        self.add_member(forming["id"], student02["id"], "leader", "approved", now - timedelta(hours=10))
        self.add_member(forming["id"], student03["id"], "member", "pending", None)
        self.add_application(
            hack_night["id"],
            forming["id"],
            student03["id"],
            "join_team",
            "pending",
            "我擅长前端原型和交互实现，希望一起参加。",
        )

        self.seed_showcase_activities(now, organizer, captain, student01, student02, student03)

        self.create_notice(captain["id"], "报名已提交", "队伍 Campus Masters 已提交创新挑战赛报名，请等待组织者审核。", "review_result")
        self.create_notice(student03["id"], "入队申请已发送", "你对队伍 Idea Spark 的申请已提交，请等待队长审核。", "team_apply")
        self.create_notice(admin["id"], "系统巡检提醒", "当前演示环境已初始化，可使用管理员账号发布公告。", "system", is_read=True)

        self.add_sign_record(workshop["id"], student01["id"], "signed", now - timedelta(days=5, minutes=5))
        self.feedbacks.append(
            {
                "id": self.next_id("feedbacks"),
                "activityId": workshop["id"],
                "userId": student01["id"],
                "score": 5,
                "content": "培训流程很清晰，组织非常有序，签到和通知都很及时。",
                "tags": ["流程清晰", "通知及时", "组织有序"],
                "willingRejoin": True,
                "createdAt": _iso(now - timedelta(days=4)),
            }
        )
        self.announcements.append(
            {
                "id": self.next_id("announcements"),
                "title": "CampusFlow 演示环境已就绪",
                "content": "你可以使用示例账号体验活动浏览、组队报名、审核、通知、签到和反馈的完整流程。",
                "createdBy": admin["id"],
                "createdAt": _iso(now - timedelta(hours=2)),
            }
        )

    def seed_showcase_activities(
        self,
        now: datetime,
        organizer: dict[str, Any],
        captain: dict[str, Any],
        student01: dict[str, Any],
        student02: dict[str, Any],
        student03: dict[str, Any],
    ) -> None:
        activity_rows = [
            ("校园摄影漫步", "文化体验", "樱花大道与艺术楼", False, 2, 2, "signup_open", ["摄影", "校园", "美育"]),
            ("社团开放日市集", "社团招新", "南区广场", False, 3, 3, "published", ["社团", "市集", "展示"]),
            ("低碳校园行动周", "公益实践", "教学楼群", True, 4, 6, "signup_open", ["低碳", "公益", "实践"]),
            ("校园辩论挑战夜", "思辨竞赛", "人文楼报告厅", True, 4, 4, "signup_open", ["辩论", "表达", "团队"]),
            ("迎新志愿服务队", "志愿服务", "新生报到点", True, 5, 8, "signup_open", ["迎新", "志愿", "协作"]),
            ("数据可视化工作坊", "技术沙龙", "信息楼 B204", False, 1, 1, "signup_open", ["数据", "可视化", "工具"]),
            ("校园音乐草坪会", "艺术活动", "中心草坪", False, 1, 1, "published", ["音乐", "草坪", "开放麦"]),
            ("创业计划训练营", "创新竞赛", "创业学院 301", True, 3, 5, "signup_open", ["创业", "商业计划", "路演"]),
            ("心理健康同伴营", "成长支持", "心理中心团辅室", False, 1, 1, "signup_open", ["心理", "同伴", "成长"]),
            ("机器人创客赛", "技术竞赛", "工程训练中心", True, 3, 6, "signup_open", ["机器人", "创客", "竞赛"]),
            ("校园安全微课堂", "安全教育", "线上会议室", False, 1, 1, "published", ["安全", "课堂", "校园"]),
            ("非遗手作体验课", "文化体验", "美育工坊", False, 1, 1, "signup_open", ["非遗", "手作", "体验"]),
            ("运动嘉年华", "体育活动", "东区体育场", True, 4, 8, "signup_open", ["运动", "嘉年华", "团队"]),
            ("读书分享下午茶", "阅读活动", "图书馆咖啡角", False, 1, 1, "signup_open", ["阅读", "分享", "交流"]),
            ("校园产品经理训练", "技术沙龙", "信息楼 A401", True, 3, 5, "signup_open", ["产品", "原型", "调研"]),
            ("急救技能认证课", "安全教育", "校医院培训室", False, 1, 1, "signup_closed", ["急救", "技能", "认证"]),
            ("毕业季影像征集", "文化体验", "线上征集", False, 1, 1, "signup_open", ["影像", "毕业季", "征集"]),
            ("公益支教共创会", "公益实践", "明德楼 105", True, 4, 7, "signup_open", ["支教", "公益", "共创"]),
            ("算法趣味闯关赛", "技术竞赛", "信息楼机房", True, 3, 5, "signup_open", ["算法", "闯关", "竞赛"]),
            ("校园成果复盘会", "结果反馈", "图书馆研讨室", False, 1, 1, "finished", ["复盘", "反馈", "总结"]),
        ]
        for index, row in enumerate(activity_rows, start=1):
            title, activity_type, location, require_team, min_size, max_size, status, tags = row
            day_offset = index + 1
            if status == "finished":
                start_time = now - timedelta(days=2)
                signup_deadline = now - timedelta(days=6)
            elif status == "signup_closed":
                start_time = now + timedelta(days=day_offset)
                signup_deadline = now - timedelta(hours=8)
            else:
                start_time = now + timedelta(days=day_offset)
                signup_deadline = start_time - timedelta(days=2)
            end_time = start_time + timedelta(hours=3)
            activity = self.add_activity(
                title=title,
                coverUrl=f"https://picsum.photos/seed/campusflow-{index:02d}/1200/800",
                description=f"{title} 面向全校开放，四类角色账号都已预置参与路径，适合前端演示和流程测试。",
                organizerId=organizer["id"],
                type=activity_type,
                location=location,
                startTime=start_time,
                endTime=end_time,
                signupDeadline=signup_deadline,
                requireTeam=require_team,
                minTeamSize=min_size,
                maxTeamSize=max_size,
                status=status,
                tags=tags,
                signCode=f"CF{index:02d}26",
                signStartTime=start_time - timedelta(hours=1),
                signEndTime=start_time + timedelta(hours=2),
                resultSummary="本场活动已完成复盘，可查看签到和反馈链路。" if status == "finished" else None,
            )
            if require_team:
                leaders = [student02, student03, captain]
                leader = leaders[index % len(leaders)]
                sample_team = self.add_team(
                    activity["id"],
                    f"{title}招募队",
                    leader["id"],
                    "欢迎同学申请加入",
                    "这是一个正在招募成员的示例队伍。创建队伍的同学会自动成为队长，申请加入的同学由队长审核后成为队员。",
                    "forming",
                )
                self.add_member(sample_team["id"], leader["id"], "leader", "approved", now - timedelta(hours=index))
            else:
                if status == "finished":
                    for participant in [student01, student02, student03, captain]:
                        self.add_sign_record(
                            activity["id"],
                            participant["id"],
                            "signed",
                            start_time + timedelta(minutes=10),
                        )

    def add_user(self, username: str, nickname: str, email: str, role: str) -> dict[str, Any]:
        user = {
            "id": self.next_id("users"),
            "username": username,
            "password": "123456",
            "nickname": nickname,
            "avatar": f"https://api.dicebear.com/7.x/initials/svg?seed={nickname}",
            "email": email,
            "role": role,
            "status": 1,
        }
        self.users.append(user)
        return user

    def add_activity(self, **data: Any) -> dict[str, Any]:
        now = _now()
        activity = {
            "id": self.next_id("activities"),
            "title": data["title"],
            "coverUrl": data.get("coverUrl"),
            "description": data["description"],
            "organizerId": data["organizerId"],
            "type": data["type"],
            "location": data["location"],
            "startTime": _iso(data["startTime"]),
            "endTime": _iso(data["endTime"]),
            "signupDeadline": _iso(data["signupDeadline"]),
            "requireTeam": bool(data["requireTeam"]),
            "minTeamSize": int(data["minTeamSize"]),
            "maxTeamSize": int(data["maxTeamSize"]),
            "status": data.get("status", "signup_open"),
            "tags": _tags(data.get("tags")),
            "signCode": data.get("signCode") or self.generate_sign_code(),
            "signStartTime": _iso(data.get("signStartTime")),
            "signEndTime": _iso(data.get("signEndTime")),
            "resultSummary": data.get("resultSummary"),
            "createdAt": _iso(data.get("createdAt") or now),
        }
        self.activities.append(activity)
        return activity

    def add_team(
        self,
        activity_id: int,
        team_name: str,
        leader_id: int,
        slogan: str | None,
        description: str | None,
        status: str,
    ) -> dict[str, Any]:
        team_id = self.next_id("teams")
        team = {
            "id": team_id,
            "activityId": activity_id,
            "teamName": team_name,
            "leaderId": leader_id,
            "slogan": slogan,
            "description": description,
            "inviteCode": f"CF-DEMO-{team_id}",
            "status": status,
            "createdAt": _iso(_now()),
        }
        self.teams.append(team)
        return team

    def add_member(
        self,
        team_id: int,
        user_id: int,
        member_role: str,
        join_status: str,
        joined_at: datetime | str | None,
    ) -> dict[str, Any]:
        member = {
            "id": self.next_id("team_members"),
            "teamId": team_id,
            "userId": user_id,
            "memberRole": member_role,
            "joinStatus": join_status,
            "joinedAt": _iso(joined_at),
        }
        self.team_members.append(member)
        return member

    def add_application(
        self,
        activity_id: int,
        team_id: int | None,
        applicant_id: int,
        app_type: str,
        status: str,
        reason: str | None,
    ) -> dict[str, Any]:
        record = {
            "id": self.next_id("applications"),
            "activityId": activity_id,
            "teamId": team_id,
            "applicantId": applicant_id,
            "type": app_type,
            "status": status,
            "reason": reason,
            "reviewComment": None,
            "reviewedBy": None,
            "reviewedAt": None,
            "createdAt": _iso(_now()),
        }
        self.applications.append(record)
        return record

    def add_sign_record(self, activity_id: int, user_id: int, status: str, sign_time: datetime | str | None = None) -> dict[str, Any]:
        record = {
            "id": self.next_id("sign_records"),
            "activityId": activity_id,
            "userId": user_id,
            "signType": "code",
            "status": status,
            "signTime": _iso(sign_time),
        }
        self.sign_records.append(record)
        return record

    def generate_sign_code(self) -> str:
        return f"SIGN-{uuid.uuid4().hex[:8].upper()}"

    def generate_invite_code(self) -> str:
        return f"CF-{uuid.uuid4().hex[:8].upper()}"

    def make_token(self, user: dict[str, Any]) -> str:
        payload = json.dumps({"id": user["id"], "username": user["username"]}, separators=(",", ":")).encode()
        return "demo." + base64.urlsafe_b64encode(payload).decode().rstrip("=")

    def user_from_token(self, token: str | None) -> dict[str, Any] | None:
        if not token:
            return None
        if not token.startswith("demo."):
            return self.user_from_legacy_jwt(token)
        try:
            raw = token.removeprefix("demo.")
            payload = json.loads(_urlsafe_b64decode(raw).decode())
            return self.user_by_id(_int(payload.get("id")))
        except Exception:
            return None

    def user_from_legacy_jwt(self, token: str) -> dict[str, Any] | None:
        payload = _decode_legacy_jwt(token)
        if payload is None:
            return None
        username = str(
            payload.get("username")
            or payload.get("userName")
            or payload.get("preferred_username")
            or payload.get("login")
            or payload.get("account")
            or ""
        ).strip()
        if username:
            user = self.user_by_username(username)
            if user is not None:
                return user
        subject = str(payload.get("sub") or "").strip()
        if subject:
            user = self.user_by_username(subject)
            if user is not None:
                return user
        email = str(payload.get("email") or "").strip()
        if email:
            user = self.user_by_email(email)
            if user is not None:
                return user
        return self.user_by_id(_int(payload.get("sub") or payload.get("id") or payload.get("userId") or payload.get("user_id") or payload.get("uid")))

    def user_by_id(self, user_id: int | None) -> dict[str, Any] | None:
        return next((user for user in self.users if user["id"] == user_id), None)

    def user_by_username(self, username: str) -> dict[str, Any] | None:
        return next((user for user in self.users if user["username"] == username), None)

    def user_by_email(self, email: str) -> dict[str, Any] | None:
        return next((user for user in self.users if user.get("email") == email), None)

    def activity_by_id(self, activity_id: int | None) -> dict[str, Any] | None:
        return next((activity for activity in self.activities if activity["id"] == activity_id), None)

    def team_by_id(self, team_id: int | None) -> dict[str, Any] | None:
        return next((team for team in self.teams if team["id"] == team_id), None)

    def application_by_id(self, application_id: int | None) -> dict[str, Any] | None:
        return next((record for record in self.applications if record["id"] == application_id), None)

    def signup_accepting(self, activity: dict[str, Any]) -> bool:
        deadline = _dt(activity.get("signupDeadline"))
        return activity.get("status") == "signup_open" and (deadline is None or _now() <= deadline)

    def personal_signup_record(self, activity_id: int, user_id: int) -> dict[str, Any] | None:
        records = [
            record
            for record in self.applications
            if record["activityId"] == activity_id
            and record["applicantId"] == user_id
            and record["type"] == "signup_personal"
        ]
        records.sort(key=lambda item: item["createdAt"], reverse=True)
        return records[0] if records else None

    def sign_record(self, activity_id: int, user_id: int) -> dict[str, Any] | None:
        return next(
            (record for record in self.sign_records if record["activityId"] == activity_id and record["userId"] == user_id),
            None,
        )

    def organizer_name(self, organizer_id: int) -> str:
        organizer = self.user_by_id(organizer_id)
        return organizer["nickname"] if organizer else "未知组织者"

    def user_profile(self, user: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": user["id"],
            "username": user["username"],
            "nickname": user["nickname"],
            "avatar": user.get("avatar"),
            "email": user.get("email"),
            "role": user.get("role", "student"),
        }

    def activity_card(self, activity: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": activity["id"],
            "title": activity["title"],
            "coverUrl": activity.get("coverUrl"),
            "organizerName": self.organizer_name(activity["organizerId"]),
            "type": activity["type"],
            "location": activity["location"],
            "startTime": activity["startTime"],
            "signupDeadline": activity["signupDeadline"],
            "requireTeam": activity["requireTeam"],
            "status": activity["status"],
            "tags": list(activity.get("tags") or []),
        }

    def login(self, payload: dict[str, Any]) -> dict[str, Any]:
        username = str(payload.get("username") or "").strip()
        password = str(payload.get("password") or "")
        if not username or not password:
            raise BusinessError("用户名和密码不能为空", 400, 400)
        user = next((item for item in self.users if item["username"] == username), None)
        if user is None or user["password"] != password:
            raise BusinessError("用户名或密码错误", 401, 401)
        return {"token": self.make_token(user), "userInfo": self.user_profile(user)}

    def update_profile(self, user: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        nickname = str(payload.get("nickname") or user["nickname"]).strip()
        if not nickname:
            raise BusinessError("昵称不能为空")
        email = payload.get("email")
        if email:
            duplicated = next((item for item in self.users if item["email"] == email and item["id"] != user["id"]), None)
            if duplicated:
                raise BusinessError("邮箱已被占用", 409, 409)
        user["nickname"] = nickname
        user["avatar"] = payload.get("avatar")
        user["email"] = email
        return self.user_profile(user)

    def page_activities(self, params: dict[str, Any]) -> dict[str, Any]:
        keyword = str(params.get("keyword") or "").strip().lower()
        activity_type = str(params.get("type") or "").strip()
        status = str(params.get("status") or "").strip()
        require_team = _bool(params.get("requireTeam"), None)
        records = []
        for activity in self.activities:
            if keyword and keyword not in activity["title"].lower():
                continue
            if activity_type and activity["type"] != activity_type:
                continue
            if require_team is not None and activity["requireTeam"] != require_team:
                continue
            if status and activity["status"] != status:
                continue
            if not status and activity["status"] == "draft":
                continue
            records.append(activity)
        records.sort(key=lambda item: item["startTime"])
        return _page([self.activity_card(item) for item in records], params)

    def activity_detail(self, activity_id: int, user: dict[str, Any] | None) -> dict[str, Any]:
        activity = self.activity_by_id(activity_id)
        if activity is None:
            raise BusinessError("活动不存在", 404, 404)
        team_count = len([team for team in self.teams if team["activityId"] == activity_id])
        my_team_id = None
        my_application_status = None
        can_create_team = bool(activity["requireTeam"] and self.signup_accepting(activity))
        can_apply_team = bool(activity["requireTeam"] and self.signup_accepting(activity))
        can_signup_personal = bool(not activity["requireTeam"] and self.signup_accepting(activity))
        can_sign_in = False
        can_feedback = False
        if user:
            for membership in self.team_members:
                if membership["userId"] != user["id"] or membership["joinStatus"] not in {"pending", "approved"}:
                    continue
                team = self.team_by_id(membership["teamId"])
                if team and team["activityId"] == activity_id:
                    my_team_id = team["id"]
                    my_application_status = membership["joinStatus"]
                    can_create_team = False
                    can_apply_team = False
                    break
            if not activity["requireTeam"]:
                personal_record = self.personal_signup_record(activity_id, user["id"])
                if personal_record is not None:
                    my_application_status = personal_record["status"]
                    if personal_record["status"] in {"pending", "approved"}:
                        can_signup_personal = False
            sign_record = self.sign_record(activity_id, user["id"])
            can_sign_in = self.is_eligible(user["id"], activity)
            can_feedback = bool(sign_record and sign_record["status"] == "signed")
            if any(item["activityId"] == activity_id and item["userId"] == user["id"] for item in self.feedbacks):
                can_feedback = False
            if sign_record is not None:
                can_signup_personal = False
        detail = self.activity_card(activity)
        detail.update(
            {
                "description": activity["description"],
                "organizerId": activity["organizerId"],
                "endTime": activity["endTime"],
                "minTeamSize": activity["minTeamSize"],
                "maxTeamSize": activity["maxTeamSize"],
                "teamCount": team_count,
                "myTeamId": my_team_id,
                "myApplicationStatus": my_application_status,
                "canCreateTeam": can_create_team,
                "canApplyTeam": can_apply_team,
                "canSignupPersonal": can_signup_personal,
                "canSignIn": can_sign_in,
                "canFeedback": can_feedback,
                "resultSummary": activity.get("resultSummary"),
            }
        )
        return detail

    def my_activities(self, user: dict[str, Any]) -> list[dict[str, Any]]:
        records = [item for item in self.activities if item["organizerId"] == user["id"]]
        records.sort(key=lambda item: item["createdAt"], reverse=True)
        return [self.activity_card(item) for item in records]

    def save_activity(self, user: dict[str, Any], payload: dict[str, Any], activity_id: int | None = None) -> dict[str, Any]:
        if user["role"] not in {"organizer", "admin"}:
            raise BusinessError("仅组织者或管理员可管理活动", 403, 403)
        activity = self.activity_by_id(activity_id) if activity_id is not None else None
        if activity_id is not None and activity is None:
            raise BusinessError("活动不存在", 404, 404)
        if activity is not None and user["role"] != "admin" and activity["organizerId"] != user["id"]:
            raise BusinessError("仅组织者或管理员可管理活动", 403, 403)

        required = ["title", "description", "type", "location", "startTime", "endTime", "signupDeadline"]
        missing = [field for field in required if not payload.get(field)]
        if missing:
            raise BusinessError("缺少必要字段：" + ",".join(missing))
        start = _dt(payload["startTime"])
        end = _dt(payload["endTime"])
        signup_deadline = _dt(payload["signupDeadline"])
        sign_start = _dt(payload.get("signStartTime"))
        sign_end = _dt(payload.get("signEndTime"))
        if end and start and end < start:
            raise BusinessError("活动结束时间不能早于开始时间")
        if signup_deadline and start and signup_deadline > start:
            raise BusinessError("报名截止时间必须早于活动开始时间")
        min_size = _int(payload.get("minTeamSize"), 1) or 1
        max_size = _int(payload.get("maxTeamSize"), 1) or 1
        if max_size < min_size:
            raise BusinessError("最大队伍人数不能小于最小队伍人数")
        if sign_start and sign_end and sign_end < sign_start:
            raise BusinessError("签到结束时间不能早于签到开始时间")

        data = {
            "title": str(payload.get("title")).strip(),
            "coverUrl": payload.get("coverUrl"),
            "description": str(payload.get("description")).strip(),
            "type": str(payload.get("type")).strip(),
            "location": str(payload.get("location")).strip(),
            "startTime": _iso(start),
            "endTime": _iso(end),
            "signupDeadline": _iso(signup_deadline),
            "requireTeam": bool(payload.get("requireTeam")),
            "minTeamSize": min_size,
            "maxTeamSize": max_size,
            "status": payload.get("status") or "signup_open",
            "tags": _tags(payload.get("tags")),
            "signCode": payload.get("signCode") or self.generate_sign_code(),
            "signStartTime": _iso(sign_start),
            "signEndTime": _iso(sign_end),
            "resultSummary": payload.get("resultSummary"),
        }
        if activity is None:
            data["id"] = self.next_id("activities")
            data["organizerId"] = user["id"]
            data["createdAt"] = _iso(_now())
            self.activities.append(data)
            activity = data
        else:
            activity.update(data)
        return self.activity_detail(activity["id"], user)

    def update_activity_status(self, user: dict[str, Any], activity_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        if user["role"] not in {"organizer", "admin"}:
            raise BusinessError("仅组织者或管理员可调整活动状态", 403, 403)
        activity = self.activity_by_id(activity_id)
        if activity is None:
            raise BusinessError("活动不存在", 404, 404)
        if user["role"] != "admin" and activity["organizerId"] != user["id"]:
            raise BusinessError("仅活动组织者或管理员可调整该活动", 403, 403)
        status = str(payload.get("status") or "").strip()
        allowed = {"draft", "published", "signup_open", "signup_closed", "finished", "cancelled"}
        if status not in allowed:
            raise BusinessError("活动状态不合法")
        activity["status"] = status
        if "resultSummary" in payload:
            activity["resultSummary"] = payload.get("resultSummary")
        if status == "cancelled":
            self.create_batch_notices(
                self.activity_participant_ids(activity_id, include_pending=True),
                "活动已取消",
                f"活动「{activity['title']}」已取消，请关注后续安排。",
                "activity_reminder",
            )
        elif status == "finished":
            self.create_batch_notices(
                self.activity_participant_ids(activity_id),
                "活动已结束",
                f"活动「{activity['title']}」已结束，已签到参与者可以提交反馈。",
                "activity_reminder",
            )
        return self.activity_detail(activity_id, user)

    def signup_activity(self, user: dict[str, Any], activity_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        activity = self.activity_by_id(activity_id)
        if activity is None:
            raise BusinessError("活动不存在", 404, 404)
        if activity["requireTeam"]:
            raise BusinessError("当前活动需要组队，请创建或加入队伍")
        if not self.signup_accepting(activity):
            raise BusinessError("当前活动不在报名开放时间内")
        record = self.personal_signup_record(activity_id, user["id"])
        if record is not None and record["status"] in {"pending", "approved"}:
            raise BusinessError("你已提交过该活动报名", 409, 409)
        if self.sign_record(activity_id, user["id"]) is not None:
            raise BusinessError("你已获得该活动参与资格", 409, 409)
        record = self.add_application(activity_id, None, user["id"], "signup_personal", "pending", payload.get("reason"))
        self.create_notice(
            activity["organizerId"],
            "新的个人报名待审核",
            f"{user['nickname']} 已提交活动「{activity['title']}」的个人报名，请及时审核。",
            "review_result",
        )
        return {"applicationId": record["id"], "status": record["status"]}

    def approved_member_count(self, team_id: int) -> int:
        return len([item for item in self.team_members if item["teamId"] == team_id and item["joinStatus"] == "approved"])

    def assert_not_in_activity_team(self, user_id: int, activity_id: int) -> None:
        for membership in self.team_members:
            if membership["userId"] != user_id or membership["joinStatus"] not in {"pending", "approved"}:
                continue
            team = self.team_by_id(membership["teamId"])
            if team and team["activityId"] == activity_id:
                raise BusinessError("你已在当前活动的队伍中或申请待审核", 409, 409)

    def create_team(self, user: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        activity_id = _int(payload.get("activityId"))
        activity = self.activity_by_id(activity_id)
        if activity is None:
            raise BusinessError("活动不存在", 404, 404)
        if not activity["requireTeam"]:
            raise BusinessError("当前活动不允许组队")
        if not self.signup_accepting(activity):
            raise BusinessError("当前活动不在报名开放时间内")
        self.assert_not_in_activity_team(user["id"], activity["id"])
        team_name = str(payload.get("teamName") or "").strip()
        if not team_name:
            raise BusinessError("队伍名称不能为空")
        duplicated = any(team["activityId"] == activity["id"] and team["teamName"] == team_name for team in self.teams)
        if duplicated:
            raise BusinessError("同一活动下队伍名称不能重复", 409, 409)
        team = {
            "id": self.next_id("teams"),
            "activityId": activity["id"],
            "teamName": team_name,
            "leaderId": user["id"],
            "slogan": payload.get("slogan"),
            "description": payload.get("description"),
            "inviteCode": self.generate_invite_code(),
            "status": "forming",
            "createdAt": _iso(_now()),
        }
        self.teams.append(team)
        self.add_member(team["id"], user["id"], "leader", "approved", _now())
        return {"teamId": team["id"], "inviteCode": team["inviteCode"]}

    def team_detail(self, team_id: int, user: dict[str, Any] | None) -> dict[str, Any]:
        team = self.team_by_id(team_id)
        if team is None:
            raise BusinessError("队伍不存在", 404, 404)
        activity = self.activity_by_id(team["activityId"])
        if activity is None:
            raise BusinessError("活动不存在", 404, 404)
        leader = self.user_by_id(team["leaderId"])
        members = []
        for member in sorted(self.team_members, key=lambda item: item.get("joinedAt") or ""):
            if member["teamId"] == team_id and member["joinStatus"] == "approved":
                member_user = self.user_by_id(member["userId"])
                members.append(
                    {
                        "userId": member["userId"],
                        "nickname": member_user["nickname"] if member_user else "未知用户",
                        "avatar": member_user.get("avatar") if member_user else None,
                        "memberRole": member["memberRole"],
                        "joinStatus": member["joinStatus"],
                        "joinedAt": member.get("joinedAt"),
                    }
                )
        applications = []
        for record in sorted(self.applications, key=lambda item: item["createdAt"], reverse=True):
            if record["teamId"] == team_id and record["type"] == "join_team" and record["status"] == "pending":
                applicant = self.user_by_id(record["applicantId"])
                applications.append(
                    {
                        "id": record["id"],
                        "applicantId": record["applicantId"],
                        "applicantName": applicant["nickname"] if applicant else "未知用户",
                        "type": record["type"],
                        "status": record["status"],
                        "reason": record.get("reason"),
                        "reviewComment": record.get("reviewComment"),
                        "createdAt": record["createdAt"],
                    }
                )
        return {
            "id": team["id"],
            "activityId": activity["id"],
            "activityTitle": activity["title"],
            "teamName": team["teamName"],
            "leaderId": team["leaderId"],
            "leaderName": leader["nickname"] if leader else "未知队长",
            "slogan": team.get("slogan"),
            "description": team.get("description"),
            "inviteCode": team["inviteCode"],
            "status": team["status"],
            "currentSize": len(members),
            "minTeamSize": activity["minTeamSize"],
            "maxTeamSize": activity["maxTeamSize"],
            "canManage": bool(user and user["id"] == team["leaderId"]),
            "members": members,
            "pendingApplications": applications,
        }

    def joinable_teams(self, user: dict[str, Any] | None, params: dict[str, Any]) -> dict[str, Any]:
        keyword = str(params.get("keyword") or "").strip().lower()
        activity_id = _int(params.get("activityId"))
        records = []
        for team in self.teams:
            if team["status"] != "forming":
                continue
            if keyword and keyword not in team["teamName"].lower():
                continue
            if activity_id is not None and team["activityId"] != activity_id:
                continue
            activity = self.activity_by_id(team["activityId"])
            if activity is None:
                continue
            leader = self.user_by_id(team["leaderId"])
            applied = False
            joined = False
            joined_other_activity_team = False
            if user:
                applied = any(
                    record["teamId"] == team["id"]
                    and record["applicantId"] == user["id"]
                    and record["type"] == "join_team"
                    and record["status"] == "pending"
                    for record in self.applications
                )
                for membership in self.team_members:
                    if membership["userId"] != user["id"] or membership["joinStatus"] not in {"pending", "approved"}:
                        continue
                    membership_team = self.team_by_id(membership["teamId"])
                    if membership_team is None or membership_team["activityId"] != team["activityId"]:
                        continue
                    if membership_team["id"] == team["id"]:
                        joined = True
                    else:
                        joined_other_activity_team = True
            current_size = self.approved_member_count(team["id"])
            records.append(
                {
                    "id": team["id"],
                    "activityId": team["activityId"],
                    "activityTitle": activity["title"],
                    "teamName": team["teamName"],
                    "slogan": team.get("slogan"),
                    "description": team.get("description"),
                    "leaderId": team["leaderId"],
                    "leaderName": leader["nickname"] if leader else "未知队长",
                    "currentSize": current_size,
                    "maxTeamSize": activity["maxTeamSize"],
                    "status": team["status"],
                    "applied": applied,
                    "joined": joined,
                    "canApply": bool(
                        user
                        and not applied
                        and not joined
                        and not joined_other_activity_team
                        and current_size < activity["maxTeamSize"]
                    ),
                }
            )
        records.sort(key=lambda item: item["id"], reverse=True)
        return _page(records, params)

    def apply_to_team(self, user: dict[str, Any], team_id: int, payload: dict[str, Any]) -> None:
        team = self.team_by_id(team_id)
        if team is None:
            raise BusinessError("队伍不存在", 404, 404)
        activity = self.activity_by_id(team["activityId"])
        if activity is None:
            raise BusinessError("活动不存在", 404, 404)
        if team["status"] != "forming":
            raise BusinessError("当前队伍不可申请加入")
        if not self.signup_accepting(activity):
            raise BusinessError("当前活动不在报名开放时间内")
        if self.approved_member_count(team_id) >= activity["maxTeamSize"]:
            raise BusinessError("队伍人数已满")
        if user["id"] == team["leaderId"]:
            raise BusinessError("队长无需重复申请")
        self.assert_not_in_activity_team(user["id"], activity["id"])
        if any(
            record["teamId"] == team_id
            and record["applicantId"] == user["id"]
            and record["type"] == "join_team"
            and record["status"] == "pending"
            for record in self.applications
        ):
            raise BusinessError("你已经申请过该队伍", 409, 409)
        member = next((item for item in self.team_members if item["teamId"] == team_id and item["userId"] == user["id"]), None)
        if member is None:
            self.add_member(team_id, user["id"], "member", "pending", None)
        elif member["joinStatus"] in {"approved", "pending"}:
            raise BusinessError("你已经在该队伍中或申请正在审核", 409, 409)
        else:
            member["joinStatus"] = "pending"
            member["joinedAt"] = None
        self.add_application(activity["id"], team_id, user["id"], "join_team", "pending", payload.get("reason"))
        self.create_notice(team["leaderId"], "新的入队申请", f"{user['nickname']} 申请加入队伍「{team['teamName']}」", "team_apply")

    def submit_team(self, user: dict[str, Any], team_id: int, payload: dict[str, Any]) -> None:
        team = self.team_by_id(team_id)
        if team is None:
            raise BusinessError("队伍不存在", 404, 404)
        if team["leaderId"] != user["id"]:
            raise BusinessError("只有队长可以提交报名", 403, 403)
        activity = self.activity_by_id(team["activityId"])
        if activity is None:
            raise BusinessError("活动不存在", 404, 404)
        if not self.signup_accepting(activity):
            raise BusinessError("当前活动不在报名开放时间内")
        count = self.approved_member_count(team_id)
        if count < activity["minTeamSize"] or count > activity["maxTeamSize"]:
            raise BusinessError("队伍人数未满足活动要求")
        if any(record["teamId"] == team_id and record["type"] == "signup_team" and record["status"] == "pending" for record in self.applications):
            raise BusinessError("当前队伍已有待审核报名", 409, 409)
        self.add_application(activity["id"], team_id, user["id"], "signup_team", "pending", payload.get("reason"))
        team["status"] = "submitted"
        self.create_notice(
            activity["organizerId"],
            "新的队伍报名待审核",
            f"队伍「{team['teamName']}」已提交活动「{activity['title']}」报名，请及时审核。",
            "review_result",
        )

    def assert_team_mutable(self, team: dict[str, Any]) -> None:
        if team["status"] in {"submitted", "approved"}:
            raise BusinessError("队伍已提交或已通过报名，不能再调整成员")
        if team["status"] == "disbanded":
            raise BusinessError("队伍已解散")

    def active_team_member(self, team_id: int, user_id: int) -> dict[str, Any] | None:
        return next(
            (
                item
                for item in self.team_members
                if item["teamId"] == team_id
                and item["userId"] == user_id
                and item["joinStatus"] in {"pending", "approved"}
            ),
            None,
        )

    def leave_team(self, user: dict[str, Any], team_id: int) -> None:
        team = self.team_by_id(team_id)
        if team is None:
            raise BusinessError("队伍不存在", 404, 404)
        self.assert_team_mutable(team)
        member = self.active_team_member(team_id, user["id"])
        if member is None:
            raise BusinessError("你不在该队伍中", 404, 404)
        if team["leaderId"] == user["id"]:
            approved_members = [
                item for item in self.team_members if item["teamId"] == team_id and item["joinStatus"] == "approved"
            ]
            if len(approved_members) > 1:
                raise BusinessError("队长需先转让队长或解散队伍")
            self.disband_team(user, team_id)
            return
        member["joinStatus"] = "left"
        member["joinedAt"] = None
        for record in self.applications:
            if record["teamId"] == team_id and record["applicantId"] == user["id"] and record["status"] == "pending":
                self.update_application(record, "rejected", user, "成员主动退出队伍")
        self.create_notice(
            team["leaderId"],
            "成员退出队伍",
            f"{user['nickname']} 已退出队伍「{team['teamName']}」。",
            "team_apply",
        )

    def remove_team_member(self, user: dict[str, Any], team_id: int, member_user_id: int) -> None:
        team = self.team_by_id(team_id)
        if team is None:
            raise BusinessError("队伍不存在", 404, 404)
        self.assert_team_mutable(team)
        if team["leaderId"] != user["id"]:
            raise BusinessError("只有队长可以移除成员", 403, 403)
        if member_user_id == team["leaderId"]:
            raise BusinessError("不能移除队长本人")
        member = self.active_team_member(team_id, member_user_id)
        if member is None:
            raise BusinessError("成员不存在或已不在队伍中", 404, 404)
        member["joinStatus"] = "removed"
        member["joinedAt"] = None
        for record in self.applications:
            if record["teamId"] == team_id and record["applicantId"] == member_user_id and record["status"] == "pending":
                self.update_application(record, "rejected", user, "队长移除成员")
        self.create_notice(
            member_user_id,
            "你已被移出队伍",
            f"队长已将你移出队伍「{team['teamName']}」。",
            "team_apply",
        )

    def transfer_leader(self, user: dict[str, Any], team_id: int, payload: dict[str, Any]) -> None:
        team = self.team_by_id(team_id)
        if team is None:
            raise BusinessError("队伍不存在", 404, 404)
        self.assert_team_mutable(team)
        if team["leaderId"] != user["id"]:
            raise BusinessError("只有队长可以转让队长", 403, 403)
        new_leader_id = _int(payload.get("newLeaderId"))
        if new_leader_id is None or new_leader_id == user["id"]:
            raise BusinessError("请选择新的队长")
        new_leader_member = next(
            (
                item
                for item in self.team_members
                if item["teamId"] == team_id
                and item["userId"] == new_leader_id
                and item["joinStatus"] == "approved"
            ),
            None,
        )
        if new_leader_member is None:
            raise BusinessError("新队长必须是已通过的队伍成员")
        old_leader_member = self.active_team_member(team_id, user["id"])
        if old_leader_member:
            old_leader_member["memberRole"] = "member"
        new_leader_member["memberRole"] = "leader"
        team["leaderId"] = new_leader_id
        new_leader = self.user_by_id(new_leader_id)
        self.create_notice(
            new_leader_id,
            "你已成为队长",
            f"你已成为队伍「{team['teamName']}」的新队长，请继续维护队伍报名。",
            "team_apply",
        )
        self.create_notice(
            user["id"],
            "队长已转让",
            f"队伍「{team['teamName']}」已转让给 {new_leader['nickname'] if new_leader else '新队长'}。",
            "team_apply",
        )

    def disband_team(self, user: dict[str, Any], team_id: int) -> None:
        team = self.team_by_id(team_id)
        if team is None:
            raise BusinessError("队伍不存在", 404, 404)
        self.assert_team_mutable(team)
        if user["role"] != "admin" and team["leaderId"] != user["id"]:
            raise BusinessError("只有队长或管理员可以解散队伍", 403, 403)
        team["status"] = "disbanded"
        affected_user_ids = []
        for member in self.team_members:
            if member["teamId"] == team_id and member["joinStatus"] in {"pending", "approved"}:
                affected_user_ids.append(member["userId"])
                member["joinStatus"] = "disbanded"
                member["joinedAt"] = None
        for record in self.applications:
            if record["teamId"] == team_id and record["status"] == "pending":
                self.update_application(record, "rejected", user, "队伍已解散")
        self.create_batch_notices(
            affected_user_ids,
            "队伍已解散",
            f"队伍「{team['teamName']}」已解散，相关报名或申请已终止。",
            "team_apply",
        )

    def review_item(self, record: dict[str, Any]) -> dict[str, Any]:
        activity = self.activity_by_id(record["activityId"])
        team = self.team_by_id(record.get("teamId"))
        applicant = self.user_by_id(record["applicantId"])
        return {
            "id": record["id"],
            "type": record["type"],
            "status": record["status"],
            "activityId": record["activityId"],
            "activityTitle": activity["title"] if activity else "未知活动",
            "teamId": record.get("teamId"),
            "teamName": team["teamName"] if team else "个人报名",
            "applicantId": record["applicantId"],
            "applicantName": applicant["nickname"] if applicant else "未知用户",
            "reason": record.get("reason"),
            "memberCount": self.approved_member_count(team["id"]) if team else 1,
            "reviewComment": record.get("reviewComment"),
            "createdAt": record["createdAt"],
        }

    def page_reviews(self, user: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        if user["role"] == "admin":
            activity_ids = {activity["id"] for activity in self.activities}
        else:
            activity_ids = {activity["id"] for activity in self.activities if activity["organizerId"] == user["id"]}
        status = str(params.get("status") or "").strip()
        keyword = str(params.get("keyword") or "").strip().lower()
        records = []
        for record in self.applications:
            if record["activityId"] not in activity_ids or record["type"] not in {"signup_team", "signup_personal"}:
                continue
            if status and record["status"] != status:
                continue
            if keyword and keyword not in str(record.get("reason") or "").lower():
                continue
            records.append(record)
        records.sort(key=lambda item: item["createdAt"], reverse=True)
        return _page([self.review_item(item) for item in records], params)

    def approve_review(self, user: dict[str, Any], review_id: int, comment: str | None, approve: bool) -> None:
        record = self.application_by_id(review_id)
        if record is None:
            raise BusinessError("审核记录不存在", 404, 404)
        if record["status"] != "pending":
            raise BusinessError("当前记录已审核，无需重复操作")
        if record["type"] == "join_team":
            self.review_join_team(user, record, comment, approve)
        elif record["type"] == "signup_team":
            self.review_signup_team(user, record, comment, approve)
        elif record["type"] == "signup_personal":
            self.review_signup_personal(user, record, comment, approve)
        else:
            raise BusinessError("不支持的审核类型")

    def update_application(self, record: dict[str, Any], status: str, user: dict[str, Any], comment: str | None) -> None:
        record["status"] = status
        record["reviewedBy"] = user["id"]
        record["reviewedAt"] = _iso(_now())
        record["reviewComment"] = comment

    def review_join_team(self, user: dict[str, Any], record: dict[str, Any], comment: str | None, approve: bool) -> None:
        team = self.team_by_id(record.get("teamId"))
        if team is None:
            raise BusinessError("队伍不存在", 404, 404)
        if team["leaderId"] != user["id"]:
            raise BusinessError("只有队长可以审核入队申请", 403, 403)
        activity = self.activity_by_id(team["activityId"])
        if activity is None:
            raise BusinessError("活动不存在", 404, 404)
        member = next((item for item in self.team_members if item["teamId"] == team["id"] and item["userId"] == record["applicantId"]), None)
        if member is None:
            raise BusinessError("入队申请成员记录不存在", 404, 404)
        if approve:
            if self.approved_member_count(team["id"]) >= activity["maxTeamSize"]:
                raise BusinessError("队伍人数已满，无法通过申请")
            for membership in self.team_members:
                if membership["teamId"] == team["id"] or membership["userId"] != record["applicantId"]:
                    continue
                if membership["joinStatus"] not in {"pending", "approved"}:
                    continue
                other = self.team_by_id(membership["teamId"])
                if other and other["activityId"] == activity["id"]:
                    raise BusinessError("申请人已在当前活动的其他队伍中")
            member["joinStatus"] = "approved"
            member["joinedAt"] = _iso(_now())
            self.update_application(record, "approved", user, comment)
            self.create_notice(record["applicantId"], "入队申请已通过", f"你申请加入的队伍「{team['teamName']}」已通过审核。", "review_result")
        else:
            member["joinStatus"] = "rejected"
            self.update_application(record, "rejected", user, comment)
            reason = comment or "未填写具体原因"
            self.create_notice(record["applicantId"], "入队申请未通过", f"你申请加入的队伍「{team['teamName']}」被拒绝，原因：{reason}", "review_result")

    def review_signup_team(self, user: dict[str, Any], record: dict[str, Any], comment: str | None, approve: bool) -> None:
        team = self.team_by_id(record.get("teamId"))
        activity = self.activity_by_id(record.get("activityId"))
        if team is None:
            raise BusinessError("队伍不存在", 404, 404)
        if activity is None:
            raise BusinessError("活动不存在", 404, 404)
        if user["role"] != "admin" and activity["organizerId"] != user["id"]:
            raise BusinessError("只有活动组织者或管理员可以审核报名", 403, 403)
        approved_members = [member for member in self.team_members if member["teamId"] == team["id"] and member["joinStatus"] == "approved"]
        if approve:
            if len(approved_members) < activity["minTeamSize"] or len(approved_members) > activity["maxTeamSize"]:
                raise BusinessError("队伍人数未满足活动要求")
            team["status"] = "approved"
            for member in approved_members:
                if self.sign_record(activity["id"], member["userId"]) is None:
                    self.add_sign_record(activity["id"], member["userId"], "unsigned")
            self.update_application(record, "approved", user, comment)
            self.create_batch_notices(
                [member["userId"] for member in approved_members],
                "活动报名审核通过",
                f"队伍「{team['teamName']}」已通过活动「{activity['title']}」审核，请按时参加。",
                "review_result",
            )
        else:
            team["status"] = "rejected"
            self.update_application(record, "rejected", user, comment)
            reason = comment or "未填写具体原因"
            self.create_batch_notices(
                [member["userId"] for member in approved_members],
                "活动报名未通过",
                f"队伍「{team['teamName']}」未通过活动「{activity['title']}」审核，原因：{reason}",
                "review_result",
            )

    def review_signup_personal(self, user: dict[str, Any], record: dict[str, Any], comment: str | None, approve: bool) -> None:
        activity = self.activity_by_id(record.get("activityId"))
        if activity is None:
            raise BusinessError("活动不存在", 404, 404)
        if user["role"] != "admin" and activity["organizerId"] != user["id"]:
            raise BusinessError("只有活动组织者或管理员可以审核报名", 403, 403)
        applicant = self.user_by_id(record["applicantId"])
        if applicant is None:
            raise BusinessError("申请人不存在", 404, 404)
        if approve:
            self.update_application(record, "approved", user, comment)
            if self.sign_record(activity["id"], applicant["id"]) is None:
                self.add_sign_record(activity["id"], applicant["id"], "unsigned")
            self.create_notice(
                applicant["id"],
                "活动报名审核通过",
                f"你已通过活动「{activity['title']}」报名审核，请按时参加。",
                "review_result",
            )
        else:
            self.update_application(record, "rejected", user, comment)
            reason = comment or "未填写具体原因"
            self.create_notice(
                applicant["id"],
                "活动报名未通过",
                f"你未通过活动「{activity['title']}」报名审核，原因：{reason}",
                "review_result",
            )

    def page_notices(self, user: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        is_read = _bool(params.get("isRead"), None)
        notice_type = str(params.get("type") or "").strip()
        records = []
        for notice in self.notifications:
            if notice["userId"] != user["id"]:
                continue
            if is_read is not None and notice["isRead"] != is_read:
                continue
            if notice_type and notice["type"] != notice_type:
                continue
            records.append(self.notification_vo(notice))
        records.sort(key=lambda item: item["createdAt"], reverse=True)
        return _page(records, params)

    def notification_vo(self, notice: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": notice["id"],
            "title": notice["title"],
            "content": notice["content"],
            "type": notice["type"],
            "isRead": notice["isRead"],
            "createdAt": notice["createdAt"],
        }

    def mark_read(self, user: dict[str, Any], ids: list[Any]) -> None:
        wanted = {_int(item) for item in ids}
        for notice in self.notifications:
            if notice["userId"] == user["id"] and notice["id"] in wanted:
                notice["isRead"] = True

    def mark_all_read(self, user: dict[str, Any]) -> None:
        for notice in self.notifications:
            if notice["userId"] == user["id"]:
                notice["isRead"] = True

    def unread_count(self, user: dict[str, Any]) -> int:
        return len([notice for notice in self.notifications if notice["userId"] == user["id"] and not notice["isRead"]])

    def create_notice(self, user_id: int, title: str, content: str, notice_type: str, is_read: bool = False) -> dict[str, Any]:
        notice = {
            "id": self.next_id("notifications"),
            "userId": user_id,
            "title": title,
            "content": content,
            "type": notice_type,
            "isRead": is_read,
            "createdAt": _iso(_now()),
        }
        self.notifications.append(notice)
        return notice

    def create_batch_notices(self, user_ids: list[int], title: str, content: str, notice_type: str) -> None:
        for user_id in sorted(set(user_ids)):
            self.create_notice(user_id, title, content, notice_type)

    def activity_participant_ids(self, activity_id: int, include_pending: bool = False) -> list[int]:
        statuses = {"approved", "signed"}
        if include_pending:
            statuses.add("pending")
        user_ids = {
            record["userId"]
            for record in self.sign_records
            if record["activityId"] == activity_id
        }
        for record in self.applications:
            if record["activityId"] != activity_id or record["status"] not in statuses:
                continue
            if record["type"] == "signup_personal":
                user_ids.add(record["applicantId"])
            elif include_pending and record.get("teamId") is not None:
                for member in self.team_members:
                    if member["teamId"] == record["teamId"] and member["joinStatus"] in {"pending", "approved"}:
                        user_ids.add(member["userId"])
        for team in self.teams:
            if team["activityId"] != activity_id:
                continue
            if team["status"] == "approved" or (include_pending and team["status"] in {"forming", "submitted"}):
                for member in self.team_members:
                    if member["teamId"] == team["id"] and member["joinStatus"] in {"pending", "approved"}:
                        user_ids.add(member["userId"])
        return sorted(user_ids)

    def overview(self, user: dict[str, Any]) -> dict[str, Any]:
        role = user["role"]
        if role == "organizer":
            activity_scope = [activity for activity in self.activities if activity["organizerId"] == user["id"]]
        else:
            activity_scope = [activity for activity in self.activities if activity["status"] != "draft"]
        activity_ids = {activity["id"] for activity in activity_scope}
        if role in {"student", "captain"}:
            team_count = len([member for member in self.team_members if member["userId"] == user["id"]])
            pending_count = len([record for record in self.applications if record["applicantId"] == user["id"] and record["status"] == "pending"])
            signed_count = len([record for record in self.sign_records if record["userId"] == user["id"] and record["status"] == "signed"])
            feedbacks = [feedback for feedback in self.feedbacks if feedback["userId"] == user["id"]]
        else:
            team_count = len([team for team in self.teams if team["activityId"] in activity_ids])
            pending_count = len([record for record in self.applications if record["activityId"] in activity_ids and record["status"] == "pending"])
            signed_count = len([record for record in self.sign_records if record["activityId"] in activity_ids and record["status"] == "signed"])
            feedbacks = [feedback for feedback in self.feedbacks if feedback["activityId"] in activity_ids]
        average = sum(item["score"] for item in feedbacks) / len(feedbacks) if feedbacks else 0
        distribution: defaultdict[str, int] = defaultdict(int)
        for activity in activity_scope:
            distribution[activity["type"]] += 1
        upcoming = [
            activity
            for activity in activity_scope
            if (_dt(activity["startTime"]) or _now()) >= _now() - timedelta(days=1)
        ]
        upcoming.sort(key=lambda item: item["startTime"])
        return {
            "role": role,
            "activityCount": len(activity_scope),
            "teamCount": team_count,
            "pendingCount": pending_count,
            "unreadCount": self.unread_count(user),
            "signedCount": signed_count,
            "feedbackAverage": average,
            "activityTypeDistribution": [
                {"name": name, "value": value} for name, value in sorted(distribution.items(), key=lambda item: item[1], reverse=True)
            ],
            "upcomingActivities": [self.activity_card(activity) for activity in upcoming[:5]],
        }

    def sign_status(self, user: dict[str, Any], activity_id: int) -> dict[str, Any]:
        activity = self.activity_by_id(activity_id)
        if activity is None:
            raise BusinessError("活动不存在", 404, 404)
        record = self.sign_record(activity_id, user["id"])
        return {
            "activityId": activity_id,
            "activityTitle": activity["title"],
            "status": record["status"] if record else "unsigned",
            "eligible": self.is_eligible(user["id"], activity),
            "signWindowOpen": self.is_sign_window_open(activity),
            "signTime": record.get("signTime") if record else None,
        }

    def is_eligible(self, user_id: int, activity: dict[str, Any]) -> bool:
        if not activity["requireTeam"]:
            if self.sign_record(activity["id"], user_id) is not None:
                return True
            record = self.personal_signup_record(activity["id"], user_id)
            return bool(record and record["status"] == "approved")
        for member in self.team_members:
            if member["userId"] != user_id or member["joinStatus"] != "approved":
                continue
            team = self.team_by_id(member["teamId"])
            if team and team["activityId"] == activity["id"] and team["status"] == "approved":
                return True
        return False

    def is_sign_window_open(self, activity: dict[str, Any]) -> bool:
        now = _now()
        start = _dt(activity.get("signStartTime")) or ((_dt(activity["startTime"]) or now) - timedelta(hours=1))
        end = _dt(activity.get("signEndTime")) or (_dt(activity["endTime"]) or now)
        return start <= now <= end

    def check_in(self, user: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        activity_id = _int(payload.get("activityId"))
        activity = self.activity_by_id(activity_id)
        if activity is None:
            raise BusinessError("活动不存在", 404, 404)
        if not self.is_eligible(user["id"], activity):
            raise BusinessError("仅审核通过的参与者可签到")
        if not self.is_sign_window_open(activity):
            raise BusinessError("当前不在签到时间范围内")
        if str(activity.get("signCode") or "").lower() != str(payload.get("signCode") or "").lower():
            raise BusinessError("签到码不正确")
        record = self.sign_record(activity["id"], user["id"])
        if record is None:
            record = self.add_sign_record(activity["id"], user["id"], "unsigned")
        if record["status"] == "signed":
            raise BusinessError("请勿重复签到", 409, 409)
        record["status"] = "signed"
        record["signType"] = "code"
        record["signTime"] = _iso(_now())
        return {"signTime": record["signTime"]}

    def submit_feedback(self, user: dict[str, Any], payload: dict[str, Any]) -> None:
        activity_id = _int(payload.get("activityId"))
        activity = self.activity_by_id(activity_id)
        if activity is None:
            raise BusinessError("活动不存在", 404, 404)
        if _now() < (_dt(activity["endTime"]) or _now()):
            raise BusinessError("活动结束后才能提交反馈")
        record = self.sign_record(activity["id"], user["id"])
        if record is None or record["status"] != "signed":
            raise BusinessError("仅已签到参与者可提交反馈")
        if any(item["activityId"] == activity["id"] and item["userId"] == user["id"] for item in self.feedbacks):
            raise BusinessError("你已提交过本次活动反馈", 409, 409)
        score = _int(payload.get("score"))
        if score is None or score < 1 or score > 5:
            raise BusinessError("评分必须在 1 到 5 之间")
        self.feedbacks.append(
            {
                "id": self.next_id("feedbacks"),
                "activityId": activity["id"],
                "userId": user["id"],
                "score": score,
                "content": payload.get("content"),
                "tags": _tags(payload.get("tags")),
                "willingRejoin": _bool(payload.get("willingRejoin"), None),
                "createdAt": _iso(_now()),
            }
        )

    def feedback_by_activity(self, activity_id: int) -> dict[str, Any]:
        if self.activity_by_id(activity_id) is None:
            raise BusinessError("活动不存在", 404, 404)
        records = [item for item in self.feedbacks if item["activityId"] == activity_id]
        records.sort(key=lambda item: item["createdAt"], reverse=True)
        average = sum(item["score"] for item in records) / len(records) if records else 0
        return {
            "averageScore": average,
            "total": len(records),
            "records": [self.feedback_item(item) for item in records],
        }

    def feedback_item(self, feedback: dict[str, Any]) -> dict[str, Any]:
        user = self.user_by_id(feedback["userId"])
        return {
            "userId": feedback["userId"],
            "nickname": user["nickname"] if user else "匿名用户",
            "score": feedback["score"],
            "content": feedback.get("content"),
            "tags": list(feedback.get("tags") or []),
            "willingRejoin": feedback.get("willingRejoin"),
            "createdAt": feedback["createdAt"],
        }

    def announcements_all(self) -> list[dict[str, Any]]:
        records = [self.announcement_vo(item) for item in self.announcements]
        records.sort(key=lambda item: item["createdAt"], reverse=True)
        return records

    def announcement_vo(self, announcement: dict[str, Any]) -> dict[str, Any]:
        creator = self.user_by_id(announcement["createdBy"])
        return {
            "id": announcement["id"],
            "title": announcement["title"],
            "content": announcement["content"],
            "createdBy": announcement["createdBy"],
            "creatorName": creator["nickname"] if creator else "未知用户",
            "createdAt": announcement["createdAt"],
        }

    def create_announcement(self, user: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        if user["role"] != "admin":
            raise BusinessError("仅管理员可发布公告", 403, 403)
        title = str(payload.get("title") or "").strip()
        content = str(payload.get("content") or "").strip()
        if not title or not content:
            raise BusinessError("公告标题和内容不能为空")
        announcement = {
            "id": self.next_id("announcements"),
            "title": title,
            "content": content,
            "createdBy": user["id"],
            "createdAt": _iso(_now()),
        }
        self.announcements.append(announcement)
        self.create_batch_notices([item["id"] for item in self.users], "新公告发布", title, "announcement")
        return self.announcement_vo(announcement)


class CampusFlowHTTPServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], handler_class: type[BaseHTTPRequestHandler]):
        super().__init__(server_address, handler_class)
        self.store = CampusFlowStore()


class CampusFlowHandler(BaseHTTPRequestHandler):
    server: CampusFlowHTTPServer

    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        self.handle_json("GET")

    def do_POST(self) -> None:
        self.handle_json("POST")

    def do_PUT(self) -> None:
        self.handle_json("PUT")

    def send_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type, X-Access-Token, X-Demo-Username, X-Demo-User-Id")
        self.send_header("Access-Control-Max-Age", "86400")

    def send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self) -> dict[str, Any]:
        length = _int(self.headers.get("Content-Length"), 0) or 0
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        if not raw.strip():
            return {}
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise BusinessError(f"请求体 JSON 格式错误：{exc.msg}") from exc
        if not isinstance(data, dict):
            raise BusinessError("请求体必须是 JSON 对象")
        return data

    def current_user(self, required: bool = False) -> dict[str, Any] | None:
        query = parse_qs(urlparse(self.path).query)
        candidates = [
            _normalize_token(self.headers.get("Authorization")),
            _normalize_token(self.headers.get("X-Access-Token")),
            _normalize_token((query.get("access_token") or query.get("token") or [None])[-1]),
        ]
        for token in candidates:
            user = self.server.store.user_from_token(token)
            if user is not None:
                return user
        demo_username = str(self.headers.get("X-Demo-Username") or "").strip()
        if demo_username:
            user = self.server.store.user_by_username(demo_username)
            if user is not None:
                return user
        demo_user_id = _int(self.headers.get("X-Demo-User-Id"))
        if demo_user_id is not None:
            user = self.server.store.user_by_id(demo_user_id)
            if user is not None:
                return user
        if required:
            raise BusinessError("请先登录", 401, 401)
        return None

    def handle_json(self, method: str) -> None:
        parsed = urlparse(self.path)
        params = {key: values[-1] for key, values in parse_qs(parsed.query).items()}
        try:
            if method == "GET" and (parsed.path.rstrip("/") or "/") == "/ws/info":
                self.send_json(
                    {
                        "websocket": False,
                        "origins": ["*:*"],
                        "cookie_needed": False,
                        "entropy": random.randint(0, 2_147_483_647),
                    }
                )
                return
            body = self.read_json() if method in {"POST", "PUT"} else {}
            with self.server.store.lock:
                message, data = self.dispatch(method, parsed.path.rstrip("/") or "/", params, body)
            self.send_json({"code": 200, "message": message, "data": data})
        except BusinessError as exc:
            self.send_json({"code": exc.code, "message": str(exc), "data": None}, exc.http_status)
        except Exception as exc:
            self.send_json({"code": 500, "message": str(exc), "data": None}, 500)

    def dispatch(
        self,
        method: str,
        path: str,
        params: dict[str, Any],
        body: dict[str, Any],
    ) -> tuple[str, Any]:
        store = self.server.store

        if method == "GET" and path in {"/", "/api/health"}:
            return "CampusFlow Python backend is running", {
                "name": "CampusFlow Python Backend",
                "status": "ok",
                "time": _iso(_now()),
            }

        if method == "POST" and path == "/api/auth/login":
            return "登录成功", store.login(body)

        if method == "GET" and path == "/api/user/profile":
            return "查询成功", store.user_profile(self.current_user(required=True))

        if method == "PUT" and path == "/api/user/profile":
            return "更新成功", store.update_profile(self.current_user(required=True), body)

        if method == "GET" and path == "/api/dashboard/overview":
            return "查询成功", store.overview(self.current_user(required=True))

        if method == "GET" and path == "/api/activities":
            return "查询成功", store.page_activities(params)

        if method == "GET" and path == "/api/activities/mine":
            return "查询成功", store.my_activities(self.current_user(required=True))

        if method == "POST" and path == "/api/activities":
            return "创建成功", store.save_activity(self.current_user(required=True), body)

        activity_match = re.fullmatch(r"/api/activities/(\d+)", path)
        if activity_match and method == "GET":
            return "查询成功", store.activity_detail(int(activity_match.group(1)), self.current_user(required=False))
        if activity_match and method == "PUT":
            return "更新成功", store.save_activity(self.current_user(required=True), body, int(activity_match.group(1)))

        activity_signup_match = re.fullmatch(r"/api/activities/(\d+)/signup", path)
        if activity_signup_match and method == "POST":
            return "报名已提交", store.signup_activity(self.current_user(required=True), int(activity_signup_match.group(1)), body)

        activity_status_match = re.fullmatch(r"/api/activities/(\d+)/status", path)
        if activity_status_match and method == "POST":
            return "状态已更新", store.update_activity_status(self.current_user(required=True), int(activity_status_match.group(1)), body)

        if method == "POST" and path == "/api/teams":
            return "创建成功", store.create_team(self.current_user(required=True), body)

        if method == "GET" and path == "/api/teams/joinable":
            return "查询成功", store.joinable_teams(self.current_user(required=False), params)

        team_match = re.fullmatch(r"/api/teams/(\d+)", path)
        if team_match and method == "GET":
            return "查询成功", store.team_detail(int(team_match.group(1)), self.current_user(required=False))

        team_apply_match = re.fullmatch(r"/api/teams/(\d+)/apply", path)
        if team_apply_match and method == "POST":
            store.apply_to_team(self.current_user(required=True), int(team_apply_match.group(1)), body)
            return "申请已提交", None

        team_submit_match = re.fullmatch(r"/api/teams/(\d+)/submit", path)
        if team_submit_match and method == "POST":
            store.submit_team(self.current_user(required=True), int(team_submit_match.group(1)), body)
            return "报名已提交", None

        team_leave_match = re.fullmatch(r"/api/teams/(\d+)/leave", path)
        if team_leave_match and method == "POST":
            store.leave_team(self.current_user(required=True), int(team_leave_match.group(1)))
            return "已退出队伍", None

        team_disband_match = re.fullmatch(r"/api/teams/(\d+)/disband", path)
        if team_disband_match and method == "POST":
            store.disband_team(self.current_user(required=True), int(team_disband_match.group(1)))
            return "队伍已解散", None

        team_transfer_match = re.fullmatch(r"/api/teams/(\d+)/transfer", path)
        if team_transfer_match and method == "POST":
            store.transfer_leader(self.current_user(required=True), int(team_transfer_match.group(1)), body)
            return "队长已转让", None

        team_remove_match = re.fullmatch(r"/api/teams/(\d+)/members/(\d+)/remove", path)
        if team_remove_match and method == "POST":
            store.remove_team_member(
                self.current_user(required=True),
                int(team_remove_match.group(1)),
                int(team_remove_match.group(2)),
            )
            return "成员已移除", None

        if method == "GET" and path == "/api/reviews":
            return "查询成功", store.page_reviews(self.current_user(required=True), params)

        review_match = re.fullmatch(r"/api/reviews/(\d+)/(approve|reject)", path)
        if review_match and method == "POST":
            approve = review_match.group(2) == "approve"
            store.approve_review(self.current_user(required=True), int(review_match.group(1)), body.get("comment"), approve)
            return ("审核通过" if approve else "审核驳回"), None

        if method == "GET" and path == "/api/notices":
            return "查询成功", store.page_notices(self.current_user(required=True), params)

        if method == "POST" and path == "/api/notices/read":
            store.mark_read(self.current_user(required=True), body.get("ids") or [])
            return "操作成功", None

        if method == "POST" and path == "/api/notices/read-all":
            store.mark_all_read(self.current_user(required=True))
            return "操作成功", None

        if method == "GET" and path == "/api/notices/unread-count":
            return "查询成功", {"count": store.unread_count(self.current_user(required=True))}

        sign_status_match = re.fullmatch(r"/api/sign/status/(\d+)", path)
        if sign_status_match and method == "GET":
            return "查询成功", store.sign_status(self.current_user(required=True), int(sign_status_match.group(1)))

        if method == "POST" and path == "/api/sign/check-in":
            return "签到成功", store.check_in(self.current_user(required=True), body)

        if method == "POST" and path == "/api/feedback":
            store.submit_feedback(self.current_user(required=True), body)
            return "反馈提交成功", None

        feedback_match = re.fullmatch(r"/api/feedback/activity/(\d+)", path)
        if feedback_match and method == "GET":
            return "查询成功", store.feedback_by_activity(int(feedback_match.group(1)))

        if method == "GET" and path == "/api/announcements":
            return "查询成功", store.announcements_all()

        if method == "POST" and path == "/api/announcements":
            return "发布成功", store.create_announcement(self.current_user(required=True), body)

        raise BusinessError("接口不存在", 404, 404)


def run(host: str | None = None, port: int | None = None) -> None:
    host = host or os.environ.get("CAMPUSFLOW_HOST", "0.0.0.0")
    port = port or int(os.environ.get("CAMPUSFLOW_PORT", "8080"))
    server = CampusFlowHTTPServer((host, port), CampusFlowHandler)
    print(f"CampusFlow Python backend is running at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down CampusFlow Python backend.")
    finally:
        server.server_close()
