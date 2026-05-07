# 一、数据库建表 SQL

下面这套 SQL 以 **MySQL 8.0** 为基础，覆盖你们项目的核心业务表：

- 角色表 `sys_role`
- 用户表 `sys_user`
- 活动表 `activity`
- 队伍表 `team`
- 队伍成员表 `team_member`
- 申请/报名表 `application_record`
- 通知表 `notification`
- 签到记录表 `sign_record`
- 反馈表 `feedback`
- 公告表 `announcement`

我把字段、索引、唯一约束、外键关系都补上了。

------

## 1）创建数据库

```
CREATE DATABASE IF NOT EXISTS campusflow
DEFAULT CHARACTER SET utf8mb4
DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE campusflow;
```

------

## 2）角色表

```
DROP TABLE IF EXISTS sys_role;
CREATE TABLE sys_role (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '角色ID',
    role_name VARCHAR(50) NOT NULL UNIQUE COMMENT '角色名称，如student、captain、organizer、admin',
    role_desc VARCHAR(255) DEFAULT NULL COMMENT '角色描述',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色表';
```

------

## 3）用户表

```
DROP TABLE IF EXISTS sys_user;
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
```

------

## 4）活动表

```
DROP TABLE IF EXISTS activity;
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
    require_team TINYINT NOT NULL DEFAULT 1 COMMENT '是否需要组队：1是 0否',
    min_team_size INT DEFAULT 1 COMMENT '最小队伍人数',
    max_team_size INT DEFAULT 1 COMMENT '最大队伍人数',
    status VARCHAR(30) NOT NULL DEFAULT 'draft' COMMENT '状态：draft/published/signup_open/signup_closed/finished/cancelled',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT fk_activity_organizer FOREIGN KEY (organizer_id) REFERENCES sys_user(id),
    INDEX idx_activity_title_status_deadline (title, status, signup_deadline),
    INDEX idx_activity_organizer (organizer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='活动表';
```

------

## 5）队伍表

```
DROP TABLE IF EXISTS team;
CREATE TABLE team (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '队伍ID',
    activity_id BIGINT NOT NULL COMMENT '所属活动ID',
    team_name VARCHAR(100) NOT NULL COMMENT '队伍名称',
    leader_id BIGINT NOT NULL COMMENT '队长ID',
    slogan VARCHAR(255) DEFAULT NULL COMMENT '队伍口号',
    description TEXT COMMENT '队伍简介',
    invite_code VARCHAR(50) NOT NULL UNIQUE COMMENT '邀请码',
    status VARCHAR(30) NOT NULL DEFAULT 'forming' COMMENT '状态：forming/submitted/approved/rejected/disbanded',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT fk_team_activity FOREIGN KEY (activity_id) REFERENCES activity(id),
    CONSTRAINT fk_team_leader FOREIGN KEY (leader_id) REFERENCES sys_user(id),
    CONSTRAINT uk_team_activity_name UNIQUE (activity_id, team_name),
    INDEX idx_team_activity_leader (activity_id, leader_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='队伍表';
```

------

## 6）队伍成员表

```
DROP TABLE IF EXISTS team_member;
CREATE TABLE team_member (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '成员记录ID',
    team_id BIGINT NOT NULL COMMENT '队伍ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    member_role VARCHAR(30) NOT NULL DEFAULT 'member' COMMENT '成员角色：leader/member',
    join_status VARCHAR(30) NOT NULL DEFAULT 'pending' COMMENT '加入状态：pending/approved/rejected',
    joined_at DATETIME DEFAULT NULL COMMENT '加入时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT fk_team_member_team FOREIGN KEY (team_id) REFERENCES team(id),
    CONSTRAINT fk_team_member_user FOREIGN KEY (user_id) REFERENCES sys_user(id),
    CONSTRAINT uk_team_member UNIQUE (team_id, user_id),
    INDEX idx_team_member_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='队伍成员表';
```

------

## 7）申请/报名表

这里统一记录两类申请：

- `join_team`：申请加入队伍
- `signup_team`：队伍正式报名
- `signup_personal`：个人活动报名

```
DROP TABLE IF EXISTS application_record;
CREATE TABLE application_record (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '申请记录ID',
    activity_id BIGINT NOT NULL COMMENT '活动ID',
    team_id BIGINT DEFAULT NULL COMMENT '队伍ID，可为空',
    applicant_id BIGINT NOT NULL COMMENT '申请人ID',
    type VARCHAR(30) NOT NULL COMMENT '申请类型：join_team/signup_team/signup_personal',
    status VARCHAR(30) NOT NULL DEFAULT 'pending' COMMENT '状态：pending/approved/rejected',
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
```

