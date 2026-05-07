package com.campusflow.config;

import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.campusflow.domain.entity.Activity;
import com.campusflow.domain.entity.Announcement;
import com.campusflow.domain.entity.ApplicationRecord;
import com.campusflow.domain.entity.Feedback;
import com.campusflow.domain.entity.Notification;
import com.campusflow.domain.entity.Role;
import com.campusflow.domain.entity.SignRecord;
import com.campusflow.domain.entity.Team;
import com.campusflow.domain.entity.TeamMember;
import com.campusflow.domain.entity.User;
import com.campusflow.domain.enums.ActivityStatus;
import com.campusflow.domain.enums.ApplicationType;
import com.campusflow.domain.enums.NotificationType;
import com.campusflow.domain.enums.ReviewStatus;
import com.campusflow.domain.enums.SignStatus;
import com.campusflow.domain.enums.SignType;
import com.campusflow.domain.enums.TeamStatus;
import com.campusflow.mapper.ActivityMapper;
import com.campusflow.mapper.AnnouncementMapper;
import com.campusflow.mapper.ApplicationRecordMapper;
import com.campusflow.mapper.FeedbackMapper;
import com.campusflow.mapper.NotificationMapper;
import com.campusflow.mapper.RoleMapper;
import com.campusflow.mapper.SignRecordMapper;
import com.campusflow.mapper.TeamMapper;
import com.campusflow.mapper.TeamMemberMapper;
import com.campusflow.mapper.UserMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.time.LocalDateTime;
import java.util.Map;

@Configuration
@RequiredArgsConstructor
public class DataInitializer {

    private final RoleMapper roleMapper;
    private final UserMapper userMapper;
    private final ActivityMapper activityMapper;
    private final TeamMapper teamMapper;
    private final TeamMemberMapper teamMemberMapper;
    private final ApplicationRecordMapper applicationRecordMapper;
    private final NotificationMapper notificationMapper;
    private final SignRecordMapper signRecordMapper;
    private final FeedbackMapper feedbackMapper;
    private final AnnouncementMapper announcementMapper;
    private final PasswordEncoder passwordEncoder;

    @Bean
    public CommandLineRunner seedDemoData() {
        return args -> {
            seedRoles();
            seedUsers();
            seedActivitiesAndFlows();
        };
    }

    private void seedRoles() {
        if (roleMapper.selectCount(Wrappers.<Role>lambdaQuery()) > 0) {
            return;
        }
        insertRole("student", "普通学生用户");
        insertRole("organizer", "活动组织者");
        insertRole("admin", "系统管理员");
    }

    private void seedUsers() {
        if (userMapper.selectCount(Wrappers.<User>lambdaQuery()) > 0) {
            return;
        }
        Map<String, Long> roleIds = roleMapper.selectList(Wrappers.<Role>lambdaQuery())
            .stream()
            .collect(java.util.stream.Collectors.toMap(Role::getRoleName, Role::getId));
        insertUser("student01", "Alice", "alice@campusflow.local", roleIds.get("student"));
        insertUser("student02", "Brian", "brian@campusflow.local", roleIds.get("student"));
        insertUser("student03", "Clara", "clara@campusflow.local", roleIds.get("student"));
        insertUser("student04", "Bob", "bob@campusflow.local", roleIds.get("student"));
        insertUser("student05", "Eva", "eva@campusflow.local", roleIds.get("student"));
        insertUser("student06", "Frank", "frank@campusflow.local", roleIds.get("student"));
        insertUser("student07", "Grace", "grace@campusflow.local", roleIds.get("student"));
        insertUser("student08", "Henry", "henry@campusflow.local", roleIds.get("student"));
        insertUser("organizer01", "Cindy", "cindy@campusflow.local", roleIds.get("organizer"));
        insertUser("admin01", "David", "david@campusflow.local", roleIds.get("admin"));
    }

