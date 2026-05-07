package com.campusflow.domain.vo;

import lombok.Builder;
import lombok.Data;

import java.util.List;

@Data
@Builder
public class FeedbackSummaryVO {

    private Double averageScore;
    private Long total;
    private List<FeedbackItemVO> records;
}
