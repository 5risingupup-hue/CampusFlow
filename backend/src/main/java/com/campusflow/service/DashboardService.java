package com.campusflow.service;

import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.campusflow.domain.entity.Activity;
import com.campusflow.domain.entity.ApplicationRecord;
import com.campusflow.domain.entity.Feedback;
import com.campusflow.domain.entity.SignRecord;
import com.campusflow.domain.entity.Team;
import com.campusflow.domain.entity.TeamMember;
import com.campusflow.domain.vo.ActivityCardVO;
import com.campusflow.domain.vo.DashboardOverviewVO;
import com.campusflow.domain.vo.NameValueVO;
import com.campusflow.mapper.ActivityMapper;
import com.campusflow.mapper.ApplicationRecordMapper;
import com.campusflow.mapper.FeedbackMapper;
import com.campusflow.mapper.SignRecordMapper;
import com.campusflow.mapper.TeamMapper;
import com.campusflow.mapper.TeamMemberMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class DashboardService {

    private final ActivityMapper activityMapper;
    private final TeamMapper teamMapper;
    private final TeamMemberMapper teamMemberMapper;
    private final ApplicationRecordMapper applicationRecordMapper;
    private final SignRecordMapper signRecordMapper;
    private final FeedbackMapper feedbackMapper;
    private final NotificationService notificationService;
    private final ActivityService activityService;

    public DashboardOverviewVO overview(Long userId, String role) {
        List<Activity> activityScope = resolveActivityScope(userId, role);
        List<Long> activityIds = activityScope.stream().map(Activity::getId).toList();
        long activityCount = activityScope.size();
        long teamCount = resolveTeamCount(userId, role, activityIds);
        long pendingCount = resolvePendingCount(userId, role, activityIds);
        long unreadCount = notificationService.unreadCount(userId);
        long signedCount = resolveSignedCount(userId, role, activityIds);
        double feedbackAverage = resolveFeedbackAverage(userId, role, activityIds);
        List<NameValueVO> distribution = activityScope.stream()
            .collect(Collectors.groupingBy(Activity::getType, Collectors.counting()))
            .entrySet()
            .stream()
            .map(entry -> new NameValueVO(entry.getKey(), entry.getValue()))
            .sorted(Comparator.comparing(NameValueVO::getValue).reversed())
            .toList();
        List<ActivityCardVO> upcomingActivities = activityScope.stream()
            .filter(activity -> activity.getStartTime() == null || activity.getStartTime().isAfter(LocalDateTime.now().minusDays(1)))
            .sorted(Comparator.comparing(Activity::getStartTime))
            .limit(5)
            .map(activityService::toCardVO)
            .toList();

        return DashboardOverviewVO.builder()
            .role(role)
            .activityCount(activityCount)
            .teamCount(teamCount)
            .pendingCount(pendingCount)
            .unreadCount(unreadCount)
            .signedCount(signedCount)
            .feedbackAverage(feedbackAverage)
            .activityTypeDistribution(distribution)
            .upcomingActivities(upcomingActivities)
            .build();
    }

    private List<Activity> resolveActivityScope(Long userId, String role) {
        if ("organizer".equals(role)) {
            return activityMapper.selectList(Wrappers.<Activity>lambdaQuery()
                .eq(Activity::getOrganizerId, userId)
                .orderByDesc(Activity::getCreatedAt));
        }
        return activityMapper.selectList(Wrappers.<Activity>lambdaQuery()
            .ne(Activity::getStatus, "draft")
            .orderByDesc(Activity::getCreatedAt));
    }

    private long resolveTeamCount(Long userId, String role, List<Long> activityIds) {
        if ("student".equals(role) || "captain".equals(role)) {
            return teamMemberMapper.selectCount(Wrappers.<TeamMember>lambdaQuery().eq(TeamMember::getUserId, userId));
        }
        if (activityIds.isEmpty()) {
            return 0;
        }
        return teamMapper.selectCount(Wrappers.<Team>lambdaQuery().in(Team::getActivityId, activityIds));
    }

    private long resolvePendingCount(Long userId, String role, List<Long> activityIds) {
        if ("student".equals(role) || "captain".equals(role)) {
            return applicationRecordMapper.selectCount(Wrappers.<ApplicationRecord>lambdaQuery()
                .eq(ApplicationRecord::getApplicantId, userId)
                .eq(ApplicationRecord::getStatus, "pending"));
        }
        if (activityIds.isEmpty()) {
            return 0;
        }
        return applicationRecordMapper.selectCount(Wrappers.<ApplicationRecord>lambdaQuery()
            .in(ApplicationRecord::getActivityId, activityIds)
            .eq(ApplicationRecord::getStatus, "pending"));
    }

    private long resolveSignedCount(Long userId, String role, List<Long> activityIds) {
        if ("student".equals(role) || "captain".equals(role)) {
            return signRecordMapper.selectCount(Wrappers.<SignRecord>lambdaQuery()
                .eq(SignRecord::getUserId, userId)
                .eq(SignRecord::getStatus, "signed"));
        }
        if (activityIds.isEmpty()) {
            return 0;
        }
        return signRecordMapper.selectCount(Wrappers.<SignRecord>lambdaQuery()
            .in(SignRecord::getActivityId, activityIds)
            .eq(SignRecord::getStatus, "signed"));
    }

    private double resolveFeedbackAverage(Long userId, String role, List<Long> activityIds) {
        List<Feedback> feedbacks;
        if ("student".equals(role) || "captain".equals(role)) {
            feedbacks = feedbackMapper.selectList(Wrappers.<Feedback>lambdaQuery().eq(Feedback::getUserId, userId));
        } else if (activityIds.isEmpty()) {
            feedbacks = List.of();
        } else {
            feedbacks = feedbackMapper.selectList(Wrappers.<Feedback>lambdaQuery().in(Feedback::getActivityId, activityIds));
        }
        return feedbacks.isEmpty()
            ? 0D
            : feedbacks.stream().mapToInt(Feedback::getScore).average().orElse(0D);
    }
}
