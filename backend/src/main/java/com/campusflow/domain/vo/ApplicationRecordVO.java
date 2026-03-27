package com.campusflow.domain.vo;

import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@Builder
public class ApplicationRecordVO {

    private Long id;
    private Long applicantId;
    private String applicantName;
    private String type;
    private String status;
    private String reason;
    private String reviewComment;
    private LocalDateTime createdAt;
}
