package com.campusflow.domain.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class CreateTeamRequest {

    @NotNull(message = "活动 ID 不能为空")
    private Long activityId;

    @NotBlank(message = "队伍名称不能为空")
    private String teamName;

    private String slogan;

    private String description;
}
