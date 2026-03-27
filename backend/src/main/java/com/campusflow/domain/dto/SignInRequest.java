package com.campusflow.domain.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class SignInRequest {

    @NotNull(message = "活动 ID 不能为空")
    private Long activityId;

    @NotBlank(message = "签到码不能为空")
    private String signCode;
}
