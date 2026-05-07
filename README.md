# CampusFlow

CampusFlow 是一个面向校园活动场景的前后端分离课程项目，围绕“活动发现 -> 组队协作 -> 提交报名 -> 组织者审核 -> 消息通知 -> 活动签到 -> 结果反馈”实现完整闭环。

本项目包含：

- `backend`：Python 标准库实现的轻量后端，默认入口为 `backend/app.py`
- `frontend`：Vue 3 + TypeScript + Vite + Pinia + Element Plus 前端
- `sql`：课程数据库建表脚本，当前 Python 演示后端默认使用内存数据
- `docs`：实验报告、接口补充说明或答辩材料

说明：原 Spring Boot 代码仍保留在 `backend/src` 和 `backend/pom.xml` 中作为参考，但默认启动方式已经切换为 Python 后端。

## 已实现模块

- 用户登录、Token 鉴权、个人资料查看/修改
- 活动列表、活动详情、组织者活动管理
- 创建队伍、加入队伍、队伍详情、队长提交报名
- 个人活动报名、组织者审核个人报名
- 队伍退出、成员移除、队长转让、队伍解散
- 组织者审核报名、队长审核入队申请
- 组织者活动状态流转：草稿、已发布、报名中、报名截止、已结束、已取消
- 通知列表、未读数统计
- 活动签到、签到状态查询
- 活动反馈与历史评分展示
- 管理员公告发布与全站通知
- 概览页数据统计与 ECharts 图表展示

## 目录结构

```text
lab2/
├── backend/
│   ├── app.py                  # Python 后端启动入口
│   ├── campusflow_py/
│   │   └── server.py           # 路由、演示数据和业务逻辑
│   ├── requirements.txt        # 当前无第三方依赖
│   ├── pom.xml                 # 旧 Java 后端参考文件
│   └── src/                    # 旧 Java 后端参考源码
├── frontend/                   # Vue 3 前端
├── sql/
│   └── campusflow-mysql.sql    # MySQL 建表脚本
├── docs/
└── README.md
```

## 环境要求

建议按下面版本准备环境：

- `Python 3.10+`
- `Node.js 20+` 或 `Node.js 24`
- `npm 10+`
- `MySQL 8.0`（可选，仅用于查看或复用 `sql/campusflow-mysql.sql`）

Python 后端当前只依赖标准库，不需要安装 Flask、FastAPI 或 Django。

## 一、启动后端

后端默认监听：

- 后端地址：`http://localhost:8080`
- 健康检查：`http://localhost:8080/api/health`

如需改端口，可设置环境变量 `CAMPUSFLOW_PORT`。

### Windows PowerShell

```powershell
cd C:\path\to\lab2\backend
py -3 app.py
```

如果要改端口：

```powershell
cd C:\path\to\lab2\backend
$env:CAMPUSFLOW_PORT=8081
py -3 app.py
```

### Windows CMD

```bat
cd /d C:\path\to\lab2\backend
py -3 app.py
```

如果要改端口：

```bat
cd /d C:\path\to\lab2\backend
set CAMPUSFLOW_PORT=8081 && py -3 app.py
```

### Linux

```bash
cd /home/rising5/Software_lab/lab2/backend
python3 app.py
```

如果要改端口：

```bash
cd /home/rising5/Software_lab/lab2/backend
CAMPUSFLOW_PORT=8081 python3 app.py
```

### WSL

WSL 使用 Linux 命令。如果项目在当前 WSL 文件系统中：

```bash
cd /home/rising5/Software_lab/lab2/backend
python3 app.py
```

如果项目放在 Windows 磁盘，例如 `C:\Users\you\lab2`：

```bash
cd /mnt/c/Users/you/lab2/backend
python3 app.py
```

### macOS

```bash
cd /path/to/lab2/backend
python3 app.py
```

如果要改端口：

```bash
cd /path/to/lab2/backend
CAMPUSFLOW_PORT=8081 python3 app.py
```

## 二、启动前端

前端默认通过 `VITE_API_BASE_URL` 访问后端，示例值：

