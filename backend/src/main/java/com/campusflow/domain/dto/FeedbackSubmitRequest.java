package com.campusflow.domain.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.util.List;

@Data
public class FeedbackSubmitRequest {

    @NotNull(message = "活动 ID 不能为空")
    private Long activityId;

    @NotNull(message = "评分不能为空")
    @Min(value = 1, message = "评分不能低于 1")
    @Max(value = 5, message = "评分不能高于 5")
    private Integer score;

    private String content;

    private List<String> tags;

    private Boolean willingRejoin;
}
