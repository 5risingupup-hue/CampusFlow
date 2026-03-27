package com.campusflow.security;

import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.campusflow.domain.entity.Role;
import com.campusflow.domain.entity.User;
import com.campusflow.exception.BusinessException;
import com.campusflow.mapper.RoleMapper;
import com.campusflow.mapper.UserMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class CustomUserDetailsService implements UserDetailsService {

    private final UserMapper userMapper;
    private final RoleMapper roleMapper;

    @Override
    public UserPrincipal loadUserByUsername(String username) throws UsernameNotFoundException {
        User user = userMapper.selectOne(Wrappers.<User>lambdaQuery()
            .eq(User::getUsername, username)
            .last("limit 1"));
        if (user == null) {
            throw new UsernameNotFoundException("用户不存在");
        }
        return toPrincipal(user);
    }

    public UserPrincipal loadUserById(Long userId) {
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException(401, "用户不存在");
        }
        return toPrincipal(user);
    }

    private UserPrincipal toPrincipal(User user) {
        Role role = roleMapper.selectById(user.getRoleId());
        return UserPrincipal.builder()
            .id(user.getId())
            .username(user.getUsername())
            .password(user.getPassword())
            .status(user.getStatus())
            .roleName(role == null ? "student" : role.getRoleName())
            .build();
    }
}
