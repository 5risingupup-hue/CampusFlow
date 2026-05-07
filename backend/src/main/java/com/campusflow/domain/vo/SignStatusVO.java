package com.campusflow.domain.vo;

import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@Builder
public class SignStatusVO {

    private Long activityId;
    private String activityTitle;
    private String status;
    private Boolean eligible;
    private Boolean signWindowOpen;
    private LocalDateTime signTime;
}
