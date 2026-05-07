package com.campusflow.domain.vo;

import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@Builder
public class TeamMemberVO {

    private Long userId;
    private String nickname;
    private String avatar;
    private String memberRole;
    private String joinStatus;
    private LocalDateTime joinedAt;
}
