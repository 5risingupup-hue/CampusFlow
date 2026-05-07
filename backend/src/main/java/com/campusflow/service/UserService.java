package com.campusflow.service;

import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.campusflow.domain.dto.UpdateProfileRequest;
import com.campusflow.domain.entity.Role;
import com.campusflow.domain.entity.User;
import com.campusflow.domain.vo.UserProfileVO;
import com.campusflow.exception.BusinessException;
import com.campusflow.mapper.RoleMapper;
import com.campusflow.mapper.UserMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserMapper userMapper;
    private final RoleMapper roleMapper;

    public UserProfileVO getProfile(Long userId) {
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException(404, "用户不存在");
        }
        Role role = roleMapper.selectById(user.getRoleId());
        return UserProfileVO.builder()
            .id(user.getId())
            .username(user.getUsername())
            .nickname(user.getNickname())
            .avatar(user.getAvatar())
            .email(user.getEmail())
            .role(role == null ? "student" : role.getRoleName())
            .build();
    }

    @Transactional
    public UserProfileVO updateProfile(Long userId, UpdateProfileRequest request) {
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException(404, "用户不存在");
        }
        if (request.getEmail() != null) {
            User existing = userMapper.selectOne(Wrappers.<User>lambdaQuery()
                .eq(User::getEmail, request.getEmail())
                .ne(User::getId, userId)
                .last("limit 1"));
            if (existing != null) {
                throw new BusinessException(409, "邮箱已被占用");
            }
        }
        user.setNickname(request.getNickname());
        user.setAvatar(request.getAvatar());
        user.setEmail(request.getEmail());
        userMapper.updateById(user);
        return getProfile(userId);
    }
}
