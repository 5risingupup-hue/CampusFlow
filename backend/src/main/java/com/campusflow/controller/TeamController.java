package com.campusflow.controller;

import com.campusflow.common.ApiResponse;
import com.campusflow.common.PageResult;
import com.campusflow.domain.dto.CreateTeamRequest;
import com.campusflow.domain.dto.JoinTeamRequest;
import com.campusflow.domain.dto.SubmitTeamRequest;
import com.campusflow.domain.dto.TeamQueryRequest;
import com.campusflow.domain.vo.CreateTeamResponse;
import com.campusflow.domain.vo.TeamDetailVO;
import com.campusflow.domain.vo.TeamListItemVO;
import com.campusflow.service.TeamService;
import com.campusflow.support.SecurityUtils;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/teams")
@RequiredArgsConstructor
public class TeamController {

    private final TeamService teamService;

    @PostMapping
    public ApiResponse<CreateTeamResponse> create(@Valid @RequestBody CreateTeamRequest request) {
        return ApiResponse.success("创建成功", teamService.create(SecurityUtils.getCurrentUserId(), request));
    }

    @GetMapping("/joinable")
    public ApiResponse<PageResult<TeamListItemVO>> joinable(@ModelAttribute TeamQueryRequest request) {
        return ApiResponse.success("查询成功", teamService.listJoinable(SecurityUtils.getCurrentUserId(), request));
    }

    @GetMapping("/{id}")
    public ApiResponse<TeamDetailVO> detail(@PathVariable Long id) {
        return ApiResponse.success("查询成功", teamService.getDetail(id, SecurityUtils.getCurrentUserId()));
    }

    @PostMapping("/{id}/apply")
    public ApiResponse<Void> apply(@PathVariable Long id, @RequestBody(required = false) JoinTeamRequest request) {
        teamService.applyToJoin(SecurityUtils.getCurrentUserId(), id, request == null ? null : request.getReason());
        return ApiResponse.success("申请已提交", null);
    }

    @PostMapping("/{id}/submit")
    public ApiResponse<Void> submit(@PathVariable Long id, @RequestBody(required = false) SubmitTeamRequest request) {
        teamService.submit(SecurityUtils.getCurrentUserId(), id, request);
        return ApiResponse.success("报名已提交", null);
    }
}
