package com.campusflow.domain.vo;

import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

@Data
@Builder
public class FeedbackItemVO {

    private Long userId;
    private String nickname;
    private Integer score;
    private String content;
    private List<String> tags;
    private Boolean willingRejoin;
    private LocalDateTime createdAt;
}
