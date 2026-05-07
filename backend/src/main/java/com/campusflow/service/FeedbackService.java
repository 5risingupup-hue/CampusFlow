package com.campusflow.service;

import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.campusflow.domain.dto.FeedbackSubmitRequest;
import com.campusflow.domain.entity.Activity;
import com.campusflow.domain.entity.Feedback;
import com.campusflow.domain.entity.SignRecord;
import com.campusflow.domain.entity.User;
import com.campusflow.domain.vo.FeedbackItemVO;
import com.campusflow.domain.vo.FeedbackSummaryVO;
import com.campusflow.exception.BusinessException;
import com.campusflow.mapper.ActivityMapper;
import com.campusflow.mapper.FeedbackMapper;
import com.campusflow.mapper.SignRecordMapper;
import com.campusflow.mapper.UserMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.Collections;
import java.util.List;

@Service
@RequiredArgsConstructor
public class FeedbackService {

    private final FeedbackMapper feedbackMapper;
    private final ActivityMapper activityMapper;
    private final SignRecordMapper signRecordMapper;
    private final UserMapper userMapper;

    @Transactional
    public void submit(Long userId, FeedbackSubmitRequest request) {
        Activity activity = getActivityOrThrow(request.getActivityId());
        if (LocalDateTime.now().isBefore(activity.getEndTime())) {
            throw new BusinessException("活动结束后才能提交反馈");
        }
        SignRecord signRecord = signRecordMapper.selectOne(Wrappers.<SignRecord>lambdaQuery()
            .eq(SignRecord::getActivityId, request.getActivityId())
            .eq(SignRecord::getUserId, userId)
            .eq(SignRecord::getStatus, "signed")
            .last("limit 1"));
        if (signRecord == null) {
            throw new BusinessException("仅已签到参与者可提交反馈");
        }
        if (feedbackMapper.selectCount(Wrappers.<Feedback>lambdaQuery()
            .eq(Feedback::getActivityId, request.getActivityId())
            .eq(Feedback::getUserId, userId)) > 0) {
            throw new BusinessException(409, "你已提交过本次活动反馈");
        }
        Feedback feedback = new Feedback();
        feedback.setActivityId(request.getActivityId());
        feedback.setUserId(userId);
        feedback.setScore(request.getScore());
        feedback.setContent(request.getContent());
        feedback.setTags(request.getTags() == null ? null : String.join(",", request.getTags()));
        feedback.setWillingRejoin(request.getWillingRejoin());
        feedbackMapper.insert(feedback);
    }

    public FeedbackSummaryVO getByActivity(Long activityId) {
        getActivityOrThrow(activityId);
        List<Feedback> feedbacks = feedbackMapper.selectList(Wrappers.<Feedback>lambdaQuery()
            .eq(Feedback::getActivityId, activityId)
            .orderByDesc(Feedback::getCreatedAt));
        double average = feedbacks.isEmpty()
            ? 0D
            : feedbacks.stream().mapToInt(Feedback::getScore).average().orElse(0D);
        return FeedbackSummaryVO.builder()
            .averageScore(average)
            .total((long) feedbacks.size())
            .records(feedbacks.stream().map(this::toItemVO).toList())
            .build();
    }

    private FeedbackItemVO toItemVO(Feedback feedback) {
        User user = userMapper.selectById(feedback.getUserId());
        return FeedbackItemVO.builder()
            .userId(feedback.getUserId())
            .nickname(user == null ? "匿名用户" : user.getNickname())
            .score(feedback.getScore())
            .content(feedback.getContent())
            .tags(splitTags(feedback.getTags()))
            .willingRejoin(feedback.getWillingRejoin())
            .createdAt(feedback.getCreatedAt())
            .build();
    }

    private List<String> splitTags(String tags) {
        if (tags == null || tags.isBlank()) {
            return Collections.emptyList();
        }
        return List.of(tags.split(","));
    }

    private Activity getActivityOrThrow(Long activityId) {
        Activity activity = activityMapper.selectById(activityId);
        if (activity == null) {
            throw new BusinessException(404, "活动不存在");
        }
        return activity;
    }
}
