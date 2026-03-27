# CampusFlow

CampusFlow 是一个面向校园活动场景的前后端分离课程项目，
围绕“活动发现 -> 组队协作 -> 提交报名 -> 组织者审核 -> 消息通知 -> 活动签到 -> 结果反馈”实现完整闭环。

本项目包含：

- `backend`：Spring Boot + Spring Security + JWT + MyBatis-Plus 后端
- `frontend`：Vue 3 + TypeScript + Vite + Pinia + Element Plus 前端
- `sql`：MySQL 建表脚本
- `docs`：可继续放实验报告、接口补充说明或答辩材料

## 已实现模块

- 用户登录、JWT 鉴权、个人资料查看/修改
- 活动列表、活动详情、组织者活动管理
- 创建队伍、加入队伍、队伍详情、队长提交报名
- 组织者审核报名、队长审核入队申请
- 通知列表、未读数统计、WebSocket 实时通知
- 活动签到、签到状态查询
- 活动反馈与历史评分展示
- 管理员公告发布与全站通知
- 概览页数据统计与 ECharts 图表展示

## 目录结构

```text
lab2/
├── backend/                 # Spring Boot 后端
├── frontend/                # Vue 3 前端
├── sql/
│   └── campusflow-mysql.sql # MySQL 建表脚本
├── docs/
├── CampusFlow 开发方案.md
├── 前后端设计说明+接口文档模板.md
├── 数据库建表 SQL&系统总体设计.md
└── README.md
```

## 环境要求

建议按下面版本准备环境：

- `JDK 21`
- `Maven 3.9+`
- `Node.js 20+` 或 `Node.js 24`
- `npm 10+`
- `MySQL 8.0`（可选，默认演示模式不强依赖）

## 一、最快启动方式：H2 演示模式

后端默认使用内存数据库 H2，并在启动时自动初始化角色、用户、活动、队伍、通知和反馈示例数据。这个模式最适合课程演示和快速联调。

### 1. 启动后端

```bash
cd /home/rising5/Software_lab/lab2/backend
mvn spring-boot:run
```

启动成功后：

- 后端地址：`http://localhost:8080`
- Swagger：`http://localhost:8080/swagger-ui.html`
- H2 控制台：`http://localhost:8080/h2-console`

H2 控制台连接参数：

```text
JDBC URL: jdbc:h2:mem:campusflow;MODE=MySQL;DB_CLOSE_DELAY=-1;DATABASE_TO_LOWER=TRUE
User Name: sa
Password:
```

### 2. 启动前端

```bash
cd /home/rising5/Software_lab/lab2/frontend
cp .env.example .env
npm install
npm run dev
```

启动成功后：

- 前端地址：`http://localhost:5173`

## 二、MySQL 模式启动方式

如果你要严格按课程数据库环境演示，可以切换到 MySQL。

### 1. 初始化数据库

```bash
mysql -uroot -p < /home/rising5/Software_lab/lab2/sql/campusflow-mysql.sql
```

### 2. 修改后端 MySQL 配置

编辑文件：

- `/home/rising5/Software_lab/lab2/backend/src/main/resources/application-mysql.yml`

至少要改这三项：

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/campusflow?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai
    username: root
    password: 123456
```

### 3. 以 MySQL Profile 启动后端

```bash
cd /home/rising5/Software_lab/lab2/backend
mvn spring-boot:run -Dspring-boot.run.profiles=mysql
```

说明：

- 表结构来自 `sql/campusflow-mysql.sql`
- 应用启动后，如果数据库为空，会自动补充演示账号和示例业务数据

## 三、前端环境变量

默认前端通过 `VITE_API_BASE_URL` 访问后端。

文件：

- `/home/rising5/Software_lab/lab2/frontend/.env`

示例：

```bash
VITE_API_BASE_URL=http://localhost:8080
```

## 四、演示账号

所有演示账号密码统一为：

```text
123456
```

可直接登录的账号：

- `student01`：学生视角
- `captain01`：队长视角
- `organizer01`：组织者视角
- `admin01`：管理员视角
- `student02`、`student03`：额外学生测试账号

## 五、推荐演示路径

### 学生视角

1. 使用 `student01 / 123456` 登录
2. 在活动广场查看活动详情
3. 进入“加入队伍”页查看可加入队伍
4. 进入签到页查看活动签到状态
5. 对已结束活动提交反馈

### 队长视角

1. 使用 `captain01 / 123456` 登录
2. 查看自己的队伍详情
3. 在队伍详情页处理入队申请
4. 提交队伍报名

### 组织者视角

1. 使用 `organizer01 / 123456` 登录
2. 进入“活动管理”发布或编辑活动
3. 进入“审核中心”处理队伍报名
4. 观察学生端通知变化

### 管理员视角

1. 使用 `admin01 / 123456` 登录
2. 进入“公告治理”发布全站公告
3. 在通知页查看公告同步效果

## 六、关键接口说明

后端已按文档实现这些核心接口：

- `POST /api/auth/login`
- `GET /api/user/profile`
- `GET /api/activities`
- `GET /api/activities/{id}`
- `POST /api/activities`
- `POST /api/teams`
- `GET /api/teams/{id}`
- `POST /api/teams/{id}/apply`
- `POST /api/teams/{id}/submit`
- `GET /api/reviews`
- `POST /api/reviews/{id}/approve`
- `POST /api/reviews/{id}/reject`
- `GET /api/notices`
- `POST /api/notices/read`
- `GET /api/notices/unread-count`
- `GET /api/sign/status/{activityId}`
- `POST /api/sign/check-in`
- `POST /api/feedback`
- `GET /api/feedback/activity/{activityId}`
- `GET /api/announcements`
- `POST /api/announcements`

## 七、我对文档的实际落地说明

这次实现基本遵循你提供的技术路线与业务流程，但有两点是为了更适合课程演示做的增强：

1. 默认后端启用了 H2 演示模式，这样不用先装 MySQL 就能直接跑起来；如果要严格切 MySQL，可以按上面的 Profile 启动方式切换。
2. 在原始建表设计基础上，我额外补了几个实际运行需要的字段，比如活动签到码、签到窗口、反馈标签和活动结果总结，这样签到与反馈页才可以完整闭环。

## 八、如果启动失败，先看这里

最可能的原因有三个：

1. 本机没有安装 `mvn`
2. `npm install` 没有完成依赖安装
3. MySQL 模式下账号密码或数据库地址没有改对

### 验证命令

```bash
java -version
mvn -version
node -v
npm -v
```

### 常用修复方式

如果缺 Maven：

```bash
sudo apt-get update
sudo apt-get install -y maven
```

如果前端依赖没装：

```bash
cd /home/rising5/Software_lab/lab2/frontend
npm install
```

如果 MySQL 连不上：

```bash
mysql -uroot -p
```

先确认 `campusflow` 数据库存在，再检查 `application-mysql.yml` 中的连接信息。
