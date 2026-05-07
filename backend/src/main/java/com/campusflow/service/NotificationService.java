package com.campusflow.service;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.campusflow.common.PageResult;
import com.campusflow.domain.dto.MarkNoticeReadRequest;
import com.campusflow.domain.dto.NoticeQueryRequest;
import com.campusflow.domain.entity.Notification;
import com.campusflow.domain.vo.NotificationVO;
import com.campusflow.mapper.NotificationMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.CollectionUtils;

import java.util.Collection;
import java.util.List;
import java.util.Objects;

@Service
@RequiredArgsConstructor
public class NotificationService {

    private final NotificationMapper notificationMapper;
    private final SimpMessagingTemplate messagingTemplate;

    public PageResult<NotificationVO> pageNotices(Long userId, NoticeQueryRequest request) {
        Page<Notification> page = new Page<>(request.getPageNum(), request.getPageSize());
        IPage<Notification> result = notificationMapper.selectPage(page, Wrappers.<Notification>lambdaQuery()
            .eq(Notification::getUserId, userId)
            .eq(request.getIsRead() != null, Notification::getRead, request.getIsRead())
            .eq(request.getType() != null && !request.getType().isBlank(), Notification::getType, request.getType())
            .orderByDesc(Notification::getCreatedAt));
        return new PageResult<>(
            result.getTotal(),
            result.getRecords().stream().map(this::toVO).toList()
        );
    }

    @Transactional
    public void markRead(Long userId, MarkNoticeReadRequest request) {
        if (request == null || CollectionUtils.isEmpty(request.getIds())) {
            return;
        }
        request.getIds().forEach(id -> {
            Notification notice = notificationMapper.selectById(id);
            if (notice != null && Objects.equals(notice.getUserId(), userId) && !Boolean.TRUE.equals(notice.getRead())) {
                notice.setRead(true);
                notificationMapper.updateById(notice);
            }
        });
    }

    @Transactional
    public void markAllRead(Long userId) {
        List<Notification> notices = notificationMapper.selectList(Wrappers.<Notification>lambdaQuery()
            .eq(Notification::getUserId, userId)
            .eq(Notification::getRead, false));
        notices.forEach(notice -> {
            notice.setRead(true);
            notificationMapper.updateById(notice);
        });
    }

    public Long unreadCount(Long userId) {
        return notificationMapper.selectCount(Wrappers.<Notification>lambdaQuery()
            .eq(Notification::getUserId, userId)
            .eq(Notification::getRead, false));
    }

    @Transactional
    public void createNotice(Long userId, String title, String content, String type) {
        Notification notification = new Notification();
        notification.setUserId(userId);
        notification.setTitle(title);
        notification.setContent(content);
        notification.setType(type);
        notification.setRead(false);
        notificationMapper.insert(notification);
        messagingTemplate.convertAndSend("/topic/notifications/" + userId, toVO(notification));
    }

    @Transactional
    public void createBatchNotices(Collection<Long> userIds, String title, String content, String type) {
        if (CollectionUtils.isEmpty(userIds)) {
            return;
        }
        userIds.stream()
            .filter(Objects::nonNull)
            .distinct()
            .forEach(userId -> createNotice(userId, title, content, type));
    }

    private NotificationVO toVO(Notification notification) {
        return NotificationVO.builder()
            .id(notification.getId())
            .title(notification.getTitle())
            .content(notification.getContent())
            .type(notification.getType())
            .isRead(notification.getRead())
            .createdAt(notification.getCreatedAt())
            .build();
    }
}