------

## 8）通知表

```
DROP TABLE IF EXISTS notification;
CREATE TABLE notification (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '通知ID',
    user_id BIGINT NOT NULL COMMENT '接收用户ID',
    title VARCHAR(100) NOT NULL COMMENT '通知标题',
    content VARCHAR(1000) NOT NULL COMMENT '通知内容',
    type VARCHAR(30) NOT NULL COMMENT '通知类型：review_result/activity_reminder/system/team_apply',
    is_read TINYINT NOT NULL DEFAULT 0 COMMENT '是否已读：0未读 1已读',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT fk_notification_user FOREIGN KEY (user_id) REFERENCES sys_user(id),
    INDEX idx_notice_user_read (user_id, is_read)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='通知表';
```

------

## 9）签到记录表

```
DROP TABLE IF EXISTS sign_record;
CREATE TABLE sign_record (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '签到记录ID',
    activity_id BIGINT NOT NULL COMMENT '活动ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    sign_type VARCHAR(30) NOT NULL DEFAULT 'code' COMMENT '签到方式：code/qrcode',
    sign_time DATETIME DEFAULT NULL COMMENT '签到时间',
    status VARCHAR(30) NOT NULL DEFAULT 'unsigned' COMMENT '状态：unsigned/signed/expired',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT fk_sign_activity FOREIGN KEY (activity_id) REFERENCES activity(id),
    CONSTRAINT fk_sign_user FOREIGN KEY (user_id) REFERENCES sys_user(id),
    CONSTRAINT uk_sign_activity_user UNIQUE (activity_id, user_id),
    INDEX idx_sign_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='签到记录表';
```

------

## 10）反馈表

```
DROP TABLE IF EXISTS feedback;
CREATE TABLE feedback (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '反馈ID',
    activity_id BIGINT NOT NULL COMMENT '活动ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    score INT NOT NULL COMMENT '评分，1~5',
    content VARCHAR(1000) DEFAULT NULL COMMENT '反馈内容',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT fk_feedback_activity FOREIGN KEY (activity_id) REFERENCES activity(id),
    CONSTRAINT fk_feedback_user FOREIGN KEY (user_id) REFERENCES sys_user(id),
    CONSTRAINT uk_feedback_activity_user UNIQUE (activity_id, user_id),
    INDEX idx_feedback_activity_user (activity_id, user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='反馈表';
```

------

## 11）公告表

```
DROP TABLE IF EXISTS announcement;
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
```

------

## 12）初始化角色数据

```
INSERT INTO sys_role (role_name, role_desc) VALUES
('student', '普通学生用户'),
('captain', '队长'),
('organizer', '活动组织者'),
('admin', '系统管理员');
```

------

## 13）初始化测试用户数据（可选）

注意：这里密码只是演示，实际项目里应保存加密后的密码。

```
INSERT INTO sys_user (username, password, nickname, email, role_id, status) VALUES
('student01', '123456', 'Alice', 'alice@example.com', 1, 1),
('captain01', '123456', 'Bob', 'bob@example.com', 2, 1),
('organizer01', '123456', 'Cindy', 'cindy@example.com', 3, 1),
('admin01', '123456', 'David', 'david@example.com', 4, 1);
```

------

## 14）课程项目可选增强字段

如果你们后面还想让设计更“像正式项目”，可以再加：

- 逻辑删除字段 `deleted`
- 乐观锁字段 `version`
- 创建人 / 修改人
- 活动标签表、活动图片表
- 消息模板表
- 操作日志表

但就课程项目而言，上面这套已经够完整了。

------

# 二、可直接放进报告的“系统总体设计”章节

下面这部分我按课程报告的风格写，你可以直接放进文档里，标题都给你排好了。

------

# 第 X 章 系统总体设计

## 1. 系统设计目标

CampusFlow 是一个面向校园活动场景的活动组队与报名协作平台，系统围绕“活动发现—组队协作—报名审核—消息通知—签到—反馈”构建完整业务闭环。系统总体设计的目标主要包括以下几个方面：

第一，满足校园活动平台在活动展示、组队报名、审核管理、签到反馈等方面的核心业务需求。
 第二，采用前后端分离架构，提高系统的可维护性、扩展性和开发效率。
 第三，在保证系统功能完整的基础上，兼顾用户体验、权限控制和业务流程清晰性。
 第四，结合 Scrum 敏捷开发思想，将系统划分为若干模块，便于进行迭代开发、测试和后续优化。

因此，本系统不仅强调功能实现，还强调系统结构清晰、业务流程完整以及后续扩展能力。

