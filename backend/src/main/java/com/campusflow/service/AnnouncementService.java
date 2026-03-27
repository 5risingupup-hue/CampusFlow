package com.campusflow.service;

import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.campusflow.domain.dto.AnnouncementCreateRequest;
import com.campusflow.domain.entity.Announcement;
import com.campusflow.domain.entity.User;
import com.campusflow.domain.enums.NotificationType;
import com.campusflow.domain.vo.AnnouncementVO;
import com.campusflow.mapper.AnnouncementMapper;
import com.campusflow.mapper.UserMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class AnnouncementService {

    private final AnnouncementMapper announcementMapper;
    private final UserMapper userMapper;
    private final NotificationService notificationService;

    public List<AnnouncementVO> listAll() {
        return announcementMapper.selectList(Wrappers.<Announcement>lambdaQuery()
                .orderByDesc(Announcement::getCreatedAt))
            .stream()
            .map(this::toVO)
            .toList();
    }

    @Transactional
    public AnnouncementVO create(Long userId, AnnouncementCreateRequest request) {
        Announcement announcement = new Announcement();
        announcement.setTitle(request.getTitle());
        announcement.setContent(request.getContent());
        announcement.setCreatedBy(userId);
        announcementMapper.insert(announcement);
        List<Long> userIds = userMapper.selectList(Wrappers.<User>lambdaQuery())
            .stream()
            .map(User::getId)
            .toList();
        notificationService.createBatchNotices(
            userIds,
            "新公告发布",
            request.getTitle(),
            NotificationType.ANNOUNCEMENT.getCode()
        );
        return toVO(announcement);
    }

    private AnnouncementVO toVO(Announcement announcement) {
        User creator = userMapper.selectById(announcement.getCreatedBy());
        return AnnouncementVO.builder()
            .id(announcement.getId())
            .title(announcement.getTitle())
            .content(announcement.getContent())
            .createdBy(announcement.getCreatedBy())
            .creatorName(creator == null ? "未知用户" : creator.getNickname())
            .createdAt(announcement.getCreatedAt())
            .build();
    }
}
