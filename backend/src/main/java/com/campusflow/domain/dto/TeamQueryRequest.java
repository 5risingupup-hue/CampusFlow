package com.campusflow.domain.dto;

import lombok.Data;

@Data
public class TeamQueryRequest {

    private Long activityId;

    private String keyword;

    private Integer pageNum = 1;

    private Integer pageSize = 10;
}