------

## 2. 系统总体架构设计

CampusFlow 采用典型的前后端分离架构，整体由前端表示层、后端业务层、数据存储层和消息交互层四部分组成。

### 2.1 前端表示层

前端主要负责页面渲染、用户交互、表单校验、状态管理和接口调用。系统前端采用 Vue 3 + TypeScript + Vite 构建，通过 Vue Router 管理路由，Pinia 管理全局状态，Element Plus 作为主要 UI 组件库。
 前端根据不同角色展示不同功能入口，并通过组件化设计提高页面复用性和开发效率。

### 2.2 后端业务层

后端主要负责业务逻辑处理、权限认证、数据校验、消息通知和流程控制。系统后端采用 Spring Boot 作为核心开发框架，通过 Spring MVC 实现 RESTful API，通过 Spring Security + JWT 实现身份认证与权限控制，通过 MyBatis-Plus 实现数据库访问。
 后端按照 Controller、Service、Mapper、Entity 的分层模式组织代码，以提高系统的可读性和可维护性。

### 2.3 数据存储层

系统采用 MySQL 存储核心业务数据，包括用户、活动、队伍、报名、通知、签到与反馈等数据。
 同时，可通过 Redis 对热门活动列表、未读消息数、签到状态等高频访问数据进行缓存，以提升系统响应性能。

### 2.4 消息交互层

系统通过 WebSocket 或轮询机制实现消息实时通知，用于支持报名审核结果通知、活动提醒、入队申请提醒等业务场景。
 对于普通系统公告和消息记录，统一存储于通知表中。

综上，系统总体架构如图所示，可概括为：
 **前端页面层 → 后端业务层 → 数据库与缓存层 → 实时消息层**。

------

## 3. 系统功能模块设计

根据系统业务需求，CampusFlow 可划分为以下几个核心模块：

### 3.1 用户与权限模块

该模块负责用户登录、用户信息管理以及权限校验。系统定义了学生、队长、活动组织者和管理员四类角色，不同角色对应不同功能边界。
 学生主要负责浏览活动、加入队伍和参与签到；队长除普通学生功能外，还可管理队伍成员与提交报名；组织者负责审核报名、管理活动；管理员负责公告管理与平台治理。

### 3.2 活动管理模块

该模块主要用于活动信息的发布、展示与查询。组织者可以创建活动、配置活动类型、活动时间、地点、是否需要组队、报名截止时间等信息；学生则可通过首页浏览活动、筛选活动、查看活动详情。
 活动管理模块是系统业务流程的起点，也是用户进入系统的主要入口。

### 3.3 队伍协作模块

该模块是本系统区别于普通活动展示平台的关键模块。学生可围绕活动创建队伍、申请加入队伍、接受邀请，并由队长统一管理队伍信息和成员状态。
 通过该模块，系统实现了从“个人浏览活动”到“团队协作报名”的转化，体现出项目的协作型特征。

### 3.4 报名审核模块

该模块负责个人/队伍报名申请的提交与审核。队长可代表队伍提交报名申请，组织者可查看报名信息、审核材料并给出通过或驳回结果。
 审核结果将自动同步至通知模块，保证信息传递的及时性和闭环性。

### 3.5 通知消息模块

该模块主要负责向用户推送系统公告、报名审核结果、活动提醒和入队申请处理结果等信息。
 系统通过消息列表、未读数、小红点提醒等方式提升用户对关键信息的感知效率。

### 3.6 活动签到模块

该模块主要用于活动现场签到。参与者可通过签到码或二维码方式进行签到，系统记录签到时间和签到状态，并防止重复签到。
 签到模块保证了活动组织流程由线上报名延伸到线下参与，提高平台的完整性。

### 3.7 反馈评价模块

该模块主要用于活动结束后的评价与反馈收集。用户可对活动进行星级评分并提交文字建议，组织者则可以通过反馈数据了解活动体验并改进后续活动设计。
 反馈模块使系统形成“活动前—活动中—活动后”的全生命周期闭环。

### 3.8 平台治理模块

该模块由管理员使用，主要负责系统公告发布、活动分类维护、违规报名处理等。
 通过治理模块，系统具备了一定的后台管理能力，也使项目更符合实际应用场景。

------

## 4. 系统角色与权限设计

系统采用基于角色的访问控制模型（RBAC），通过角色区分不同用户可访问的菜单、页面和接口权限。

### 4.1 学生

学生是平台最主要的使用者，可进行活动浏览、活动详情查看、创建队伍、加入队伍、签到和反馈等操作。

### 4.2 队长

