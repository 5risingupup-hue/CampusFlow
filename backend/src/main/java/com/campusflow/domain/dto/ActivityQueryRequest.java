package com.campusflow.domain.dto;

import lombok.Data;

@Data
public class ActivityQueryRequest {

    private String keyword;

    private String type;

    private Boolean requireTeam;

    private String status;

    private Integer pageNum = 1;

    private Integer pageSize = 10;
}
