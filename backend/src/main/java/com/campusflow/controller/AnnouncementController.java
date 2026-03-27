package com.campusflow.controller;

import com.campusflow.common.ApiResponse;
import com.campusflow.domain.dto.AnnouncementCreateRequest;
import com.campusflow.domain.vo.AnnouncementVO;
import com.campusflow.service.AnnouncementService;
import com.campusflow.support.SecurityUtils;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/announcements")
@RequiredArgsConstructor
public class AnnouncementController {

    private final AnnouncementService announcementService;

    @GetMapping
    public ApiResponse<List<AnnouncementVO>> list() {
        return ApiResponse.success("查询成功", announcementService.listAll());
    }

    @PostMapping
    @PreAuthorize("hasRole('ADMIN')")
    public ApiResponse<AnnouncementVO> create(@Valid @RequestBody AnnouncementCreateRequest request) {
        return ApiResponse.success("发布成功", announcementService.create(SecurityUtils.getCurrentUserId(), request));
    }
}
