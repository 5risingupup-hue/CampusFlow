package com.campusflow.controller;

import com.campusflow.common.ApiResponse;
import com.campusflow.common.PageResult;
import com.campusflow.domain.dto.MarkNoticeReadRequest;
import com.campusflow.domain.dto.NoticeQueryRequest;
import com.campusflow.domain.vo.NotificationVO;
import com.campusflow.service.NotificationService;
import com.campusflow.support.SecurityUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/notices")
@RequiredArgsConstructor
public class NotificationController {

    private final NotificationService notificationService;

    @GetMapping
    public ApiResponse<PageResult<NotificationVO>> page(@ModelAttribute NoticeQueryRequest request) {
        return ApiResponse.success("查询成功", notificationService.pageNotices(SecurityUtils.getCurrentUserId(), request));
    }

    @PostMapping("/read")
    public ApiResponse<Void> markRead(@RequestBody MarkNoticeReadRequest request) {
        notificationService.markRead(SecurityUtils.getCurrentUserId(), request);
        return ApiResponse.success("操作成功", null);
    }

    @PostMapping("/read-all")
    public ApiResponse<Void> markAllRead() {
        notificationService.markAllRead(SecurityUtils.getCurrentUserId());
        return ApiResponse.success("操作成功", null);
    }

    @GetMapping("/unread-count")
    public ApiResponse<Map<String, Long>> unreadCount() {
        return ApiResponse.success("查询成功", Map.of("count", notificationService.unreadCount(SecurityUtils.getCurrentUserId())));
    }
}
