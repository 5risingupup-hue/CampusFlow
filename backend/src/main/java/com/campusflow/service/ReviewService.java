package com.campusflow.service;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.campusflow.common.PageResult;
import com.campusflow.domain.dto.ReviewQueryRequest;
import com.campusflow.domain.entity.Activity;
import com.campusflow.domain.entity.ApplicationRecord;
import com.campusflow.domain.entity.SignRecord;
import com.campusflow.domain.entity.Team;
import com.campusflow.domain.entity.TeamMember;
import com.campusflow.domain.entity.User;
import com.campusflow.domain.enums.ApplicationType;
import com.campusflow.domain.enums.NotificationType;
import com.campusflow.domain.enums.ReviewStatus;
import com.campusflow.domain.enums.SignStatus;
import com.campusflow.domain.enums.SignType;
import com.campusflow.domain.enums.TeamStatus;
import com.campusflow.domain.vo.ReviewItemVO;
import com.campusflow.exception.BusinessException;
import com.campusflow.mapper.ActivityMapper;
import com.campusflow.mapper.ApplicationRecordMapper;
import com.campusflow.mapper.SignRecordMapper;
import com.campusflow.mapper.TeamMapper;
import com.campusflow.mapper.TeamMemberMapper;
import com.campusflow.mapper.UserMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
public class ReviewService {

    private final ApplicationRecordMapper applicationRecordMapper;
    private final TeamMapper teamMapper;
    private final TeamMemberMapper teamMemberMapper;
    private final ActivityMapper activityMapper;
    private final UserMapper userMapper;
    private final NotificationService notificationService;
    private final SignRecordMapper signRecordMapper;
    private final TeamService teamService;

    public PageResult<ReviewItemVO> pageOrganizerReviews(Long userId, String role, ReviewQueryRequest request) {
        List<Long> activityIds = resolveVisibleActivityIds(userId, role);
        if (activityIds.isEmpty()) {
            return new PageResult<>(0L, List.of());
        }
        Page<ApplicationRecord> page = new Page<>(request.getPageNum(), request.getPageSize());
        IPage<ApplicationRecord> result = applicationRecordMapper.selectPage(page, Wrappers.<ApplicationRecord>lambdaQuery()
            .in(ApplicationRecord::getActivityId, activityIds)
            .eq(ApplicationRecord::getType, ApplicationType.SIGNUP_TEAM.getCode())
            .eq(request.getStatus() != null && !request.getStatus().isBlank(), ApplicationRecord::getStatus, request.getStatus())
            .like(request.getKeyword() != null && !request.getKeyword().isBlank(), ApplicationRecord::getReason, request.getKeyword())
            .orderByDesc(ApplicationRecord::getCreatedAt));
        return new PageResult<>(result.getTotal(), result.getRecords().stream().map(this::toReviewItem).toList());
    }

    @Transactional
    public void approve(Long reviewId, Long operatorId, String operatorRole, String comment) {
        ApplicationRecord record = getApplicationOrThrow(reviewId);
        if (ApplicationType.JOIN_TEAM.getCode().equals(record.getType())) {
            handleJoinTeamReview(record, operatorId, true, comment);
            return;
        }
        handleSignupReview(record, operatorId, operatorRole, true, comment);
    }

    @Transactional
    public void reject(Long reviewId, Long operatorId, String operatorRole, String comment) {
        ApplicationRecord record = getApplicationOrThrow(reviewId);
        if (ApplicationType.JOIN_TEAM.getCode().equals(record.getType())) {
            handleJoinTeamReview(record, operatorId, false, comment);
            return;
        }
        handleSignupReview(record, operatorId, operatorRole, false, comment);
    }

