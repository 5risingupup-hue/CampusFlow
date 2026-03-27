package com.campusflow.controller;

import com.campusflow.common.ApiResponse;
import com.campusflow.domain.dto.SignInRequest;
import com.campusflow.domain.vo.SignStatusVO;
import com.campusflow.service.SignService;
import com.campusflow.support.SecurityUtils;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/sign")
@RequiredArgsConstructor
public class SignController {

    private final SignService signService;

    @GetMapping("/status/{activityId}")
    public ApiResponse<SignStatusVO> status(@PathVariable Long activityId) {
        return ApiResponse.success("查询成功", signService.getStatus(SecurityUtils.getCurrentUserId(), activityId));
    }

    @PostMapping("/check-in")
    public ApiResponse<Map<String, Object>> checkIn(@Valid @RequestBody SignInRequest request) {
        return ApiResponse.success("签到成功", signService.checkIn(SecurityUtils.getCurrentUserId(), request));
    }
}
