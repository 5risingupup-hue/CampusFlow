package com.campusflow.controller;

import com.campusflow.common.ApiResponse;
import com.campusflow.common.PageResult;
import com.campusflow.domain.dto.ReviewQueryRequest;
import com.campusflow.domain.dto.ReviewRequest;
import com.campusflow.domain.vo.ReviewItemVO;
import com.campusflow.service.ReviewService;
import com.campusflow.support.SecurityUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/reviews")
@RequiredArgsConstructor
public class ReviewController {

    private final ReviewService reviewService;

    @GetMapping
    public ApiResponse<PageResult<ReviewItemVO>> page(@ModelAttribute ReviewQueryRequest request) {
        return ApiResponse.success("查询成功", reviewService.pageOrganizerReviews(
            SecurityUtils.getCurrentUserId(),
            SecurityUtils.getCurrentRole(),
            request
        ));
    }

    @PostMapping("/{id}/approve")
    public ApiResponse<Void> approve(@PathVariable Long id, @RequestBody(required = false) ReviewRequest request) {
        reviewService.approve(id, SecurityUtils.getCurrentUserId(), SecurityUtils.getCurrentRole(), request == null ? null : request.getComment());
        return ApiResponse.success("审核通过", null);
    }

    @PostMapping("/{id}/reject")
    public ApiResponse<Void> reject(@PathVariable Long id, @RequestBody(required = false) ReviewRequest request) {
        reviewService.reject(id, SecurityUtils.getCurrentUserId(), SecurityUtils.getCurrentRole(), request == null ? null : request.getComment());
        return ApiResponse.success("审核驳回", null);
    }
}