    private void seedActivitiesAndFlows() {
        if (activityMapper.selectCount(Wrappers.<Activity>lambdaQuery()) > 0) {
            return;
        }
        User organizer = findUser("organizer01");
        User studentLeader = findUser("student04");
        User student01 = findUser("student01");
        User student02 = findUser("student02");
        User student03 = findUser("student03");
        User admin = findUser("admin01");

        Activity innovation = insertActivity(
            "校园创新挑战赛",
            "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1200&q=80",
            "面向全校学生的跨学科创新协作活动，聚焦校园服务、可持续发展与数字化场景。",
            organizer.getId(),
            "创新竞赛",
            "图书馆报告厅",
            LocalDateTime.now().plusDays(7),
            LocalDateTime.now().plusDays(7).plusHours(4),
            LocalDateTime.now().plusDays(3),
            true,
            3,
            5,
            ActivityStatus.SIGNUP_OPEN.getCode(),
            "创新,协作,路演",
            "SIGN2026",
            LocalDateTime.now().plusDays(7).minusHours(1),
            LocalDateTime.now().plusDays(7).plusHours(1),
            null
        );

        Activity workshop = insertActivity(
            "志愿服务培训营",
            "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?auto=format&fit=crop&w=1200&q=80",
            "面向志愿者的服务流程培训与现场协同演练，帮助同学熟悉大型活动服务规范。",
            organizer.getId(),
            "志愿服务",
            "学生活动中心 201",
            LocalDateTime.now().minusDays(5),
            LocalDateTime.now().minusDays(5).plusHours(3),
            LocalDateTime.now().minusDays(8),
            false,
            1,
            1,
            ActivityStatus.FINISHED.getCode(),
            "培训,志愿,服务",
            "SERVICE26",
            LocalDateTime.now().minusDays(5).minusHours(1),
            LocalDateTime.now().minusDays(5).plusHours(2),
            "培训营顺利完成，共有 86 名同学完成现场签到，反馈平均分 4.8。"
        );

        Activity hackNight = insertActivity(
            "AI Hack Night",
            "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1200&q=80",
            "围绕校园应用场景开展一晚上的 AI 原型共创，强调快速协作与创意实现。",
            organizer.getId(),
            "技术沙龙",
            "信息楼 A301",
            LocalDateTime.now().plusDays(14),
            LocalDateTime.now().plusDays(14).plusHours(6),
            LocalDateTime.now().plusDays(10),
            true,
            2,
            4,
            ActivityStatus.SIGNUP_OPEN.getCode(),
            "AI,原型,黑客松",
            "HACK2026",
            LocalDateTime.now().plusDays(14).minusHours(1),
            LocalDateTime.now().plusDays(14).plusHours(2),
            null
        );

        Team submittedTeam = insertTeam(innovation.getId(), "Campus Masters", studentLeader.getId(), "协作赢未来", "专注创新方案与执行落地", TeamStatus.SUBMITTED.getCode());
        insertMember(submittedTeam.getId(), studentLeader.getId(), "leader", ReviewStatus.APPROVED.getCode(), LocalDateTime.now().minusDays(1));
        insertMember(submittedTeam.getId(), student01.getId(), "member", ReviewStatus.APPROVED.getCode(), LocalDateTime.now().minusHours(20));
        insertMember(submittedTeam.getId(), student02.getId(), "member", ReviewStatus.APPROVED.getCode(), LocalDateTime.now().minusHours(18));
        insertApplication(innovation.getId(), submittedTeam.getId(), studentLeader.getId(), ApplicationType.SIGNUP_TEAM.getCode(), ReviewStatus.PENDING.getCode(), "我们已完成队伍组建，希望参加创新挑战赛。");

        Team formingTeam = insertTeam(hackNight.getId(), "Idea Spark", student02.getId(), "今晚就把想法做出来", "欢迎擅长产品、前端和算法的同学加入", TeamStatus.FORMING.getCode());
        insertMember(formingTeam.getId(), student02.getId(), "leader", ReviewStatus.APPROVED.getCode(), LocalDateTime.now().minusHours(10));
        insertMember(formingTeam.getId(), student03.getId(), "member", ReviewStatus.PENDING.getCode(), null);
        insertApplication(hackNight.getId(), formingTeam.getId(), student03.getId(), ApplicationType.JOIN_TEAM.getCode(), ReviewStatus.PENDING.getCode(), "我擅长前端原型和交互实现，希望一起参加。");

        insertNotification(studentLeader.getId(), "报名已提交", "队伍 Campus Masters 已提交创新挑战赛报名，请等待组织者审核。", NotificationType.REVIEW_RESULT.getCode(), false);
        insertNotification(student03.getId(), "入队申请已发送", "你对队伍 Idea Spark 的申请已提交，请等待队长审核。", NotificationType.TEAM_APPLY.getCode(), false);
        insertNotification(admin.getId(), "系统巡检提醒", "当前演示环境已初始化，可使用管理员账号发布公告。", NotificationType.SYSTEM.getCode(), true);

        SignRecord signRecord = new SignRecord();
        signRecord.setActivityId(workshop.getId());
        signRecord.setUserId(student01.getId());
        signRecord.setSignType(SignType.CODE.getCode());
        signRecord.setSignTime(LocalDateTime.now().minusDays(5).minusMinutes(5));
        signRecord.setStatus(SignStatus.SIGNED.getCode());
        signRecordMapper.insert(signRecord);

        Feedback feedback = new Feedback();
        feedback.setActivityId(workshop.getId());
        feedback.setUserId(student01.getId());
        feedback.setScore(5);
        feedback.setContent("培训流程很清晰，组织非常有序，签到和通知都很及时。");
        feedback.setTags("流程清晰,通知及时,组织有序");
        feedback.setWillingRejoin(true);
        feedbackMapper.insert(feedback);

        Announcement announcement = new Announcement();
        announcement.setTitle("CampusFlow 演示环境已就绪");
        announcement.setContent("你可以使用示例账号体验活动浏览、组队报名、审核、通知、签到和反馈的完整流程。");
        announcement.setCreatedBy(admin.getId());
        announcementMapper.insert(announcement);
    }

