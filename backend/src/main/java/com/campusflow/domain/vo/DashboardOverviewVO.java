package com.campusflow.domain.vo;

import lombok.Builder;
import lombok.Data;

import java.util.List;

@Data
@Builder
public class DashboardOverviewVO {

    private String role;
    private Long activityCount;
    private Long teamCount;
    private Long pendingCount;
    private Long unreadCount;
    private Long signedCount;
    private Double feedbackAverage;
    private List<NameValueVO> activityTypeDistribution;
    private List<ActivityCardVO> upcomingActivities;
}
