package com.campusflow.domain.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class UpdateProfileRequest {

    @NotBlank(message = "昵称不能为空")
    private String nickname;

    private String avatar;

    @Email(message = "邮箱格式不正确")
    private String email;
}