```bash
VITE_API_BASE_URL=http://localhost:8080
```

### Windows PowerShell

```powershell
cd C:\path\to\lab2\frontend
Set-Content .env "VITE_API_BASE_URL=http://localhost:8080"
npm install
npm run dev
```

### Windows CMD

```bat
cd /d C:\path\to\lab2\frontend
echo VITE_API_BASE_URL=http://localhost:8080> .env
npm install
npm run dev
```

### Linux

```bash
cd /home/rising5/Software_lab/lab2/frontend
printf "VITE_API_BASE_URL=http://localhost:8080\n" > .env
npm install
npm run dev
```

### WSL

```bash
cd /home/rising5/Software_lab/lab2/frontend
printf "VITE_API_BASE_URL=http://localhost:8080\n" > .env
npm install
npm run dev
```

如果项目放在 Windows 磁盘：

```bash
cd /mnt/c/Users/you/lab2/frontend
printf "VITE_API_BASE_URL=http://localhost:8080\n" > .env
npm install
npm run dev
```

### macOS

```bash
cd /path/to/lab2/frontend
printf "VITE_API_BASE_URL=http://localhost:8080\n" > .env
npm install
npm run dev
```

启动成功后：

- 前端地址：`http://localhost:5173`

## 三、演示数据说明

Python 后端启动时会自动加载内存演示数据，包括角色、用户、活动、队伍、通知、签到记录、反馈和公告。

注意：数据保存在内存中，重启后会恢复为初始演示数据。

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
5. 对已结束活动查看反馈汇总

### 队长视角

1. 使用 `captain01 / 123456` 登录
2. 查看自己的队伍详情
3. 在队伍详情页处理入队申请
4. 提交队伍报名

### 组织者视角

1. 使用 `organizer01 / 123456` 登录
2. 进入“活动管理”发布或编辑活动
3. 进入“审核中心”处理队伍报名
4. 在通知页观察消息变化

### 管理员视角

1. 使用 `admin01 / 123456` 登录
2. 进入“公告治理”发布全站公告
3. 在通知页查看公告同步效果

## 六、关键接口说明

Python 后端保留了前端当前使用的核心接口：

- `POST /api/auth/login`
- `GET /api/user/profile`
- `PUT /api/user/profile`
- `GET /api/dashboard/overview`
- `GET /api/activities`
- `GET /api/activities/mine`
- `GET /api/activities/{id}`
- `POST /api/activities`
- `PUT /api/activities/{id}`
- `POST /api/activities/{id}/signup`
- `POST /api/activities/{id}/status`
- `POST /api/teams`
- `GET /api/teams/{id}`
- `GET /api/teams/joinable`
- `POST /api/teams/{id}/apply`
- `POST /api/teams/{id}/submit`
- `POST /api/teams/{id}/leave`
- `POST /api/teams/{id}/disband`
- `POST /api/teams/{id}/transfer`
- `POST /api/teams/{id}/members/{userId}/remove`
- `GET /api/reviews`
- `POST /api/reviews/{id}/approve`
- `POST /api/reviews/{id}/reject`
- `GET /api/notices`
- `POST /api/notices/read`
- `POST /api/notices/read-all`
- `GET /api/notices/unread-count`
- `GET /api/sign/status/{activityId}`
- `POST /api/sign/check-in`
- `POST /api/feedback`
- `GET /api/feedback/activity/{activityId}`
- `GET /api/announcements`
- `POST /api/announcements`

## 七、如果启动失败，先看这里

最可能的原因有三个：

1. 本机没有安装 `python` 或 `python3`
2. `npm install` 没有完成依赖安装
3. 前端 `.env` 中的 `VITE_API_BASE_URL` 端口和后端实际端口不一致

验证命令：

```bash
python --version
python3 --version
node -v
npm -v
```

Linux / WSL / macOS 如果 `python` 不存在，优先用：

```bash
python3 app.py
```

Windows 如果 `python` 不存在，优先用：

```powershell
py -3 app.py
```
