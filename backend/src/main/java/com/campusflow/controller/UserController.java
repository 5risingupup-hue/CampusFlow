package com.campusflow.controller;

import com.campusflow.common.ApiResponse;
import com.campusflow.domain.dto.UpdateProfileRequest;
import com.campusflow.domain.vo.UserProfileVO;
import com.campusflow.service.UserService;
import com.campusflow.support.SecurityUtils;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/user")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @GetMapping("/profile")
    public ApiResponse<UserProfileVO> profile() {
        return ApiResponse.success("查询成功", userService.getProfile(SecurityUtils.getCurrentUserId()));
    }

    @PutMapping("/profile")
    public ApiResponse<UserProfileVO> update(@Valid @RequestBody UpdateProfileRequest request) {
        return ApiResponse.success("更新成功", userService.updateProfile(SecurityUtils.getCurrentUserId(), request));
    }
}