队长本质上也是学生，但在特定活动中承担队伍管理职责。队长拥有邀请成员、审批入队申请、提交报名等扩展权限。

### 4.3 活动组织者

活动组织者主要负责活动发布、报名审核、活动通知和签到管理，是活动运行过程中的核心管理角色。

### 4.4 管理员

管理员负责公告管理、平台规则维护和异常情况处理，保证平台稳定运行和秩序管理。

通过 RBAC 权限模型，系统可以在保证功能清晰的同时，避免越权操作，提高系统安全性与业务规范性。

------

## 5. 系统业务流程设计

CampusFlow 的核心业务流程为：

**活动发布 → 活动发现 → 创建队伍/加入队伍 → 提交报名 → 组织者审核 → 结果通知 → 活动签到 → 反馈评价**

具体说明如下：

1. 活动组织者创建并发布活动，设置活动规则和报名条件。
2. 学生在首页浏览活动，进入活动详情后判断是否参与。
3. 若活动要求组队，学生可选择创建队伍或申请加入已有队伍。
4. 队伍组建完成后，由队长统一提交报名申请。
5. 活动组织者对报名申请进行审核，并返回通过或驳回结果。
6. 审核结果通过通知模块推送给相关用户。
7. 活动开始后，参与者通过签到模块完成签到。
8. 活动结束后，用户可对活动进行评价反馈，形成业务闭环。

该业务流程体现了系统从“信息展示”到“协作报名”再到“活动执行与复盘”的全过程管理能力。

------

## 6. 数据库总体设计

数据库设计以活动为核心实体，以队伍协作与报名审核为主线，建立了用户、角色、活动、队伍、队伍成员、申请记录、通知、签到记录、反馈和公告等主要数据表。

其中：

- `sys_user` 与 `sys_role` 用于实现用户与角色管理；
- `activity` 用于存储活动信息；
- `team` 与 `team_member` 用于实现队伍协作；
- `application_record` 用于记录入队申请与报名申请；
- `notification` 用于承载系统通知和业务通知；
- `sign_record` 用于记录用户签到状态；
- `feedback` 用于存储活动评价数据；
- `announcement` 用于平台公告管理。

该数据库结构能够较好地支撑本系统的核心业务，并具备后续功能扩展能力。

------

## 7. 系统接口设计原则

为了保证前后端协作效率，系统后端接口采用 RESTful 风格设计，统一使用 JSON 作为数据交换格式。接口设计遵循以下原则：

1. 接口命名规范清晰，能够准确表达资源含义。
2. 使用统一响应结构，便于前端解析。
3. 对输入参数进行校验，并返回明确的错误信息。
4. 关键接口需进行权限校验和业务规则校验。
5. 审核、签到、反馈等关键操作应考虑幂等性与异常处理。

系统统一响应格式如下：

```
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

通过统一接口规范，可降低前后端联调成本，提高项目实现效率。

------

## 8. 系统非功能设计

除功能需求外，系统还应满足一定的非功能要求。

### 8.1 可用性

页面布局应清晰、交互操作应直观，用户能够在较少学习成本下完成活动浏览、队伍管理和报名操作。

### 8.2 安全性

系统应采用 JWT 鉴权机制，密码使用加密存储，对关键接口进行权限控制，并对敏感操作记录日志。

### 8.3 可维护性

系统前后端均采用分层设计和模块化开发方式，降低代码耦合度，便于后续功能扩展和缺陷修复。

### 8.4 可扩展性

数据库结构和模块划分预留了扩展空间，后续可进一步增加活动标签、排行榜、推荐算法、小程序端等功能。

### 8.5 性能

对于活动列表、消息未读数等高频访问数据，可引入 Redis 缓存优化查询性能；对于签到等操作，可通过幂等控制避免重复写入。

------

## 9. 系统部署设计

在课程项目阶段，系统可采用如下部署方式：

- 前端部署于本地开发服务器或 Nginx 静态资源服务器；
- 后端部署于 Spring Boot 应用服务；
- MySQL 作为核心数据库；
- Redis 作为可选缓存服务；
- 文件资源可暂存于本地或对象存储服务。

开发阶段采用本地环境进行联调，正式演示时可通过服务器统一部署，保证系统完整可运行。

------

## 10. 本章小结

本章从系统目标、总体架构、功能模块、角色权限、业务流程、数据库设计、接口设计和非功能设计等方面对 CampusFlow 进行了总体设计。
 通过前后端分离架构、模块化设计和 RBAC 权限模型，本系统能够较好地支撑校园活动组队与报名协作场景，并为后续的详细设计、编码实现和测试验收提供明确依据。
