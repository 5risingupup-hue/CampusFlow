from __future__ import annotations

import base64
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
        self.add_member(submitted["id"], student01["id"], "member", "approved", now - timedelta(hours=20))
        self.add_member(submitted["id"], student02["id"], "member", "approved", now - timedelta(hours=18))
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
        team = {
            "id": self.next_id("teams"),
            "activityId": activity_id,
            "teamName": team_name,
            "leaderId": leader_id,
            "slogan": slogan,
            "description": description,
            "inviteCode": f"CF-DEMO-{leader_id}",
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
        if not token or not token.startswith("demo."):
            return None
        try:
            raw = token.removeprefix("demo.")
            raw += "=" * (-len(raw) % 4)
            payload = json.loads(base64.urlsafe_b64decode(raw.encode()).decode())
            return self.user_by_id(_int(payload.get("id")))
        except Exception:
            return None

    def user_by_id(self, user_id: int | None) -> dict[str, Any] | None:
        return next((user for user in self.users if user["id"] == user_id), None)

    def activity_by_id(self, activity_id: int | None) -> dict[str, Any] | None:
        return next((activity for activity in self.activities if activity["id"] == activity_id), None)

    def team_by_id(self, team_id: int | None) -> dict[str, Any] | None:
        return next((team for team in self.teams if team["id"] == team_id), None)

    def application_by_id(self, application_id: int | None) -> dict[str, Any] | None:
        return next((record for record in self.applications if record["id"] == application_id), None)

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
        can_create_team = bool(activity["requireTeam"])
        can_apply_team = bool(activity["requireTeam"])
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
            sign_record = self.sign_record(activity_id, user["id"])
            can_sign_in = sign_record is not None or my_team_id is not None or not activity["requireTeam"]
            can_feedback = bool(sign_record and sign_record["status"] == "signed")
            if any(item["activityId"] == activity_id and item["userId"] == user["id"] for item in self.feedbacks):
                can_feedback = False
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
        if _now() > (_dt(activity["signupDeadline"]) or _now()):
            raise BusinessError("活动报名已截止")
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
            if user:
                applied = any(
                    record["teamId"] == team["id"]
                    and record["applicantId"] == user["id"]
                    and record["type"] == "join_team"
                    and record["status"] == "pending"
                    for record in self.applications
                )
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
                    "currentSize": self.approved_member_count(team["id"]),
                    "maxTeamSize": activity["maxTeamSize"],
                    "status": team["status"],
                    "applied": applied,
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
        if _now() > (_dt(activity["signupDeadline"]) or _now()):
            raise BusinessError("活动报名已截止")
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
        if _now() > (_dt(activity["signupDeadline"]) or _now()):
            raise BusinessError("活动报名已截止")
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
            "teamName": team["teamName"] if team else "-",
            "applicantId": record["applicantId"],
            "applicantName": applicant["nickname"] if applicant else "未知用户",
            "reason": record.get("reason"),
            "memberCount": self.approved_member_count(team["id"]) if team else 0,
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
            if record["activityId"] not in activity_ids or record["type"] != "signup_team":
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
        else:
            self.review_signup_team(user, record, comment, approve)

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
            return True
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
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
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
        auth = self.headers.get("Authorization", "")
        token = auth.split(" ", 1)[1] if auth.lower().startswith("bearer ") else None
        user = self.server.store.user_from_token(token)
        if required and user is None:
            raise BusinessError("请先登录", 401, 401)
        return user

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
