package com.campusflow.service;

import com.campusflow.domain.dto.LoginRequest;
import com.campusflow.domain.entity.Role;
import com.campusflow.domain.entity.User;
import com.campusflow.domain.vo.LoginResponse;
import com.campusflow.domain.vo.UserProfileVO;
import com.campusflow.mapper.RoleMapper;
import com.campusflow.mapper.UserMapper;
import com.campusflow.security.JwtTokenProvider;
import com.campusflow.security.UserPrincipal;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final AuthenticationManager authenticationManager;
    private final JwtTokenProvider jwtTokenProvider;
    private final UserMapper userMapper;
    private final RoleMapper roleMapper;

    public LoginResponse login(LoginRequest request) {
        Authentication authentication = authenticationManager.authenticate(
            new UsernamePasswordAuthenticationToken(request.getUsername(), request.getPassword())
        );
        UserPrincipal principal = (UserPrincipal) authentication.getPrincipal();
        User user = userMapper.selectById(principal.getId());
        Role role = roleMapper.selectById(user.getRoleId());
        return LoginResponse.builder()
            .token(jwtTokenProvider.generateToken(authentication))
            .userInfo(UserProfileVO.builder()
                .id(user.getId())
                .username(user.getUsername())
                .nickname(user.getNickname())
                .avatar(user.getAvatar())
                .email(user.getEmail())
                .role(role == null ? "student" : role.getRoleName())
                .build())
            .build();
    }
}
