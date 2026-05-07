package com.campusflow.domain.vo;

import lombok.Builder;
import lombok.Data;

import java.util.List;

@Data
@Builder
public class TeamDetailVO {

    private Long id;
    private Long activityId;
    private String activityTitle;
    private String teamName;
    private Long leaderId;
    private String leaderName;
    private String slogan;
    private String description;
    private String inviteCode;
    private String status;
    private Integer currentSize;
    private Integer minTeamSize;
    private Integer maxTeamSize;
    private Boolean canManage;
    private List<TeamMemberVO> members;
    private List<ApplicationRecordVO> pendingApplications;
}
