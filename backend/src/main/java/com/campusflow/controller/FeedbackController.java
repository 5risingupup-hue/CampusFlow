package com.campusflow.controller;

import com.campusflow.common.ApiResponse;
import com.campusflow.domain.dto.FeedbackSubmitRequest;
import com.campusflow.domain.vo.FeedbackSummaryVO;
import com.campusflow.service.FeedbackService;
import com.campusflow.support.SecurityUtils;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/feedback")
@RequiredArgsConstructor
public class FeedbackController {

    private final FeedbackService feedbackService;

    @PostMapping
    public ApiResponse<Void> submit(@Valid @RequestBody FeedbackSubmitRequest request) {
        feedbackService.submit(SecurityUtils.getCurrentUserId(), request);
        return ApiResponse.success("反馈提交成功", null);
    }

    @GetMapping("/activity/{activityId}")
    public ApiResponse<FeedbackSummaryVO> byActivity(@PathVariable Long activityId) {
        return ApiResponse.success("查询成功", feedbackService.getByActivity(activityId));
    }
}
