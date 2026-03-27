package com.campusflow.domain.vo;

import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

@Data
@Builder
public class ActivityDetailVO {

    private Long id;
    private String title;
    private String coverUrl;
    private String description;
    private String organizerName;
    private Long organizerId;
    private String type;
    private String location;
    private LocalDateTime startTime;
    private LocalDateTime endTime;
    private LocalDateTime signupDeadline;
    private Boolean requireTeam;
    private Integer minTeamSize;
    private Integer maxTeamSize;
    private String status;
    private List<String> tags;
    private Integer teamCount;
    private Long myTeamId;
    private String myApplicationStatus;
    private Boolean canCreateTeam;
    private Boolean canApplyTeam;
    private Boolean canSignIn;
    private Boolean canFeedback;
    private String resultSummary;
}
