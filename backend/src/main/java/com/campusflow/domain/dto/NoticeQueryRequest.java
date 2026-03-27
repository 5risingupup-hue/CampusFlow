package com.campusflow.domain.dto;

import lombok.Data;

@Data
public class NoticeQueryRequest {

    private Boolean isRead;

    private String type;

    private Integer pageNum = 1;

    private Integer pageSize = 10;
}
