package com.campusflow.domain.dto;

import jakarta.validation.constraints.Future;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.time.LocalDateTime;

@Data
public class ActivityUpsertRequest {

    @NotBlank(message = "活动标题不能为空")
    private String title;

    private String coverUrl;

    @NotBlank(message = "活动描述不能为空")
    private String description;

    @NotBlank(message = "活动类型不能为空")
    private String type;

    @NotBlank(message = "活动地点不能为空")
    private String location;

    @NotNull(message = "活动开始时间不能为空")
    private LocalDateTime startTime;

    @NotNull(message = "活动结束时间不能为空")
    private LocalDateTime endTime;

    @NotNull(message = "报名截止时间不能为空")
    private LocalDateTime signupDeadline;

    @NotNull(message = "是否组队不能为空")
    private Boolean requireTeam;

    @NotNull(message = "最小队伍人数不能为空")
    @Min(value = 1, message = "最小队伍人数至少为 1")
    private Integer minTeamSize;

    @NotNull(message = "最大队伍人数不能为空")
    @Min(value = 1, message = "最大队伍人数至少为 1")
    private Integer maxTeamSize;

    @NotBlank(message = "活动状态不能为空")
    private String status;

    private String tags;

    private String signCode;

    private LocalDateTime signStartTime;

    private LocalDateTime signEndTime;

    private String resultSummary;
}
