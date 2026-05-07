package com.campusflow.domain.vo;

import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@Builder
public class ReviewItemVO {

    private Long id;
    private String type;
    private String status;
    private Long activityId;
    private String activityTitle;
    private Long teamId;
    private String teamName;
    private Long applicantId;
    private String applicantName;
    private String reason;
    private Integer memberCount;
    private String reviewComment;
    private LocalDateTime createdAt;
}
