package com.campusflow.domain.dto;

import lombok.Data;

@Data
public class ReviewQueryRequest {

    private String status;

    private String keyword;

    private Integer pageNum = 1;

    private Integer pageSize = 10;
}