    private void handleJoinTeamReview(ApplicationRecord record, Long operatorId, boolean approve, String comment) {
        ensurePending(record);
        Team team = teamService.getTeamOrThrow(record.getTeamId());
        if (!team.getLeaderId().equals(operatorId)) {
            throw new BusinessException(403, "只有队长可以审核入队申请");
        }
        Activity activity = teamService.getActivityOrThrow(team.getActivityId());
        TeamMember member = teamMemberMapper.selectOne(Wrappers.<TeamMember>lambdaQuery()
            .eq(TeamMember::getTeamId, team.getId())
            .eq(TeamMember::getUserId, record.getApplicantId())
            .last("limit 1"));
        if (member == null) {
            throw new BusinessException(404, "入队申请成员记录不存在");
        }
        if (approve) {
            if (teamService.getApprovedMemberCount(team.getId()) >= activity.getMaxTeamSize()) {
                throw new BusinessException("队伍人数已满，无法通过申请");
            }
            validateApplicantNotInAnotherTeam(record.getApplicantId(), team.getId(), activity.getId());
            member.setJoinStatus(ReviewStatus.APPROVED.getCode());
            member.setJoinedAt(LocalDateTime.now());
            teamMemberMapper.updateById(member);
            updateApplication(record, ReviewStatus.APPROVED.getCode(), operatorId, comment);
            notificationService.createNotice(
                record.getApplicantId(),
                "入队申请已通过",
                "你申请加入的队伍「" + team.getTeamName() + "」已通过审核。",
                NotificationType.REVIEW_RESULT.getCode()
            );
        } else {
            member.setJoinStatus(ReviewStatus.REJECTED.getCode());
            teamMemberMapper.updateById(member);
            updateApplication(record, ReviewStatus.REJECTED.getCode(), operatorId, comment);
            notificationService.createNotice(
                record.getApplicantId(),
                "入队申请未通过",
                "你申请加入的队伍「" + team.getTeamName() + "」被拒绝，原因：" + defaultComment(comment),
                NotificationType.REVIEW_RESULT.getCode()
            );
        }
    }

    private void handleSignupReview(ApplicationRecord record, Long operatorId, String operatorRole, boolean approve, String comment) {
        ensurePending(record);
        Team team = teamService.getTeamOrThrow(record.getTeamId());
        Activity activity = teamService.getActivityOrThrow(record.getActivityId());
        if (!"admin".equals(operatorRole) && !activity.getOrganizerId().equals(operatorId)) {
            throw new BusinessException(403, "只有活动组织者或管理员可以审核报名");
        }
        List<TeamMember> approvedMembers = teamMemberMapper.selectList(Wrappers.<TeamMember>lambdaQuery()
            .eq(TeamMember::getTeamId, team.getId())
            .eq(TeamMember::getJoinStatus, ReviewStatus.APPROVED.getCode()));
        if (approve) {
            if (approvedMembers.size() < activity.getMinTeamSize() || approvedMembers.size() > activity.getMaxTeamSize()) {
                throw new BusinessException("队伍人数未满足活动要求");
            }
            team.setStatus(TeamStatus.APPROVED.getCode());
            teamMapper.updateById(team);
            approvedMembers.forEach(member -> ensureSignRecord(activity.getId(), member.getUserId()));
            updateApplication(record, ReviewStatus.APPROVED.getCode(), operatorId, comment);
            notificationService.createBatchNotices(
                approvedMembers.stream().map(TeamMember::getUserId).toList(),
                "活动报名审核通过",
                "队伍「" + team.getTeamName() + "」已通过活动「" + activity.getTitle() + "」审核，请按时参加。",
                NotificationType.REVIEW_RESULT.getCode()
            );
        } else {
            team.setStatus(TeamStatus.REJECTED.getCode());
            teamMapper.updateById(team);
            updateApplication(record, ReviewStatus.REJECTED.getCode(), operatorId, comment);
            notificationService.createBatchNotices(
                approvedMembers.stream().map(TeamMember::getUserId).toList(),
                "活动报名未通过",
                "队伍「" + team.getTeamName() + "」未通过活动「" + activity.getTitle() + "」审核，原因：" + defaultComment(comment),
                NotificationType.REVIEW_RESULT.getCode()
            );
        }
    }

