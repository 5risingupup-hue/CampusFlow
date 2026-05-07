<template>
  <div class="list-stack landing-shell">
    <section class="hero-stage">
      <HomeHeroCluster side="left" class="cluster-left" />

      <div class="hero-center">
        <div class="hero-eyebrow">CampusFlow Platform</div>
        <h1 class="hero-title">
          CampusFlow
          <span class="hero-title-cn">让校园活动更高效</span>
        </h1>
        <p class="hero-copy">
          一个平台贯通校园活动全流程。
        </p>

        <div class="hero-cta">
          <el-button type="primary" round class="hero-button" @click="goPrimaryAction">Get Started</el-button>
        </div>

        <div class="hero-meta">
          <span class="hero-meta-pill">活动总数 {{ activityStore.pageResult.total || 0 }}</span>
          <span class="hero-meta-pill">开放报名 {{ signupOpenCount }}</span>
          <span class="hero-meta-pill">团队协作 {{ requireTeamCount }}</span>
        </div>
      </div>

      <HomeHeroCluster side="right" class="cluster-right" />
    </section>

    <section class="glass-card workflow-panel">
      <div class="panel-head">
        <div>
          <h2 class="section-title">核心流程</h2>
          <p class="section-subtitle">在一个入口里完成发布、协作、审核、签到和复盘，减少重复沟通和多系统切换。</p>
        </div>
      </div>

      <div class="workflow-grid">
        <div v-for="item in workflows" :key="item.title" class="workflow-card">
          <div class="workflow-index">{{ item.step }}</div>
          <strong>{{ item.title }}</strong>
          <p>{{ item.caption }}</p>
        </div>
      </div>
    </section>

    <section class="card-grid overview-grid">
      <article class="glass-card role-panel">
        <div class="panel-head">
          <div>
            <h2 class="section-title">角色入口</h2>
            <p class="section-subtitle">不同角色直接进入自己的高频工作流，不需要在首页重复寻找入口。</p>
          </div>
        </div>

        <div class="role-grid">
          <div v-for="item in roleEntries" :key="item.title" class="role-card">
            <strong>{{ item.title }}</strong>
            <p>{{ item.caption }}</p>
            <el-button :type="item.primary ? 'primary' : undefined" round @click="router.push(item.path)">
              {{ item.button }}
            </el-button>
          </div>
        </div>
      </article>

      <article class="glass-card bulletin-panel">
        <div class="panel-head">
          <div>
            <h2 class="section-title">公告与提醒</h2>
            <p class="section-subtitle">把规则更新和系统提醒固定在首页可见区域，确保重要通知不会遗漏。</p>
          </div>
        </div>

        <div class="bulletin-list">
          <article v-for="item in announcements.slice(0, 4)" :key="item.id" class="bulletin-item">
            <strong>{{ item.title }}</strong>
            <p>{{ item.content }}</p>
          </article>
          <el-empty v-if="!announcements.length" description="暂无公告" />
        </div>
      </article>
    </section>

    <section class="glass-card filter-panel">
      <div class="panel-head">
        <div>
          <h2 class="section-title">活动筛选</h2>
          <p class="section-subtitle">支持按关键词、类型和参与方式快速定位活动，随后直接进入详情或队伍协作。</p>
        </div>
      </div>

      <el-form :model="activityStore.filters" class="filter-form">
        <div class="filter-grid">
          <el-form-item label="关键词">
            <el-input v-model="activityStore.filters.keyword" placeholder="搜索活动标题或主题" clearable />
          </el-form-item>
          <el-form-item label="活动类型">
            <el-input v-model="activityStore.filters.type" placeholder="如 创新竞赛 / 志愿服务 / 技术沙龙" clearable />
          </el-form-item>
          <el-form-item label="参与方式">
            <el-select v-model="activityStore.filters.requireTeam" clearable placeholder="全部模式">
              <el-option :value="true" label="需要组队" />
              <el-option :value="false" label="个人参与" />
            </el-select>
          </el-form-item>
          <div class="filter-actions">
            <el-button type="primary" round @click="fetchActivities">立即筛选</el-button>
            <el-button round @click="resetFilters">重置条件</el-button>
          </div>
        </div>
      </el-form>
    </section>

    <section class="activity-board">
      <div class="board-head">
        <div>
          <h2 class="section-title">活动目录</h2>
          <p class="section-subtitle">每张卡片都直接承接后续参与动作，不再保留不能点击的伪按钮。</p>
        </div>
        <div class="board-meta">共 {{ activityStore.pageResult.total }} 个活动</div>
      </div>

      <div class="activity-grid">
        <div
          v-for="(activity, index) in activityStore.pageResult.records"
          :key="activity.id"
          class="activity-stack-item"
          :style="{
            zIndex: String(index + 1),
            '--stack-top': `${96 + index * 28}px`
          }"
        >
          <ActivityCard
            :activity="activity"
            :index="index"
          />
        </div>
      </div>

      <el-empty v-if="!activityStore.pageResult.records.length" description="暂无符合条件的活动" />
    </section>

    <section class="pagination-row">
      <el-pagination
        layout="prev, pager, next"
        :total="activityStore.pageResult.total"
        :page-size="activityStore.filters.pageSize"
        :current-page="activityStore.filters.pageNum"
        @current-change="handlePageChange"
      />
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../../api'
import ActivityCard from '../../components/ActivityCard.vue'
import HomeHeroCluster from '../../components/HomeHeroCluster.vue'
import { useActivityStore } from '../../stores/activity'
import { useUserStore } from '../../stores/user'
import type { AnnouncementItem } from '../../types'

