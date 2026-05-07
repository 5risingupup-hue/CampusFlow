package com.campusflow.domain.vo;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class TeamListItemVO {

    private Long id;
    private Long activityId;
    private String activityTitle;
    private String teamName;
    private String slogan;
    private String description;
    private String inviteCode;
    private Long leaderId;
    private String leaderName;
    private Integer currentSize;
    private Integer maxTeamSize;
    private String status;
    private Boolean applied;
    private Boolean joined;
    private Boolean canApply;
}
