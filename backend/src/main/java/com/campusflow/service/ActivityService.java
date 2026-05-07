package com.campusflow.service;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.campusflow.common.PageResult;
import com.campusflow.domain.dto.ActivityQueryRequest;
import com.campusflow.domain.dto.ActivityUpsertRequest;
import com.campusflow.domain.entity.Activity;
import com.campusflow.domain.entity.Feedback;
import com.campusflow.domain.entity.Role;
import com.campusflow.domain.entity.SignRecord;
import com.campusflow.domain.entity.Team;
import com.campusflow.domain.entity.TeamMember;
import com.campusflow.domain.entity.User;
import com.campusflow.domain.enums.ReviewStatus;
import com.campusflow.domain.vo.ActivityCardVO;
import com.campusflow.domain.vo.ActivityDetailVO;
import com.campusflow.exception.BusinessException;
import com.campusflow.mapper.ActivityMapper;
import com.campusflow.mapper.FeedbackMapper;
import com.campusflow.mapper.RoleMapper;
import com.campusflow.mapper.SignRecordMapper;
import com.campusflow.mapper.TeamMapper;
import com.campusflow.mapper.TeamMemberMapper;
import com.campusflow.mapper.UserMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.Collections;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class ActivityService {

    private final ActivityMapper activityMapper;
    private final UserMapper userMapper;
    private final TeamMapper teamMapper;
    private final TeamMemberMapper teamMemberMapper;
    private final FeedbackMapper feedbackMapper;
    private final SignRecordMapper signRecordMapper;
    private final RoleMapper roleMapper;

    public PageResult<ActivityCardVO> pageActivities(ActivityQueryRequest request) {
        Page<Activity> page = new Page<>(request.getPageNum(), request.getPageSize());
        IPage<Activity> result = activityMapper.selectPage(page, Wrappers.<Activity>lambdaQuery()
            .like(request.getKeyword() != null && !request.getKeyword().isBlank(), Activity::getTitle, request.getKeyword())
            .eq(request.getType() != null && !request.getType().isBlank(), Activity::getType, request.getType())
            .eq(request.getRequireTeam() != null, Activity::getRequireTeam, request.getRequireTeam())
            .eq(request.getStatus() != null && !request.getStatus().isBlank(), Activity::getStatus, request.getStatus())
            .ne(request.getStatus() == null || request.getStatus().isBlank(), Activity::getStatus, "draft")
            .orderByAsc(Activity::getStartTime));
        return new PageResult<>(result.getTotal(), result.getRecords().stream().map(this::toCardVO).toList());
    }

    public ActivityDetailVO getDetail(Long activityId, Long currentUserId) {
        Activity activity = getActivityOrThrow(activityId);
        User organizer = userMapper.selectById(activity.getOrganizerId());
        Long teamCount = teamMapper.selectCount(Wrappers.<Team>lambdaQuery().eq(Team::getActivityId, activityId));
        Long myTeamId = null;
        String myApplicationStatus = null;
        Boolean canCreateTeam = Boolean.TRUE.equals(activity.getRequireTeam());
        Boolean canApplyTeam = Boolean.TRUE.equals(activity.getRequireTeam());
        Boolean canSignIn = false;
        Boolean canFeedback = false;
        if (currentUserId != null) {
            List<TeamMember> memberships = teamMemberMapper.selectList(Wrappers.<TeamMember>lambdaQuery()
                .eq(TeamMember::getUserId, currentUserId)
                .in(TeamMember::getJoinStatus, List.of("pending", "approved")));
            for (TeamMember membership : memberships) {
                Team team = teamMapper.selectById(membership.getTeamId());
                if (team != null && team.getActivityId().equals(activityId)) {
                    myTeamId = team.getId();
                    myApplicationStatus = membership.getJoinStatus();
                    canCreateTeam = false;
                    canApplyTeam = false;
                    break;
                }
            }
            SignRecord signRecord = signRecordMapper.selectOne(Wrappers.<SignRecord>lambdaQuery()
                .eq(SignRecord::getActivityId, activityId)
                .eq(SignRecord::getUserId, currentUserId)
                .last("limit 1"));
            canSignIn = signRecord != null || myTeamId != null || !Boolean.TRUE.equals(activity.getRequireTeam());
            canFeedback = signRecord != null && "signed".equals(signRecord.getStatus());
            if (feedbackMapper.selectCount(Wrappers.<Feedback>lambdaQuery()
                .eq(Feedback::getActivityId, activityId)
                .eq(Feedback::getUserId, currentUserId)) > 0) {
                canFeedback = false;
            }
        }
        return ActivityDetailVO.builder()
            .id(activity.getId())
            .title(activity.getTitle())
            .coverUrl(activity.getCoverUrl())
            .description(activity.getDescription())
            .organizerId(activity.getOrganizerId())
            .organizerName(organizer == null ? "未知组织者" : organizer.getNickname())
            .type(activity.getType())
            .location(activity.getLocation())
            .startTime(activity.getStartTime())
            .endTime(activity.getEndTime())
            .signupDeadline(activity.getSignupDeadline())
            .requireTeam(activity.getRequireTeam())
            .minTeamSize(activity.getMinTeamSize())
            .maxTeamSize(activity.getMaxTeamSize())
            .status(activity.getStatus())
            .tags(splitTags(activity.getTags()))
            .teamCount(teamCount.intValue())
            .myTeamId(myTeamId)
            .myApplicationStatus(myApplicationStatus)
            .canCreateTeam(canCreateTeam)
            .canApplyTeam(canApplyTeam)
            .canSignIn(canSignIn)
            .canFeedback(canFeedback)
            .resultSummary(activity.getResultSummary())
            .build();
    }

    public List<ActivityCardVO> listMine(Long userId) {
        return activityMapper.selectList(Wrappers.<Activity>lambdaQuery()
                .eq(Activity::getOrganizerId, userId)
                .orderByDesc(Activity::getCreatedAt))
            .stream()
            .map(this::toCardVO)
            .toList();
    }

    @Transactional
    public ActivityDetailVO create(Long currentUserId, ActivityUpsertRequest request) {
        validateTimeRange(request);
        Activity activity = new Activity();
        fillActivity(activity, request);
        activity.setOrganizerId(currentUserId);
        if (activity.getSignCode() == null || activity.getSignCode().isBlank()) {
            activity.setSignCode(generateSignCode());
        }
        activityMapper.insert(activity);
        return getDetail(activity.getId(), currentUserId);
    }

    @Transactional
    public ActivityDetailVO update(Long currentUserId, Long activityId, ActivityUpsertRequest request) {
        validateTimeRange(request);
        Activity activity = getActivityOrThrow(activityId);
        assertCanManageActivity(currentUserId, activity);
        fillActivity(activity, request);
        if (activity.getSignCode() == null || activity.getSignCode().isBlank()) {
            activity.setSignCode(generateSignCode());
        }
        activityMapper.updateById(activity);
        return getDetail(activityId, currentUserId);
    }

    public Activity getActivityOrThrow(Long activityId) {
        Activity activity = activityMapper.selectById(activityId);
        if (activity == null) {
            throw new BusinessException(404, "活动不存在");
        }
        return activity;
    }

    public ActivityCardVO toCardVO(Activity activity) {
        User organizer = userMapper.selectById(activity.getOrganizerId());
        return ActivityCardVO.builder()
            .id(activity.getId())
            .title(activity.getTitle())
            .coverUrl(activity.getCoverUrl())
            .organizerName(organizer == null ? "未知组织者" : organizer.getNickname())
            .type(activity.getType())
            .location(activity.getLocation())
            .startTime(activity.getStartTime())
            .signupDeadline(activity.getSignupDeadline())
            .requireTeam(activity.getRequireTeam())
            .status(activity.getStatus())
            .tags(splitTags(activity.getTags()))
            .build();
    }

    private void fillActivity(Activity activity, ActivityUpsertRequest request) {
        activity.setTitle(request.getTitle());
        activity.setCoverUrl(request.getCoverUrl());
        activity.setDescription(request.getDescription());
        activity.setType(request.getType());
        activity.setLocation(request.getLocation());
        activity.setStartTime(request.getStartTime());
        activity.setEndTime(request.getEndTime());
        activity.setSignupDeadline(request.getSignupDeadline());
        activity.setRequireTeam(request.getRequireTeam());
        activity.setMinTeamSize(request.getMinTeamSize());
        activity.setMaxTeamSize(request.getMaxTeamSize());
        activity.setStatus(request.getStatus());
        activity.setTags(request.getTags());
        activity.setSignCode(request.getSignCode());
        activity.setSignStartTime(request.getSignStartTime());
        activity.setSignEndTime(request.getSignEndTime());
        activity.setResultSummary(request.getResultSummary());
    }

    private void validateTimeRange(ActivityUpsertRequest request) {
        if (request.getEndTime().isBefore(request.getStartTime())) {
            throw new BusinessException("活动结束时间不能早于开始时间");
        }
        if (request.getSignupDeadline().isAfter(request.getStartTime())) {
            throw new BusinessException("报名截止时间必须早于活动开始时间");
        }
        if (request.getMaxTeamSize() < request.getMinTeamSize()) {
            throw new BusinessException("最大队伍人数不能小于最小队伍人数");
        }
        if (request.getSignStartTime() != null && request.getSignEndTime() != null
            && request.getSignEndTime().isBefore(request.getSignStartTime())) {
            throw new BusinessException("签到结束时间不能早于签到开始时间");
        }
    }

    private void assertCanManageActivity(Long currentUserId, Activity activity) {
        User currentUser = userMapper.selectById(currentUserId);
        Role role = currentUser == null ? null : roleMapper.selectById(currentUser.getRoleId());
        boolean isAdmin = role != null && "admin".equals(role.getRoleName());
        if (!isAdmin && !activity.getOrganizerId().equals(currentUserId)) {
            throw new BusinessException(403, "仅组织者或管理员可管理活动");
        }
    }

    private String generateSignCode() {
        return "SIGN-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
    }

    private List<String> splitTags(String tags) {
        if (tags == null || tags.isBlank()) {
            return Collections.emptyList();
        }
        return List.of(tags.split(","));
    }
}