    private void validateApplicantNotInAnotherTeam(Long applicantId, Long currentTeamId, Long activityId) {
        List<TeamMember> memberships = teamMemberMapper.selectList(Wrappers.<TeamMember>lambdaQuery()
            .eq(TeamMember::getUserId, applicantId)
            .in(TeamMember::getJoinStatus, List.of(ReviewStatus.PENDING.getCode(), ReviewStatus.APPROVED.getCode())));
        for (TeamMember membership : memberships) {
            if (membership.getTeamId().equals(currentTeamId)) {
                continue;
            }
            Team otherTeam = teamMapper.selectById(membership.getTeamId());
            if (otherTeam != null && otherTeam.getActivityId().equals(activityId)) {
                throw new BusinessException("申请人已在当前活动的其他队伍中");
            }
        }
    }

    private void ensureSignRecord(Long activityId, Long userId) {
        SignRecord record = signRecordMapper.selectOne(Wrappers.<SignRecord>lambdaQuery()
            .eq(SignRecord::getActivityId, activityId)
            .eq(SignRecord::getUserId, userId)
            .last("limit 1"));
        if (record != null) {
            return;
        }
        SignRecord signRecord = new SignRecord();
        signRecord.setActivityId(activityId);
        signRecord.setUserId(userId);
        signRecord.setSignType(SignType.CODE.getCode());
        signRecord.setStatus(SignStatus.UNSIGNED.getCode());
        signRecordMapper.insert(signRecord);
    }

    private ReviewItemVO toReviewItem(ApplicationRecord record) {
        Activity activity = activityMapper.selectById(record.getActivityId());
        Team team = record.getTeamId() == null ? null : teamMapper.selectById(record.getTeamId());
        User applicant = userMapper.selectById(record.getApplicantId());
        int memberCount = team == null ? 0 : teamService.getApprovedMemberCount(team.getId());
        return ReviewItemVO.builder()
            .id(record.getId())
            .type(record.getType())
            .status(record.getStatus())
            .activityId(record.getActivityId())
            .activityTitle(activity == null ? "未知活动" : activity.getTitle())
            .teamId(record.getTeamId())
            .teamName(team == null ? "-" : team.getTeamName())
            .applicantId(record.getApplicantId())
            .applicantName(applicant == null ? "未知用户" : applicant.getNickname())
            .reason(record.getReason())
            .memberCount(memberCount)
            .reviewComment(record.getReviewComment())
            .createdAt(record.getCreatedAt())
            .build();
    }

    private List<Long> resolveVisibleActivityIds(Long userId, String role) {
        if ("admin".equals(role)) {
            return activityMapper.selectList(Wrappers.<Activity>lambdaQuery())
                .stream()
                .map(Activity::getId)
                .toList();
        }
        return activityMapper.selectList(Wrappers.<Activity>lambdaQuery()
                .eq(Activity::getOrganizerId, userId))
            .stream()
            .map(Activity::getId)
            .toList();
    }

    private ApplicationRecord getApplicationOrThrow(Long reviewId) {
        ApplicationRecord record = applicationRecordMapper.selectById(reviewId);
        if (record == null) {
            throw new BusinessException(404, "审核记录不存在");
        }
        return record;
    }

    private void ensurePending(ApplicationRecord record) {
        if (!ReviewStatus.PENDING.getCode().equals(record.getStatus())) {
            throw new BusinessException("当前记录已审核，无需重复操作");
        }
    }

    private void updateApplication(ApplicationRecord record, String status, Long operatorId, String comment) {
        record.setStatus(status);
        record.setReviewedBy(operatorId);
        record.setReviewedAt(LocalDateTime.now());
        record.setReviewComment(comment);
        applicationRecordMapper.updateById(record);
    }

    private String defaultComment(String comment) {
        return comment == null || comment.isBlank() ? "未填写具体原因" : comment;
    }
}
