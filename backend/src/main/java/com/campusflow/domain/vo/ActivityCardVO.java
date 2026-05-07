package com.campusflow.domain.vo;

import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

@Data
@Builder
public class ActivityCardVO {

    private Long id;
    private String title;
    private String coverUrl;
    private String organizerName;
    private String type;
    private String location;
    private LocalDateTime startTime;
    private LocalDateTime signupDeadline;
    private Boolean requireTeam;
    private String status;
    private List<String> tags;
}
