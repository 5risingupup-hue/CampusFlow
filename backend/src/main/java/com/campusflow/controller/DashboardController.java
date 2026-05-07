package com.campusflow.controller;

import com.campusflow.common.ApiResponse;
import com.campusflow.domain.vo.DashboardOverviewVO;
import com.campusflow.service.DashboardService;
import com.campusflow.support.SecurityUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/dashboard")
@RequiredArgsConstructor
public class DashboardController {

    private final DashboardService dashboardService;

    @GetMapping("/overview")
    public ApiResponse<DashboardOverviewVO> overview() {
        return ApiResponse.success("查询成功", dashboardService.overview(
            SecurityUtils.getCurrentUserId(),
            SecurityUtils.getCurrentRole()
        ));
    }
}
