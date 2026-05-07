package com.campusflow.domain.vo;

import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@Builder
public class AnnouncementVO {

    private Long id;
    private String title;
    private String content;
    private Long createdBy;
    private String creatorName;
    private LocalDateTime createdAt;
}