    private void insertRole(String roleName, String roleDesc) {
        Role role = new Role();
        role.setRoleName(roleName);
        role.setRoleDesc(roleDesc);
        roleMapper.insert(role);
    }

    private void insertUser(String username, String nickname, String email, Long roleId) {
        User user = new User();
        user.setUsername(username);
        user.setPassword(passwordEncoder.encode("123456"));
        user.setNickname(nickname);
        user.setEmail(email);
        user.setAvatar("https://api.dicebear.com/7.x/initials/svg?seed=" + nickname);
        user.setRoleId(roleId);
        user.setStatus(1);
        userMapper.insert(user);
    }

    private Activity insertActivity(
        String title,
        String coverUrl,
        String description,
        Long organizerId,
        String type,
        String location,
        LocalDateTime startTime,
        LocalDateTime endTime,
        LocalDateTime signupDeadline,
        boolean requireTeam,
        int minTeamSize,
        int maxTeamSize,
        String status,
        String tags,
        String signCode,
        LocalDateTime signStartTime,
        LocalDateTime signEndTime,
        String resultSummary
    ) {
        Activity activity = new Activity();
        activity.setTitle(title);
        activity.setCoverUrl(coverUrl);
        activity.setDescription(description);
        activity.setOrganizerId(organizerId);
        activity.setType(type);
        activity.setLocation(location);
        activity.setStartTime(startTime);
        activity.setEndTime(endTime);
        activity.setSignupDeadline(signupDeadline);
        activity.setRequireTeam(requireTeam);
        activity.setMinTeamSize(minTeamSize);
        activity.setMaxTeamSize(maxTeamSize);
        activity.setStatus(status);
        activity.setTags(tags);
        activity.setSignCode(signCode);
        activity.setSignStartTime(signStartTime);
        activity.setSignEndTime(signEndTime);
        activity.setResultSummary(resultSummary);
        activityMapper.insert(activity);
        return activity;
    }

    private Team insertTeam(Long activityId, String teamName, Long leaderId, String slogan, String description, String status) {
        Team team = new Team();
        team.setActivityId(activityId);
        team.setTeamName(teamName);
        team.setLeaderId(leaderId);
        team.setSlogan(slogan);
        team.setDescription(description);
        team.setInviteCode("CF-DEMO-" + leaderId);
        team.setStatus(status);
        teamMapper.insert(team);
        return team;
    }

    private void insertMember(Long teamId, Long userId, String memberRole, String joinStatus, LocalDateTime joinedAt) {
        TeamMember teamMember = new TeamMember();
        teamMember.setTeamId(teamId);
        teamMember.setUserId(userId);
        teamMember.setMemberRole(memberRole);
        teamMember.setJoinStatus(joinStatus);
        teamMember.setJoinedAt(joinedAt);
        teamMemberMapper.insert(teamMember);
    }

    private void insertApplication(Long activityId, Long teamId, Long applicantId, String type, String status, String reason) {
        ApplicationRecord record = new ApplicationRecord();
        record.setActivityId(activityId);
        record.setTeamId(teamId);
        record.setApplicantId(applicantId);
        record.setType(type);
        record.setStatus(status);
        record.setReason(reason);
        applicationRecordMapper.insert(record);
    }

    private void insertNotification(Long userId, String title, String content, String type, boolean isRead) {
        Notification notification = new Notification();
        notification.setUserId(userId);
        notification.setTitle(title);
        notification.setContent(content);
        notification.setType(type);
        notification.setRead(isRead);
        notificationMapper.insert(notification);
    }

    private User findUser(String username) {
        return userMapper.selectOne(Wrappers.<User>lambdaQuery()
            .eq(User::getUsername, username)
            .last("limit 1"));
    }
}
