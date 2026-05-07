<template>
  <div class="layout-shell">
    <header class="layout-header">
      <div class="page-shell header-shell">
        <div class="header-card">
          <RouterLink to="/activities" class="brand">
            <img class="brand-logo" :src="brandLogo" alt="CampusFlow 校园活动更高效" />
          </RouterLink>

          <nav class="nav-links" aria-label="主导航">
            <RouterLink to="/activities">首页</RouterLink>
            <RouterLink to="/activities#ai-screening">AI筛选</RouterLink>
            <RouterLink v-if="userStore.isLoggedIn" to="/dashboard">工作台</RouterLink>
            <RouterLink v-if="userStore.isLoggedIn" to="/teams/join">队伍广场</RouterLink>
            <RouterLink v-if="isOrganizer" to="/organizer/activities">活动管理</RouterLink>
            <RouterLink v-if="isOrganizer" to="/organizer/reviews">审核中心</RouterLink>
            <RouterLink v-if="isAdmin" to="/admin/announcements">公告治理</RouterLink>
          </nav>

          <div class="header-actions">
            <ThemeToggle />

            <el-button
              v-if="userStore.isLoggedIn"
              round
              class="ghost-button"
              @click="router.push('/notices')"
            >
              消息
              <el-badge :value="noticeStore.unreadCount" :hidden="!noticeStore.unreadCount" class="message-badge" />
            </el-button>

            <template v-if="userStore.isLoggedIn && userStore.profile">
              <el-dropdown>
                <button type="button" class="user-chip">
                  <el-avatar :src="userStore.profile.avatar" :size="38" />
                  <div>
                    <div class="user-name">{{ userStore.profile.nickname }}</div>
                    <div class="user-role">{{ roleLabelMap[userStore.role] || userStore.role }}</div>
                  </div>
                </button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="router.push('/dashboard')">进入工作台</el-dropdown-item>
                    <el-dropdown-item @click="router.push('/notices')">查看消息</el-dropdown-item>
                    <el-dropdown-item v-if="isOrganizer" @click="router.push('/organizer/activities')">管理活动</el-dropdown-item>
                    <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>

            <template v-else>
              <button type="button" class="text-action" @click="router.push('/login')">Login</button>
              <el-button type="primary" round @click="router.push('/login')">Join</el-button>
            </template>
          </div>
        </div>
      </div>
    </header>

    <main class="page-shell main-shell">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ThemeToggle from '../components/ThemeToggle.vue'
import brandLogo from '../assets/brand/logo.png'
import { useNoticeStore } from '../stores/notice'
import { useUserStore } from '../stores/user'
import { roleLabelMap } from '../utils/format'

const router = useRouter()
const userStore = useUserStore()
const noticeStore = useNoticeStore()

const isOrganizer = computed(() => ['organizer', 'admin'].includes(userStore.role))
const isAdmin = computed(() => userStore.role === 'admin')

const bindNotice = async () => {
  if (!userStore.profile?.id) return
  await noticeStore.fetchUnreadCount()
  await noticeStore.connect(userStore.profile.id)
}

watch(
  () => noticeStore.latest,
  (notice) => {
    if (notice) {
      ElMessage.success(notice.title)
    }
  }
)

onMounted(async () => {
  if (userStore.isLoggedIn && !userStore.profile) {
    await userStore.fetchProfile()
  }
  if (userStore.profile?.id) {
    await bindNotice()
  }
})

watch(
  () => userStore.profile?.id,
  async (userId) => {
    if (userId) {
      await bindNotice()
    } else {
      noticeStore.disconnect()
    }
  }
)

const handleLogout = () => {
  noticeStore.disconnect()
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/activities')
}
</script>

<style scoped>
.layout-shell {
  min-height: 100vh;
}

.layout-header {
  position: relative;
}

.header-shell {
  padding-bottom: 0;
}

.header-card {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 20px;
  padding: 18px 0 14px;
}

.brand {
  display: flex;
  align-items: center;
  width: clamp(78px, 7.5vw, 102px);
  flex-shrink: 0;
}

.brand-logo {
  width: 100%;
  height: auto;
  display: block;
}

.nav-links {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 8px;
}

.nav-links a {
  padding: 10px 14px;
  border-radius: 999px;
  color: var(--cf-ink-soft);
  font-size: 14px;
  font-weight: 700;
  transition: color 0.18s ease, background 0.18s ease;
}

.nav-links a:hover,
.nav-links a.router-link-active {
  color: var(--cf-ink);
  background: var(--cf-surface-soft);
}

.header-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
}

.ghost-button {
  position: relative;
}

.message-badge {
  margin-left: 6px;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 7px 12px 7px 8px;
  border: 1px solid var(--cf-line);
  border-radius: 18px;
  background: var(--cf-paper);
  color: inherit;
  cursor: pointer;
}

.user-name {
  font-size: 14px;
  font-weight: 800;
  text-align: left;
}

.user-role {
  margin-top: 3px;
  color: var(--cf-ink-soft);
  font-size: 12px;
  text-align: left;
}

.text-action {
  border: 0;
  background: transparent;
  color: var(--cf-ink-soft);
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.text-action:hover {
  color: var(--cf-ink);
}

.main-shell {
  padding-top: 10px;
}

@media (max-width: 1120px) {
  .header-card {
    grid-template-columns: 1fr;
  }

  .nav-links {
    justify-content: flex-start;
    overflow-x: auto;
    flex-wrap: nowrap;
    padding-bottom: 4px;
  }

  .header-actions {
    justify-content: space-between;
    flex-wrap: wrap;
  }
}

@media (max-width: 720px) {
  .brand {
    width: clamp(72px, 21vw, 88px);
  }

  .user-chip {
    width: 100%;
    justify-content: center;
  }
}
</style>
