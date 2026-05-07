package com.campusflow.controller;

import com.campusflow.common.ApiResponse;
import com.campusflow.common.PageResult;
import com.campusflow.domain.dto.ActivityQueryRequest;
import com.campusflow.domain.dto.ActivityUpsertRequest;
import com.campusflow.domain.vo.ActivityCardVO;
import com.campusflow.domain.vo.ActivityDetailVO;
import com.campusflow.service.ActivityService;
import com.campusflow.support.SecurityUtils;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/activities")
@RequiredArgsConstructor
public class ActivityController {

    private final ActivityService activityService;

    @GetMapping
    public ApiResponse<PageResult<ActivityCardVO>> page(@ModelAttribute ActivityQueryRequest request) {
        return ApiResponse.success("查询成功", activityService.pageActivities(request));
    }

    @GetMapping("/mine")
    @PreAuthorize("isAuthenticated()")
    public ApiResponse<List<ActivityCardVO>> mine() {
        return ApiResponse.success("查询成功", activityService.listMine(SecurityUtils.getCurrentUserId()));
    }

    @GetMapping("/{id}")
    public ApiResponse<ActivityDetailVO> detail(@PathVariable Long id) {
        return ApiResponse.success("查询成功", activityService.getDetail(id, SecurityUtils.getCurrentUserId()));
    }

    @PostMapping
    @PreAuthorize("hasAnyRole('ORGANIZER','ADMIN')")
    public ApiResponse<ActivityDetailVO> create(@Valid @RequestBody ActivityUpsertRequest request) {
        return ApiResponse.success("创建成功", activityService.create(SecurityUtils.getCurrentUserId(), request));
    }

    @PutMapping("/{id}")
    @PreAuthorize("hasAnyRole('ORGANIZER','ADMIN')")
    public ApiResponse<ActivityDetailVO> update(@PathVariable Long id, @Valid @RequestBody ActivityUpsertRequest request) {
        return ApiResponse.success("更新成功", activityService.update(SecurityUtils.getCurrentUserId(), id, request));
    }
}
