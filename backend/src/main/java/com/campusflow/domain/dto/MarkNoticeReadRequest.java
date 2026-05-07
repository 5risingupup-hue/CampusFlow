package com.campusflow.domain.dto;

import lombok.Data;

import java.util.List;

@Data
public class MarkNoticeReadRequest {

    private List<Long> ids;
}
