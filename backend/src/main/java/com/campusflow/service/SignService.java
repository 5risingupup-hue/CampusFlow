package com.campusflow.service;

import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.campusflow.domain.dto.SignInRequest;
import com.campusflow.domain.entity.Activity;
import com.campusflow.domain.entity.SignRecord;
import com.campusflow.domain.entity.Team;
import com.campusflow.domain.entity.TeamMember;
import com.campusflow.domain.enums.ReviewStatus;
import com.campusflow.domain.enums.SignStatus;
import com.campusflow.domain.enums.SignType;
import com.campusflow.domain.vo.SignStatusVO;
import com.campusflow.exception.BusinessException;
import com.campusflow.mapper.ActivityMapper;
import com.campusflow.mapper.SignRecordMapper;
import com.campusflow.mapper.TeamMapper;
import com.campusflow.mapper.TeamMemberMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class SignService {

    private final SignRecordMapper signRecordMapper;
    private final ActivityMapper activityMapper;
    private final TeamMemberMapper teamMemberMapper;
    private final TeamMapper teamMapper;

    public SignStatusVO getStatus(Long userId, Long activityId) {
        Activity activity = getActivityOrThrow(activityId);
        SignRecord record = signRecordMapper.selectOne(Wrappers.<SignRecord>lambdaQuery()
            .eq(SignRecord::getActivityId, activityId)
            .eq(SignRecord::getUserId, userId)
            .last("limit 1"));
        boolean eligible = isEligibleParticipant(userId, activity);
        return SignStatusVO.builder()
            .activityId(activityId)
            .activityTitle(activity.getTitle())
            .status(record == null ? SignStatus.UNSIGNED.getCode() : record.getStatus())
            .eligible(eligible)
            .signWindowOpen(isSignWindowOpen(activity))
            .signTime(record == null ? null : record.getSignTime())
            .build();
    }

    @Transactional
    public Map<String, Object> checkIn(Long userId, SignInRequest request) {
        Activity activity = getActivityOrThrow(request.getActivityId());
        if (!isEligibleParticipant(userId, activity)) {
            throw new BusinessException("仅审核通过的参与者可签到");
        }
        if (!isSignWindowOpen(activity)) {
            throw new BusinessException("当前不在签到时间范围内");
        }
        if (!activity.getSignCode().equalsIgnoreCase(request.getSignCode())) {
            throw new BusinessException("签到码不正确");
        }
        SignRecord record = signRecordMapper.selectOne(Wrappers.<SignRecord>lambdaQuery()
            .eq(SignRecord::getActivityId, request.getActivityId())
            .eq(SignRecord::getUserId, userId)
            .last("limit 1"));
        if (record == null) {
            record = new SignRecord();
            record.setActivityId(request.getActivityId());
            record.setUserId(userId);
            record.setSignType(SignType.CODE.getCode());
            record.setStatus(SignStatus.UNSIGNED.getCode());
            signRecordMapper.insert(record);
        }
        if (SignStatus.SIGNED.getCode().equals(record.getStatus())) {
            throw new BusinessException(409, "请勿重复签到");
        }
        record.setSignType(SignType.CODE.getCode());
        record.setSignTime(LocalDateTime.now());
        record.setStatus(SignStatus.SIGNED.getCode());
        signRecordMapper.updateById(record);
        Map<String, Object> response = new HashMap<>();
        response.put("signTime", record.getSignTime());
        return response;
    }

    private boolean isEligibleParticipant(Long userId, Activity activity) {
        if (!Boolean.TRUE.equals(activity.getRequireTeam())) {
            return true;
        }
        List<TeamMember> memberships = teamMemberMapper.selectList(Wrappers.<TeamMember>lambdaQuery()
            .eq(TeamMember::getUserId, userId)
            .eq(TeamMember::getJoinStatus, ReviewStatus.APPROVED.getCode()));
        for (TeamMember membership : memberships) {
            Team team = teamMapper.selectById(membership.getTeamId());
            if (team != null && team.getActivityId().equals(activity.getId()) && "approved".equals(team.getStatus())) {
                return true;
            }
        }
        return false;
    }

    private boolean isSignWindowOpen(Activity activity) {
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime start = activity.getSignStartTime() == null ? activity.getStartTime().minusHours(1) : activity.getSignStartTime();
        LocalDateTime end = activity.getSignEndTime() == null ? activity.getEndTime() : activity.getSignEndTime();
        return !now.isBefore(start) && !now.isAfter(end);
    }

    private Activity getActivityOrThrow(Long activityId) {
        Activity activity = activityMapper.selectById(activityId);
        if (activity == null) {
            throw new BusinessException(404, "活动不存在");
        }
        return activity;
    }
}
