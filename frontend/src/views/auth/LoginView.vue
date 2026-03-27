<template>
  <div class="login-shell">
    <div class="login-toolbar">
      <ThemeToggle />
    </div>

    <section class="login-board glass-card">
      <div class="login-copy">
        <div class="soft-tag">Unified Campus Operations</div>
        <h1>一个把校园活动运营流程真正串起来的统一入口</h1>
        <p>
          CampusFlow 将活动发布、队伍协作、审核通知、签到反馈放在同一个平台内处理。
          无论你是学生、队长、组织者还是管理员，都能从这里进入对应的工作流。
        </p>

        <div class="feature-grid">
          <div class="feature-card">
            <strong>入口统一</strong>
            <span>活动浏览、协作报名、消息提醒和运营台统一收口。</span>
          </div>
          <div class="feature-card">
            <strong>协作清晰</strong>
            <span>队长、组织者和管理员各自拥有直接可用的工作入口。</span>
          </div>
          <div class="feature-card">
            <strong>状态同步</strong>
            <span>审核结果、公告广播和流程通知都能自动回流到消息中心。</span>
          </div>
          <div class="feature-card">
            <strong>流程闭环</strong>
            <span>从报名到签到再到反馈复盘，不再依赖多个分散页面。</span>
          </div>
        </div>

        <div class="account-wall">
          <button
            v-for="account in accounts"
            :key="account.username"
            type="button"
            class="account-card"
            @click="fillAccount(account.username)"
          >
            <div>
              <strong>{{ account.label }}</strong>
              <span>{{ account.caption }}</span>
            </div>
            <em>{{ account.username }}</em>
          </button>
        </div>
      </div>

      <div class="login-panel">
        <div class="panel-badge">Platform Access</div>
        <h2>登录账号</h2>
        <p>当前预置角色账号均可直接使用，默认密码统一为 <strong>123456</strong>。</p>

        <el-form :model="form" label-position="top" @submit.prevent="handleSubmit">
          <el-form-item label="用户名">
            <el-input v-model="form.username" placeholder="例如 student01 / organizer01" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="form.password" show-password placeholder="默认 123456" />
          </el-form-item>
          <el-button type="primary" round class="submit-btn" :loading="loading" @click="handleSubmit">
            进入 CampusFlow
          </el-button>
        </el-form>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ThemeToggle from '../../components/ThemeToggle.vue'
import { useUserStore } from '../../stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loading = ref(false)
const form = reactive({
  username: 'student01',
  password: '123456'
})

const accounts = [
  { label: '学生入口', username: 'student01', caption: '浏览活动、加队、签到和反馈' },
  { label: '队长入口', username: 'captain01', caption: '队伍管理、入队审批、提交报名' },
  { label: '组织者入口', username: 'organizer01', caption: '发布活动、审核报名、运营活动' },
  { label: '管理员入口', username: 'admin01', caption: '公告治理、平台消息与系统管理' }
]

const fillAccount = (username: string) => {
  form.username = username
  form.password = '123456'
}

const handleSubmit = async () => {
  try {
    loading.value = true
    await userStore.login(form)
    ElMessage.success('登录成功')
    router.push((route.query.redirect as string) || '/dashboard')
  } catch (error) {
    ElMessage.error((error as Error).message)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-shell {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
}

.login-toolbar {
  position: absolute;
  top: 24px;
  right: 24px;
}

.login-board {
  width: min(1220px, 100%);
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(360px, 0.82fr);
  gap: 26px;
  padding: 28px;
  border-radius: 34px;
}

.login-copy {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.login-copy h1 {
  margin: 0;
  font-size: clamp(40px, 4.4vw, 64px);
  line-height: 1.02;
  letter-spacing: -0.05em;
}

.login-copy p {
  margin: 0;
  max-width: 760px;
  color: var(--cf-ink-soft);
  line-height: 1.9;
  font-size: 15px;
}

.feature-grid,
.account-wall {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.feature-card,
.account-card {
  padding: 18px;
  border: 1px solid var(--cf-line);
  border-radius: 22px;
  background: var(--cf-surface-strong);
}

.feature-card strong,
.account-card strong {
  display: block;
  font-size: 16px;
}

.feature-card span,
.account-card span {
  display: block;
  margin-top: 8px;
  color: var(--cf-ink-soft);
  font-size: 13px;
  line-height: 1.7;
}

.account-card {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
  cursor: pointer;
}

.account-card em {
  padding: 8px 10px;
  border-radius: 12px;
  background: var(--cf-primary-soft);
  color: var(--cf-primary-deep);
  font-style: normal;
  font-size: 12px;
  font-weight: 800;
}

.login-panel {
  align-self: stretch;
  padding: 26px;
  border-radius: 30px;
  background: linear-gradient(180deg, var(--cf-paper-strong), var(--cf-card-end));
  border: 1px solid var(--cf-line);
}

.panel-badge {
  width: fit-content;
  padding: 8px 12px;
  border-radius: 999px;
  background: var(--cf-accent-soft);
  color: var(--cf-accent);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.login-panel h2 {
  margin: 18px 0 10px;
  font-size: 30px;
  line-height: 1.1;
  letter-spacing: -0.03em;
}

.login-panel p {
  margin: 0 0 22px;
  color: var(--cf-ink-soft);
  line-height: 1.75;
}

.submit-btn {
  width: 100%;
  margin-top: 8px;
}

@media (max-width: 980px) {
  .login-board,
  .feature-grid,
  .account-wall {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .login-toolbar {
    top: 16px;
    right: 16px;
  }
}
</style>