const router = useRouter()
const userStore = useUserStore()
const activityStore = useActivityStore()
const announcements = ref<AnnouncementItem[]>([])

const signupOpenCount = computed(() =>
  activityStore.pageResult.records.filter((item) => item.status === 'signup_open').length
)

const requireTeamCount = computed(() =>
  activityStore.pageResult.records.filter((item) => item.requireTeam).length
)

const workflows = [
  { step: '01', title: '发布活动', caption: '统一录入活动信息、时间窗口和签到规则。' },
  { step: '02', title: '组队报名', caption: '学生按活动创建或加入队伍，队伍负责人集中提交。' },
  { step: '03', title: '审核同步', caption: '组织者处理审核后，结果自动写入通知中心。' },
  { step: '04', title: '现场签到', caption: '活动当天通过签到码完成状态校验与入场记录。' },
  { step: '05', title: '反馈回收', caption: '活动结束后沉淀反馈与结果复盘。' }
]

const roleEntries = computed(() => [
  {
    title: '学生',
    caption: '浏览活动、选择个人参与或加入已有队伍。',
    button: userStore.isLoggedIn ? '查看活动' : '登录后参与',
    path: userStore.isLoggedIn ? '/activities' : '/login',
    primary: !userStore.isLoggedIn
  },
  {
    title: '组队协作',
    caption: '学生创建队伍后可处理入队申请、维护成员并提交报名。',
    button: userStore.isLoggedIn ? '进入协作' : '登录查看',
    path: userStore.isLoggedIn ? '/teams/join' : '/login',
    primary: false
  },
  {
    title: '组织者',
    caption: '发布活动、调整时间窗口并集中处理审核。',
    button: ['organizer', 'admin'].includes(userStore.role) ? '打开工作台' : '登录查看',
    path: ['organizer', 'admin'].includes(userStore.role) ? '/organizer/activities' : '/login',
    primary: userStore.role === 'organizer'
  },
  {
    title: '管理员',
    caption: '治理公告和全站信息，维护平台统一规则。',
    button: userStore.role === 'admin' ? '进入治理台' : '登录查看',
    path: userStore.role === 'admin' ? '/admin/announcements' : '/login',
    primary: userStore.role === 'admin'
  }
])

const fetchActivities = async () => {
  await activityStore.fetchActivities()
}

const handlePageChange = async (page: number) => {
  activityStore.filters.pageNum = page
  await fetchActivities()
}

const resetFilters = async () => {
  activityStore.filters.keyword = ''
  activityStore.filters.type = ''
  activityStore.filters.requireTeam = undefined
  activityStore.filters.pageNum = 1
  await fetchActivities()
}

const goPrimaryAction = () => {
  if (userStore.isLoggedIn) {
    router.push('/dashboard')
    return
  }
  router.push('/login')
}

onMounted(async () => {
  await Promise.all([
    fetchActivities(),
    api.getAnnouncements().then((response) => {
      announcements.value = response.data
    })
  ])
})
</script>

<style scoped>
.landing-shell {
  gap: 22px;
}

.hero-stage {
  position: relative;
  display: grid;
  grid-template-columns: minmax(280px, 1fr) minmax(420px, 620px) minmax(280px, 1fr);
  align-items: center;
  min-height: 620px;
  padding: 18px 0 6px;
}

.hero-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
  text-align: center;
}

