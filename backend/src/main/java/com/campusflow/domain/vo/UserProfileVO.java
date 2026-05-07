package com.campusflow.domain.vo;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class UserProfileVO {

    private Long id;
    private String username;
    private String nickname;
    private String avatar;
    private String email;
    private String role;
}
