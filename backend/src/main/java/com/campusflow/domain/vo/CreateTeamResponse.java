package com.campusflow.domain.vo;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class CreateTeamResponse {

    private Long teamId;
    private String inviteCode;
}