.hero-eyebrow {
  padding: 8px 14px;
  border-radius: 999px;
  background: var(--cf-primary-soft);
  color: var(--cf-primary-deep);
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.hero-title {
  margin: 0;
  max-width: 760px;
  font-size: clamp(56px, 7vw, 96px);
  line-height: 0.95;
  letter-spacing: -0.08em;
  font-weight: 900;
}

.hero-title span {
  display: block;
  margin-top: 10px;
  font-size: clamp(30px, 3.2vw, 54px);
  line-height: 1.04;
}

.hero-title-cn {
  letter-spacing: 0.01em;
}

.hero-copy {
  max-width: 640px;
  margin: 0;
  color: var(--cf-ink-soft);
  font-size: 17px;
  line-height: 1.75;
}

.hero-button {
  min-width: 190px;
  min-height: 64px;
  font-size: 24px;
  box-shadow: 0 12px 0 color-mix(in srgb, var(--cf-primary) 42%, transparent);
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
}

.hero-meta-pill {
  padding: 10px 14px;
  border: 1px solid var(--cf-line);
  border-radius: 999px;
  background: var(--cf-surface-strong);
  color: var(--cf-ink-soft);
  font-size: 13px;
  font-weight: 700;
}

.workflow-panel,
.role-panel,
.bulletin-panel,
.filter-panel {
  padding: 26px;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-start;
}

.workflow-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 14px;
  margin-top: 20px;
}

.workflow-card {
  padding: 20px;
  border-radius: 22px;
  background: var(--cf-workflow-1);
}

.workflow-card:nth-child(2) {
  background: var(--cf-workflow-2);
}

.workflow-card:nth-child(3) {
  background: var(--cf-workflow-3);
}

.workflow-card:nth-child(4) {
  background: var(--cf-workflow-4);
}

.workflow-card:nth-child(5) {
  background: var(--cf-workflow-5);
}

.workflow-index {
  color: var(--cf-primary);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.08em;
}

.workflow-card strong {
  display: block;
  margin-top: 12px;
  font-size: 18px;
}

.workflow-card p {
  margin: 10px 0 0;
  color: var(--cf-ink-soft);
  font-size: 13px;
  line-height: 1.75;
}

.overview-grid {
  grid-template-columns: minmax(0, 1.2fr) minmax(360px, 0.9fr);
}

.role-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-top: 20px;
}

.role-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px;
  border-radius: 22px;
  background: var(--cf-surface-soft);
}

.role-card strong {
  font-size: 18px;
}

.role-card p {
  margin: 0;
  color: var(--cf-ink-soft);
  line-height: 1.75;
  flex: 1;
}

.bulletin-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 20px;
}

.bulletin-item {
  padding: 18px;
  border-radius: 20px;
  background: var(--cf-surface-soft);
}

.bulletin-item strong {
  display: block;
  font-size: 15px;
}

.bulletin-item p {
  margin: 10px 0 0;
  color: var(--cf-ink-soft);
  line-height: 1.8;
  font-size: 13px;
}

.filter-grid {
  display: grid;
  grid-template-columns: 1.15fr 1fr 0.92fr auto;
  gap: 16px;
  align-items: end;
}

.filter-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding-bottom: 2px;
}

.activity-board {
  display: flex;
  flex-direction: column;
  gap: 18px;
  overflow: visible;
}

.board-head {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-end;
}

.board-meta {
  color: var(--cf-ink-soft);
  font-size: 13px;
  font-weight: 700;
}

.activity-grid {
  display: flex;
  flex-direction: column;
  gap: 34px;
  padding-top: 10px;
  padding-bottom: 28vh;
}

.activity-stack-item {
  position: relative;
  position: sticky;
  top: var(--stack-top);
}

.pagination-row {
  display: flex;
  justify-content: center;
}

@media (max-width: 1280px) {
  .hero-stage {
    grid-template-columns: 1fr;
    min-height: auto;
    justify-items: center;
    gap: 0;
  }

  .cluster-left,
  .cluster-right {
    max-width: 380px;
  }

  .cluster-right {
    margin-top: -60px;
  }

  .workflow-grid,
  .overview-grid {
    grid-template-columns: 1fr;
  }

  .activity-grid {
    gap: 28px;
  }
}

@media (max-width: 960px) {
  .role-grid,
  .filter-grid,
  .board-head {
    grid-template-columns: 1fr;
    display: grid;
  }

  .board-head {
    gap: 10px;
  }

  .activity-stack-item {
    top: var(--stack-top);
  }
}

@media (max-width: 760px) {
  .hero-title {
    font-size: 50px;
  }

  .hero-title span {
    font-size: 28px;
  }

  .hero-copy {
    font-size: 15px;
  }

  .hero-button {
    min-width: 168px;
    min-height: 58px;
    font-size: 21px;
  }

  .workflow-grid {
    grid-template-columns: 1fr;
  }

  .activity-grid {
    padding-bottom: 0;
    gap: 20px;
  }

  .activity-stack-item {
    position: relative;
    top: auto;
  }
}
</style>
