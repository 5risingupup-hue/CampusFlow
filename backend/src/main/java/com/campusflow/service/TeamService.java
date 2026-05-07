package com.campusflow.service;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.campusflow.common.PageResult;
import com.campusflow.domain.dto.CreateTeamRequest;
import com.campusflow.domain.dto.SubmitTeamRequest;
import com.campusflow.domain.dto.TeamQueryRequest;
import com.campusflow.domain.entity.Activity;
import com.campusflow.domain.entity.ApplicationRecord;
import com.campusflow.domain.entity.Team;
import com.campusflow.domain.entity.TeamMember;
import com.campusflow.domain.entity.User;
import com.campusflow.domain.enums.ApplicationType;
import com.campusflow.domain.enums.NotificationType;
import com.campusflow.domain.enums.ReviewStatus;
import com.campusflow.domain.enums.TeamStatus;
import com.campusflow.domain.vo.ApplicationRecordVO;
import com.campusflow.domain.vo.CreateTeamResponse;
import com.campusflow.domain.vo.TeamDetailVO;
import com.campusflow.domain.vo.TeamListItemVO;
import com.campusflow.domain.vo.TeamMemberVO;
import com.campusflow.exception.BusinessException;
import com.campusflow.mapper.ActivityMapper;
import com.campusflow.mapper.ApplicationRecordMapper;
import com.campusflow.mapper.TeamMapper;
import com.campusflow.mapper.TeamMemberMapper;
import com.campusflow.mapper.UserMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class TeamService {

    private final TeamMapper teamMapper;
    private final TeamMemberMapper teamMemberMapper;
    private final ActivityMapper activityMapper;
    private final UserMapper userMapper;
    private final ApplicationRecordMapper applicationRecordMapper;
    private final NotificationService notificationService;

    @Transactional
    public CreateTeamResponse create(Long userId, CreateTeamRequest request) {
        Activity activity = getActivityOrThrow(request.getActivityId());
        validateActivityCanCreateTeam(activity);
        assertNotInActivityTeam(userId, activity.getId());
        Long duplicated = teamMapper.selectCount(Wrappers.<Team>lambdaQuery()
            .eq(Team::getActivityId, request.getActivityId())
            .eq(Team::getTeamName, request.getTeamName()));
        if (duplicated > 0) {
            throw new BusinessException(409, "同一活动下队伍名称不能重复");
        }
        Team team = new Team();
        team.setActivityId(request.getActivityId());
        team.setTeamName(request.getTeamName());
        team.setLeaderId(userId);
        team.setSlogan(request.getSlogan());
        team.setDescription(request.getDescription());
        team.setInviteCode(generateInviteCode());
        team.setStatus(TeamStatus.FORMING.getCode());
        teamMapper.insert(team);

        TeamMember leader = new TeamMember();
        leader.setTeamId(team.getId());
        leader.setUserId(userId);
        leader.setMemberRole("leader");
        leader.setJoinStatus(ReviewStatus.APPROVED.getCode());
        leader.setJoinedAt(LocalDateTime.now());
        teamMemberMapper.insert(leader);

        return CreateTeamResponse.builder()
            .teamId(team.getId())
            .inviteCode(team.getInviteCode())
            .build();
    }

    public TeamDetailVO getDetail(Long teamId, Long currentUserId) {
        Team team = getTeamOrThrow(teamId);
        Activity activity = getActivityOrThrow(team.getActivityId());
        User leader = userMapper.selectById(team.getLeaderId());
        List<TeamMemberVO> members = teamMemberMapper.selectList(Wrappers.<TeamMember>lambdaQuery()
                .eq(TeamMember::getTeamId, teamId)
                .eq(TeamMember::getJoinStatus, ReviewStatus.APPROVED.getCode())
                .orderByAsc(TeamMember::getJoinedAt))
            .stream()
            .map(member -> {
                User user = userMapper.selectById(member.getUserId());
                return TeamMemberVO.builder()
                    .userId(member.getUserId())
                    .nickname(user == null ? "未知用户" : user.getNickname())
                    .avatar(user == null ? null : user.getAvatar())
                    .memberRole(member.getMemberRole())
                    .joinStatus(member.getJoinStatus())
                    .joinedAt(member.getJoinedAt())
                    .build();
            })
            .toList();
        List<ApplicationRecordVO> applications = applicationRecordMapper.selectList(Wrappers.<ApplicationRecord>lambdaQuery()
                .eq(ApplicationRecord::getTeamId, teamId)
                .eq(ApplicationRecord::getType, ApplicationType.JOIN_TEAM.getCode())
                .eq(ApplicationRecord::getStatus, ReviewStatus.PENDING.getCode())
                .orderByDesc(ApplicationRecord::getCreatedAt))
            .stream()
            .map(record -> {
                User applicant = userMapper.selectById(record.getApplicantId());
                return ApplicationRecordVO.builder()
                    .id(record.getId())
                    .applicantId(record.getApplicantId())
                    .applicantName(applicant == null ? "未知用户" : applicant.getNickname())
                    .type(record.getType())
                    .status(record.getStatus())
                    .reason(record.getReason())
                    .reviewComment(record.getReviewComment())
                    .createdAt(record.getCreatedAt())
                    .build();
            })
            .toList();
        return TeamDetailVO.builder()
            .id(team.getId())
            .activityId(activity.getId())
            .activityTitle(activity.getTitle())
            .teamName(team.getTeamName())
            .leaderId(team.getLeaderId())
            .leaderName(leader == null ? "未知队长" : leader.getNickname())
            .slogan(team.getSlogan())
            .description(team.getDescription())
            .inviteCode(team.getInviteCode())
            .status(team.getStatus())
            .currentSize(members.size())
            .minTeamSize(activity.getMinTeamSize())
            .maxTeamSize(activity.getMaxTeamSize())
            .canManage(currentUserId != null && currentUserId.equals(team.getLeaderId()))
            .members(members)
            .pendingApplications(applications)
            .build();
    }

    public PageResult<TeamListItemVO> listJoinable(Long userId, TeamQueryRequest request) {
        Page<Team> page = new Page<>(request.getPageNum(), request.getPageSize());
        String keyword = request.getKeyword() == null ? null : request.getKeyword().trim();
        boolean hasKeyword = keyword != null && !keyword.isBlank();
        String inviteKeyword = hasKeyword ? keyword.toUpperCase() : null;
        IPage<Team> result = teamMapper.selectPage(page, Wrappers.<Team>lambdaQuery()
            .eq(Team::getStatus, TeamStatus.FORMING.getCode())
            .and(hasKeyword, query -> query
                .like(Team::getTeamName, keyword)
                .or()
                .like(Team::getInviteCode, inviteKeyword))
            .eq(request.getActivityId() != null, Team::getActivityId, request.getActivityId())
            .orderByDesc(Team::getCreatedAt));
        List<TeamListItemVO> records = result.getRecords().stream()
            .map(team -> {
                Activity activity = activityMapper.selectById(team.getActivityId());
                if (activity == null) {
                    return null;
                }
                User leader = userMapper.selectById(team.getLeaderId());
                int currentSize = getApprovedMemberCount(team.getId());
                boolean applied = false;
                boolean joined = false;
                boolean canApply = false;
                if (userId != null) {
                    TeamMember currentMembership = teamMemberMapper.selectOne(Wrappers.<TeamMember>lambdaQuery()
                        .eq(TeamMember::getTeamId, team.getId())
                        .eq(TeamMember::getUserId, userId)
                        .last("limit 1"));
                    joined = currentMembership != null
                        && ReviewStatus.APPROVED.getCode().equals(currentMembership.getJoinStatus());
                    applied = currentMembership != null
                        && ReviewStatus.PENDING.getCode().equals(currentMembership.getJoinStatus());
                    applied = applicationRecordMapper.selectCount(Wrappers.<ApplicationRecord>lambdaQuery()
                        .eq(ApplicationRecord::getTeamId, team.getId())
                        .eq(ApplicationRecord::getApplicantId, userId)
                        .eq(ApplicationRecord::getType, ApplicationType.JOIN_TEAM.getCode())
                        .eq(ApplicationRecord::getStatus, ReviewStatus.PENDING.getCode())) > 0 || applied;
                    boolean signupOpen = activity.getSignupDeadline() == null
                        || !LocalDateTime.now().isAfter(activity.getSignupDeadline());
                    canApply = signupOpen
                        && !joined
                        && !applied
                        && !hasActiveMembershipInActivity(userId, team.getActivityId())
                        && currentSize < activity.getMaxTeamSize();
                }
                return TeamListItemVO.builder()
                    .id(team.getId())
                    .activityId(team.getActivityId())
                    .activityTitle(activity.getTitle())
                    .teamName(team.getTeamName())
                    .slogan(team.getSlogan())
                    .description(team.getDescription())
                    .inviteCode(team.getInviteCode())
                    .leaderId(team.getLeaderId())
                    .leaderName(leader == null ? "未知队长" : leader.getNickname())
                    .currentSize(currentSize)
                    .maxTeamSize(activity.getMaxTeamSize())
                    .status(team.getStatus())
                    .applied(applied)
                    .joined(joined)
                    .canApply(canApply)
                    .build();
            })
            .filter(java.util.Objects::nonNull)
            .toList();
        return new PageResult<>(result.getTotal(), records);
    }

    @Transactional
    public void applyToJoin(Long userId, Long teamId, String reason) {
        Team team = getTeamOrThrow(teamId);
        Activity activity = getActivityOrThrow(team.getActivityId());
        if (!TeamStatus.FORMING.getCode().equals(team.getStatus())) {
            throw new BusinessException("当前队伍不可申请加入");
        }
        if (LocalDateTime.now().isAfter(activity.getSignupDeadline())) {
            throw new BusinessException("活动报名已截止");
        }
        if (getApprovedMemberCount(teamId) >= activity.getMaxTeamSize()) {
            throw new BusinessException("队伍人数已满");
        }
        if (userId.equals(team.getLeaderId())) {
            throw new BusinessException("队长无需重复申请");
        }
        assertNotInActivityTeam(userId, activity.getId());
        ApplicationRecord pendingRecord = applicationRecordMapper.selectOne(Wrappers.<ApplicationRecord>lambdaQuery()
            .eq(ApplicationRecord::getTeamId, teamId)
            .eq(ApplicationRecord::getApplicantId, userId)
            .eq(ApplicationRecord::getType, ApplicationType.JOIN_TEAM.getCode())
            .eq(ApplicationRecord::getStatus, ReviewStatus.PENDING.getCode())
            .last("limit 1"));
        if (pendingRecord != null) {
            throw new BusinessException(409, "你已经申请过该队伍");
        }
        TeamMember teamMember = teamMemberMapper.selectOne(Wrappers.<TeamMember>lambdaQuery()
            .eq(TeamMember::getTeamId, teamId)
            .eq(TeamMember::getUserId, userId)
            .last("limit 1"));
        if (teamMember == null) {
            teamMember = new TeamMember();
            teamMember.setTeamId(teamId);
            teamMember.setUserId(userId);
            teamMember.setMemberRole("member");
            teamMember.setJoinStatus(ReviewStatus.PENDING.getCode());
            teamMemberMapper.insert(teamMember);
        } else if (ReviewStatus.APPROVED.getCode().equals(teamMember.getJoinStatus())
            || ReviewStatus.PENDING.getCode().equals(teamMember.getJoinStatus())) {
            throw new BusinessException(409, "你已经在该队伍中或申请正在审核");
        } else {
            teamMember.setJoinStatus(ReviewStatus.PENDING.getCode());
            teamMember.setJoinedAt(null);
            teamMemberMapper.updateById(teamMember);
        }
        ApplicationRecord record = new ApplicationRecord();
        record.setActivityId(activity.getId());
        record.setTeamId(teamId);
        record.setApplicantId(userId);
        record.setType(ApplicationType.JOIN_TEAM.getCode());
        record.setStatus(ReviewStatus.PENDING.getCode());
        record.setReason(reason);
        applicationRecordMapper.insert(record);
        User applicant = userMapper.selectById(userId);
        notificationService.createNotice(
            team.getLeaderId(),
            "新的入队申请",
            (applicant == null ? "有同学" : applicant.getNickname()) + " 申请加入队伍「" + team.getTeamName() + "」",
            NotificationType.TEAM_APPLY.getCode()
        );
    }

    @Transactional
    public void submit(Long userId, Long teamId, SubmitTeamRequest request) {
        Team team = getTeamOrThrow(teamId);
        if (!team.getLeaderId().equals(userId)) {
            throw new BusinessException(403, "只有队长可以提交报名");
        }
        Activity activity = getActivityOrThrow(team.getActivityId());
        if (LocalDateTime.now().isAfter(activity.getSignupDeadline())) {
            throw new BusinessException("活动报名已截止");
        }
        int approvedCount = getApprovedMemberCount(teamId);
        if (approvedCount < activity.getMinTeamSize() || approvedCount > activity.getMaxTeamSize()) {
            throw new BusinessException("队伍人数未满足活动要求");
        }
        Long pendingCount = applicationRecordMapper.selectCount(Wrappers.<ApplicationRecord>lambdaQuery()
            .eq(ApplicationRecord::getTeamId, teamId)
            .eq(ApplicationRecord::getType, ApplicationType.SIGNUP_TEAM.getCode())
            .eq(ApplicationRecord::getStatus, ReviewStatus.PENDING.getCode()));
        if (pendingCount > 0) {
            throw new BusinessException(409, "当前队伍已有待审核报名");
        }
        ApplicationRecord application = new ApplicationRecord();
        application.setActivityId(activity.getId());
        application.setTeamId(teamId);
        application.setApplicantId(userId);
        application.setType(ApplicationType.SIGNUP_TEAM.getCode());
        application.setStatus(ReviewStatus.PENDING.getCode());
        application.setReason(request == null ? null : request.getReason());
        applicationRecordMapper.insert(application);
        team.setStatus(TeamStatus.SUBMITTED.getCode());
        teamMapper.updateById(team);

        notificationService.createNotice(
            activity.getOrganizerId(),
            "新的队伍报名待审核",
            "队伍「" + team.getTeamName() + "」已提交活动「" + activity.getTitle() + "」报名，请及时审核。",
            NotificationType.REVIEW_RESULT.getCode()
        );
    }

    public Team getTeamOrThrow(Long teamId) {
        Team team = teamMapper.selectById(teamId);
        if (team == null) {
            throw new BusinessException(404, "队伍不存在");
        }
        return team;
    }

    public Activity getActivityOrThrow(Long activityId) {
        Activity activity = activityMapper.selectById(activityId);
        if (activity == null) {
            throw new BusinessException(404, "活动不存在");
        }
        return activity;
    }

    public int getApprovedMemberCount(Long teamId) {
        return teamMemberMapper.selectList(Wrappers.<TeamMember>lambdaQuery()
                .eq(TeamMember::getTeamId, teamId)
                .eq(TeamMember::getJoinStatus, ReviewStatus.APPROVED.getCode()))
            .size();
    }

    private void validateActivityCanCreateTeam(Activity activity) {
        if (!Boolean.TRUE.equals(activity.getRequireTeam())) {
            throw new BusinessException("当前活动不允许组队");
        }
        if (LocalDateTime.now().isAfter(activity.getSignupDeadline())) {
            throw new BusinessException("活动报名已截止");
        }
    }

    private void assertNotInActivityTeam(Long userId, Long activityId) {
        if (hasActiveMembershipInActivity(userId, activityId)) {
            throw new BusinessException(409, "你已在当前活动的队伍中或申请待审核");
        }
    }

    private boolean hasActiveMembershipInActivity(Long userId, Long activityId) {
        List<TeamMember> memberships = teamMemberMapper.selectList(Wrappers.<TeamMember>lambdaQuery()
            .eq(TeamMember::getUserId, userId)
            .in(TeamMember::getJoinStatus, List.of(ReviewStatus.PENDING.getCode(), ReviewStatus.APPROVED.getCode())));
        for (TeamMember membership : memberships) {
            Team current = teamMapper.selectById(membership.getTeamId());
            if (current != null && current.getActivityId().equals(activityId)) {
                return true;
            }
        }
        return false;
    }

    private String generateInviteCode() {
        return "CF-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
    }
}
