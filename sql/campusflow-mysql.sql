CREATE DATABASE IF NOT EXISTS campusflow
DEFAULT CHARACTER SET utf8mb4
DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE campusflow;

DROP TABLE IF EXISTS announcement;
DROP TABLE IF EXISTS feedback;
DROP TABLE IF EXISTS sign_record;
DROP TABLE IF EXISTS notification;
DROP TABLE IF EXISTS application_record;
DROP TABLE IF EXISTS team_member;
DROP TABLE IF EXISTS team;
DROP TABLE IF EXISTS activity;
DROP TABLE IF EXISTS sys_user;
DROP TABLE IF EXISTS sys_role;

CREATE TABLE sys_role (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '角色ID',
    role_name VARCHAR(50) NOT NULL UNIQUE COMMENT '角色名称',
    role_desc VARCHAR(255) DEFAULT NULL COMMENT '角色描述',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色表';

CREATE TABLE sys_user (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '加密密码',
    nickname VARCHAR(50) NOT NULL COMMENT '昵称',
    avatar VARCHAR(255) DEFAULT NULL COMMENT '头像地址',
    email VARCHAR(100) DEFAULT NULL UNIQUE COMMENT '邮箱',
    role_id BIGINT NOT NULL COMMENT '角色ID',
    status TINYINT NOT NULL DEFAULT 1 COMMENT '状态：1正常 0禁用',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT fk_user_role FOREIGN KEY (role_id) REFERENCES sys_role(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

CREATE TABLE activity (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '活动ID',
    title VARCHAR(100) NOT NULL COMMENT '活动标题',
    cover_url VARCHAR(255) DEFAULT NULL COMMENT '活动封面',
    description TEXT COMMENT '活动描述',
    organizer_id BIGINT NOT NULL COMMENT '组织者ID',
    type VARCHAR(50) NOT NULL COMMENT '活动类型',
    location VARCHAR(255) NOT NULL COMMENT '活动地点',
    start_time DATETIME NOT NULL COMMENT '活动开始时间',
    end_time DATETIME NOT NULL COMMENT '活动结束时间',
    signup_deadline DATETIME NOT NULL COMMENT '报名截止时间',
    require_team TINYINT NOT NULL DEFAULT 1 COMMENT '是否需要组队',
    min_team_size INT DEFAULT 1 COMMENT '最小队伍人数',
    max_team_size INT DEFAULT 1 COMMENT '最大队伍人数',
    status VARCHAR(30) NOT NULL DEFAULT 'draft' COMMENT '活动状态',
    tags VARCHAR(255) DEFAULT NULL COMMENT '标签，逗号分隔',
    sign_code VARCHAR(50) DEFAULT NULL COMMENT '签到码',
    sign_start_time DATETIME DEFAULT NULL COMMENT '签到开始时间',
    sign_end_time DATETIME DEFAULT NULL COMMENT '签到结束时间',
    result_summary VARCHAR(1000) DEFAULT NULL COMMENT '活动结果总结',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT fk_activity_organizer FOREIGN KEY (organizer_id) REFERENCES sys_user(id),
    INDEX idx_activity_title_status_deadline (title, status, signup_deadline),
    INDEX idx_activity_organizer (organizer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='活动表';

CREATE TABLE team (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '队伍ID',
    activity_id BIGINT NOT NULL COMMENT '所属活动ID',
    team_name VARCHAR(100) NOT NULL COMMENT '队伍名称',
    leader_id BIGINT NOT NULL COMMENT '队长ID',
    slogan VARCHAR(255) DEFAULT NULL COMMENT '队伍口号',
    description TEXT COMMENT '队伍简介',
    invite_code VARCHAR(50) NOT NULL UNIQUE COMMENT '邀请码',
    status VARCHAR(30) NOT NULL DEFAULT 'forming' COMMENT '状态',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT fk_team_activity FOREIGN KEY (activity_id) REFERENCES activity(id),
    CONSTRAINT fk_team_leader FOREIGN KEY (leader_id) REFERENCES sys_user(id),
    CONSTRAINT uk_team_activity_name UNIQUE (activity_id, team_name),
    INDEX idx_team_activity_leader (activity_id, leader_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='队伍表';

CREATE TABLE team_member (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '成员记录ID',
    team_id BIGINT NOT NULL COMMENT '队伍ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    member_role VARCHAR(30) NOT NULL DEFAULT 'member' COMMENT '成员角色',
    join_status VARCHAR(30) NOT NULL DEFAULT 'pending' COMMENT '加入状态',
    joined_at DATETIME DEFAULT NULL COMMENT '加入时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT fk_team_member_team FOREIGN KEY (team_id) REFERENCES team(id),
    CONSTRAINT fk_team_member_user FOREIGN KEY (user_id) REFERENCES sys_user(id),
    CONSTRAINT uk_team_member UNIQUE (team_id, user_id),
    INDEX idx_team_member_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='队伍成员表';

CREATE TABLE application_record (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '申请记录ID',
    activity_id BIGINT NOT NULL COMMENT '活动ID',
    team_id BIGINT DEFAULT NULL COMMENT '队伍ID',
    applicant_id BIGINT NOT NULL COMMENT '申请人ID',
    type VARCHAR(30) NOT NULL COMMENT '申请类型',
    status VARCHAR(30) NOT NULL DEFAULT 'pending' COMMENT '审核状态',
    reason VARCHAR(500) DEFAULT NULL COMMENT '申请理由',
    reviewed_by BIGINT DEFAULT NULL COMMENT '审核人ID',
    reviewed_at DATETIME DEFAULT NULL COMMENT '审核时间',
    review_comment VARCHAR(500) DEFAULT NULL COMMENT '审核备注',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT fk_app_activity FOREIGN KEY (activity_id) REFERENCES activity(id),
    CONSTRAINT fk_app_team FOREIGN KEY (team_id) REFERENCES team(id),
    CONSTRAINT fk_app_applicant FOREIGN KEY (applicant_id) REFERENCES sys_user(id),
    CONSTRAINT fk_app_reviewed_by FOREIGN KEY (reviewed_by) REFERENCES sys_user(id),
    INDEX idx_app_activity_status_type (activity_id, status, type),
    INDEX idx_app_team (team_id),
    INDEX idx_app_applicant (applicant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='申请/报名记录表';

CREATE TABLE notification (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '通知ID',
    user_id BIGINT NOT NULL COMMENT '接收用户ID',
    title VARCHAR(100) NOT NULL COMMENT '通知标题',
    content VARCHAR(1000) NOT NULL COMMENT '通知内容',
    type VARCHAR(30) NOT NULL COMMENT '通知类型',
    is_read TINYINT NOT NULL DEFAULT 0 COMMENT '是否已读',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT fk_notification_user FOREIGN KEY (user_id) REFERENCES sys_user(id),
    INDEX idx_notice_user_read (user_id, is_read)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='通知表';

CREATE TABLE sign_record (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '签到记录ID',
    activity_id BIGINT NOT NULL COMMENT '活动ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    sign_type VARCHAR(30) NOT NULL DEFAULT 'code' COMMENT '签到方式',
    sign_time DATETIME DEFAULT NULL COMMENT '签到时间',
    status VARCHAR(30) NOT NULL DEFAULT 'unsigned' COMMENT '签到状态',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT fk_sign_activity FOREIGN KEY (activity_id) REFERENCES activity(id),
    CONSTRAINT fk_sign_user FOREIGN KEY (user_id) REFERENCES sys_user(id),
    CONSTRAINT uk_sign_activity_user UNIQUE (activity_id, user_id),
    INDEX idx_sign_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='签到记录表';

CREATE TABLE feedback (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '反馈ID',
    activity_id BIGINT NOT NULL COMMENT '活动ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    score INT NOT NULL COMMENT '评分',
    content VARCHAR(1000) DEFAULT NULL COMMENT '反馈内容',
    tags VARCHAR(255) DEFAULT NULL COMMENT '反馈标签',
    willing_rejoin TINYINT DEFAULT 0 COMMENT '是否愿意再次参加',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT fk_feedback_activity FOREIGN KEY (activity_id) REFERENCES activity(id),
    CONSTRAINT fk_feedback_user FOREIGN KEY (user_id) REFERENCES sys_user(id),
    CONSTRAINT uk_feedback_activity_user UNIQUE (activity_id, user_id),
    INDEX idx_feedback_activity_user (activity_id, user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='反馈表';

CREATE TABLE announcement (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '公告ID',
    title VARCHAR(100) NOT NULL COMMENT '公告标题',
    content VARCHAR(2000) NOT NULL COMMENT '公告内容',
    created_by BIGINT NOT NULL COMMENT '创建人ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT fk_announcement_user FOREIGN KEY (created_by) REFERENCES sys_user(id),
    INDEX idx_announcement_creator (created_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='公告表';
