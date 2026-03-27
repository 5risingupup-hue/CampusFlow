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
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    role_desc VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sys_user (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    nickname VARCHAR(50) NOT NULL,
    avatar VARCHAR(255),
    email VARCHAR(100) UNIQUE,
    role_id BIGINT NOT NULL,
    status TINYINT NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_role FOREIGN KEY (role_id) REFERENCES sys_role(id)
);

CREATE TABLE activity (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    cover_url VARCHAR(255),
    description CLOB,
    organizer_id BIGINT NOT NULL,
    type VARCHAR(50) NOT NULL,
    location VARCHAR(255) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    signup_deadline TIMESTAMP NOT NULL,
    require_team BOOLEAN NOT NULL DEFAULT TRUE,
    min_team_size INT DEFAULT 1,
    max_team_size INT DEFAULT 1,
    status VARCHAR(30) NOT NULL DEFAULT 'draft',
    tags VARCHAR(255),
    sign_code VARCHAR(50),
    sign_start_time TIMESTAMP,
    sign_end_time TIMESTAMP,
    result_summary VARCHAR(1000),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_activity_organizer FOREIGN KEY (organizer_id) REFERENCES sys_user(id)
);

CREATE TABLE team (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    activity_id BIGINT NOT NULL,
    team_name VARCHAR(100) NOT NULL,
    leader_id BIGINT NOT NULL,
    slogan VARCHAR(255),
    description CLOB,
    invite_code VARCHAR(50) NOT NULL UNIQUE,
    status VARCHAR(30) NOT NULL DEFAULT 'forming',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_team_activity FOREIGN KEY (activity_id) REFERENCES activity(id),
    CONSTRAINT fk_team_leader FOREIGN KEY (leader_id) REFERENCES sys_user(id),
    CONSTRAINT uk_team_activity_name UNIQUE (activity_id, team_name)
);

CREATE TABLE team_member (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    team_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    member_role VARCHAR(30) NOT NULL DEFAULT 'member',
    join_status VARCHAR(30) NOT NULL DEFAULT 'pending',
    joined_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_team_member_team FOREIGN KEY (team_id) REFERENCES team(id),
    CONSTRAINT fk_team_member_user FOREIGN KEY (user_id) REFERENCES sys_user(id),
    CONSTRAINT uk_team_member UNIQUE (team_id, user_id)
);

CREATE TABLE application_record (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    activity_id BIGINT NOT NULL,
    team_id BIGINT,
    applicant_id BIGINT NOT NULL,
    type VARCHAR(30) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    reason VARCHAR(500),
    reviewed_by BIGINT,
    reviewed_at TIMESTAMP,
    review_comment VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_app_activity FOREIGN KEY (activity_id) REFERENCES activity(id),
    CONSTRAINT fk_app_team FOREIGN KEY (team_id) REFERENCES team(id),
    CONSTRAINT fk_app_applicant FOREIGN KEY (applicant_id) REFERENCES sys_user(id),
    CONSTRAINT fk_app_reviewed_by FOREIGN KEY (reviewed_by) REFERENCES sys_user(id)
);

CREATE TABLE notification (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    title VARCHAR(100) NOT NULL,
    content VARCHAR(1000) NOT NULL,
    type VARCHAR(30) NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notification_user FOREIGN KEY (user_id) REFERENCES sys_user(id)
);

CREATE TABLE sign_record (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    activity_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    sign_type VARCHAR(30) NOT NULL DEFAULT 'code',
    sign_time TIMESTAMP,
    status VARCHAR(30) NOT NULL DEFAULT 'unsigned',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sign_activity FOREIGN KEY (activity_id) REFERENCES activity(id),
    CONSTRAINT fk_sign_user FOREIGN KEY (user_id) REFERENCES sys_user(id),
    CONSTRAINT uk_sign_activity_user UNIQUE (activity_id, user_id)
);

CREATE TABLE feedback (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    activity_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    score INT NOT NULL,
    content VARCHAR(1000),
    tags VARCHAR(255),
    willing_rejoin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_feedback_activity FOREIGN KEY (activity_id) REFERENCES activity(id),
    CONSTRAINT fk_feedback_user FOREIGN KEY (user_id) REFERENCES sys_user(id),
    CONSTRAINT uk_feedback_activity_user UNIQUE (activity_id, user_id)
);

CREATE TABLE announcement (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    content VARCHAR(2000) NOT NULL,
    created_by BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_announcement_user FOREIGN KEY (created_by) REFERENCES sys_user(id)
);
