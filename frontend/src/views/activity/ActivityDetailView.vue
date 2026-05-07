<template>
  <div class="list-stack" v-if="detail">
    <section class="detail-hero glass-card">
      <div class="hero-media" :style="{ backgroundImage: `url(${detail.coverUrl || fallbackCover})` }">
        <div class="hero-overlay" />
        <div class="hero-inner">
          <div class="hero-copy">
            <div class="cf-chip-row">
              <span class="soft-tag">{{ detail.type }}</span>
              <el-tag :type="statusTagTypeMap[detail.status] || 'info'" round effect="dark">
                {{ statusLabelMap[detail.status] || detail.status }}
              </el-tag>
            </div>
            <h1 class="page-title">{{ detail.title }}</h1>
            <p class="page-subtitle hero-subtitle">
              由 {{ detail.organizerName }} 发起，活动地点位于 {{ detail.location }}。
              在这里可以直接查看规则、进入组队或签到，并跟进活动结束后的反馈情况。
            </p>

            <div class="hero-facts">
              <div class="hero-fact">
                <span>开始时间</span>
                <strong>{{ formatDateTime(detail.startTime) }}</strong>
              </div>
              <div class="hero-fact">
                <span>报名截止</span>
                <strong>{{ formatDateTime(detail.signupDeadline) }}</strong>
              </div>
              <div class="hero-fact">
                <span>参与模式</span>
                <strong>{{ detail.requireTeam ? `${detail.minTeamSize}-${detail.maxTeamSize} 人组队` : '个人参与' }}</strong>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <div class="card-grid two-col">
      <section class="list-stack">
        <article class="glass-card content-panel">
          <div class="panel-head">
            <div>
              <h2 class="section-title">活动全景</h2>
              <p class="section-subtitle">统一展示活动定位、时间、规则与组织方式</p>
            </div>
          </div>

          <div class="overview-grid">
            <div class="overview-card">
              <span>队伍数量</span>
              <strong>{{ detail.teamCount }}</strong>
              <p>当前围绕本活动形成的协作队伍数</p>
            </div>
            <div class="overview-card">
              <span>历史评分</span>
              <strong>{{ averageScore }}</strong>
              <p>{{ feedback?.total || 0 }} 条历史反馈的平均分</p>
            </div>
            <div class="overview-card">
              <span>我的状态</span>
              <strong>{{ participationLabel }}</strong>
              <p>平台根据当前账号自动判断参与与协作状态</p>
            </div>
          </div>

          <div class="cf-chip-row detail-tags">
            <span v-for="tag in detail.tags" :key="tag" class="cf-chip">{{ tag }}</span>
          </div>

          <div class="content-section">
            <h3 class="section-title">活动介绍</h3>
            <div class="article-text">{{ detail.description }}</div>
          </div>

          <div class="content-section">
            <h3 class="section-title">参与规则</h3>
            <div class="rule-list">
              <div class="rule-item">
                <strong>报名截止</strong>
                <p>请在 {{ formatDateTime(detail.signupDeadline) }} 前完成报名或队伍提交。</p>
              </div>
              <div class="rule-item">
                <strong>组队要求</strong>
                <p>{{ detail.requireTeam ? `本活动要求 ${detail.minTeamSize}-${detail.maxTeamSize} 人组队参与。` : '本活动支持个人直接参与。' }}</p>
              </div>
              <div class="rule-item">
                <strong>后续环节</strong>
                <p>通过审核后将收到通知提醒，并在活动开始前进入签到和反馈闭环。</p>
              </div>
            </div>
          </div>

          <div class="content-section" v-if="detail.resultSummary">
            <h3 class="section-title">结果与复盘</h3>
            <div class="article-text">{{ detail.resultSummary }}</div>
          </div>
        </article>

        <article class="glass-card content-panel">
          <div class="panel-head">
            <div>
              <h2 class="section-title">历史反馈</h2>
              <p class="section-subtitle">帮助后续参与者快速判断活动质量与组织水平</p>
            </div>
            <div class="feedback-score">{{ averageScore }}</div>
          </div>

          <div class="feedback-list">
            <div v-for="item in feedback?.records || []" :key="`${item.userId}-${item.createdAt}`" class="feedback-item">
              <div class="feedback-head">
                <div>
                  <strong>{{ item.nickname }}</strong>
                  <span>{{ formatDateTime(item.createdAt) }}</span>
                </div>
                <div class="feedback-rate">{{ item.score }} / 5</div>
              </div>
              <p>{{ item.content || '该参与者未填写文字反馈。' }}</p>
              <div class="cf-chip-row" v-if="item.tags?.length">
                <span v-for="tag in item.tags" :key="tag" class="cf-chip">{{ tag }}</span>
              </div>
            </div>
            <el-empty v-if="!(feedback?.records?.length)" description="暂无反馈" />
          </div>
        </article>
      </section>

      <aside class="list-stack">
        <article class="glass-card action-panel">
          <div class="soft-tag">Participation</div>
          <h2 class="section-title">参与入口</h2>
          <p class="section-subtitle">根据当前账号状态展示可执行动作，减少无效跳转和重复确认。</p>

          <div class="action-status">
            <span class="status-dot">{{ participationLabel }}</span>
            <span>{{ actionStatusText }}</span>
          </div>

          <div class="list-stack action-buttons">
            <el-button
              v-if="userStore.isLoggedIn && detail.requireTeam && detail.canCreateTeam"
              type="primary"
              round
              @click="router.push(`/teams/create?activityId=${detail.id}`)"
            >
              创建队伍并发起招募
            </el-button>
            <el-button
              v-if="userStore.isLoggedIn && detail.requireTeam && detail.canApplyTeam"
              round
              @click="router.push(`/teams/join?activityId=${detail.id}`)"
            >
              查找队伍并申请加入
            </el-button>
            <el-button
              v-if="userStore.isLoggedIn && !detail.requireTeam && detail.canSignupPersonal"
              type="primary"
              round
              @click="handlePersonalSignup"
            >
              提交个人报名
            </el-button>
            <el-button
              v-if="userStore.isLoggedIn && detail.myTeamId"
              type="primary"
              round
              @click="router.push(`/teams/${detail.myTeamId}`)"
            >
              进入我的队伍提交报名
            </el-button>
            <el-button
              v-if="userStore.isLoggedIn && detail.canSignIn"
              type="success"
              round
              @click="router.push(`/sign?activityId=${detail.id}`)"
            >
              进入现场签到
            </el-button>
            <el-button
              v-if="userStore.isLoggedIn && detail.canFeedback"
              type="warning"
              round
              @click="router.push(`/feedback/${detail.id}`)"
            >
              提交活动反馈
            </el-button>
            <el-button v-if="!userStore.isLoggedIn" type="primary" round @click="router.push('/login')">
              登录后参与活动
            </el-button>
          </div>
        </article>

        <article class="glass-card side-info">
          <h3 class="section-title">关键节点</h3>
          <div class="timeline-list">
            <div class="timeline-item">
              <span>活动开始</span>
              <strong>{{ formatDateTime(detail.startTime) }}</strong>
            </div>
            <div class="timeline-item">
              <span>活动结束</span>
              <strong>{{ formatDateTime(detail.endTime) }}</strong>
            </div>
            <div class="timeline-item">
              <span>报名截止</span>
              <strong>{{ formatDateTime(detail.signupDeadline) }}</strong>
            </div>
          </div>
        </article>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '../../api'
import { useUserStore } from '../../stores/user'
import type { ActivityDetail, FeedbackSummary } from '../../types'
import { formatDateTime, statusLabelMap, statusTagTypeMap } from '../../utils/format'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const detail = ref<ActivityDetail | null>(null)
const feedback = ref<FeedbackSummary | null>(null)
const fallbackCover =
  'https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=1200&q=80'

const averageScore = computed(() => (feedback.value?.averageScore ?? 0).toFixed(1))
const participationLabel = computed(() => {
  if (!userStore.isLoggedIn) return '待登录'
  if (detail.value?.myTeamId) return '已在队伍中'
  if (detail.value?.myApplicationStatus === 'pending') return '报名待审核'
  if (detail.value?.myApplicationStatus === 'approved') return '报名已通过'
  if (detail.value?.myApplicationStatus === 'rejected') return '报名未通过'
  if (detail.value?.canFeedback) return '可反馈'
  if (detail.value?.canSignIn) return '可签到'
  if (detail.value?.canApplyTeam || detail.value?.canCreateTeam || detail.value?.canSignupPersonal) return '可参与'
  return '待审核或已结束'
})
const actionStatusText = computed(() => {
  if (!detail.value) return ''
  if (detail.value.myTeamId) return `当前已加入队伍 #${detail.value.myTeamId}`
  if (!detail.value.requireTeam && detail.value.myApplicationStatus) {
    return `个人报名状态：${statusLabelMap[detail.value.myApplicationStatus] || detail.value.myApplicationStatus}`
  }
  return detail.value.requireTeam ? '尚未加入本活动队伍' : '尚未提交个人报名'
})

const loadDetail = async () => {
  const id = Number(route.params.id)
  const [detailResponse, feedbackResponse] = await Promise.all([
    api.getActivityDetail(id),
    api.getFeedback(id)
  ])
  detail.value = detailResponse.data
  feedback.value = feedbackResponse.data
}

const handlePersonalSignup = async () => {
  if (!detail.value) return
  const { value } = await ElMessageBox.prompt('可填写报名说明，帮助组织者快速审核。', '提交个人报名', {
    confirmButtonText: '提交',
    cancelButtonText: '取消',
    inputPlaceholder: '例如：我已确认时间安排，可以准时参加'
  })
  await api.signupActivity(detail.value.id, { reason: value })
  ElMessage.success('个人报名已提交，等待组织者审核')
  await loadDetail()
}

onMounted(loadDetail)
</script>

<style scoped>
.detail-hero {
  overflow: hidden;
  padding: 0;
}

.hero-media {
  position: relative;
  min-height: 410px;
  padding: 36px;
  background-size: cover;
  background-position: center;
  color: white;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--cf-hero-overlay) 42%, transparent), var(--cf-hero-overlay)),
    linear-gradient(120deg, color-mix(in srgb, var(--cf-primary) 36%, transparent), transparent 42%);
}

.hero-inner {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: end;
  min-height: 338px;
}

.hero-copy {
  width: min(860px, 100%);
}

.hero-subtitle {
  margin-top: 16px;
  color: rgba(255, 255, 255, 0.88);
}

.hero-facts {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 26px;
}

.hero-fact {
  padding: 16px;
  border-radius: 18px;
  background: var(--cf-hero-soft-overlay);
  backdrop-filter: blur(8px);
}

.hero-fact span {
  display: block;
  font-size: 12px;
  opacity: 0.86;
}

.hero-fact strong {
  display: block;
  margin-top: 10px;
  font-size: 15px;
  line-height: 1.6;
}

.content-panel,
.action-panel,
.side-info {
  padding: 24px;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-start;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 20px;
}

.overview-card {
  padding: 18px;
  border-radius: 20px;
  background: var(--cf-surface-soft);
}

.overview-card span {
  color: var(--cf-ink-soft);
  font-size: 12px;
}

.overview-card strong {
  display: block;
  margin-top: 14px;
  font-size: 30px;
  font-weight: 800;
  letter-spacing: -0.04em;
}

.overview-card p {
  margin: 10px 0 0;
  color: var(--cf-ink-soft);
  font-size: 13px;
  line-height: 1.7;
}

.detail-tags {
  margin-top: 18px;
}

.content-section + .content-section {
  margin-top: 28px;
}

.content-section {
  margin-top: 28px;
}

.article-text {
  margin-top: 14px;
  color: var(--cf-ink-soft);
  line-height: 1.95;
  white-space: pre-line;
}

.rule-list {
  display: grid;
  gap: 14px;
  margin-top: 14px;
}

.rule-item {
  padding: 16px 18px;
  border-left: 3px solid color-mix(in srgb, var(--cf-primary) 36%, transparent);
  border-radius: 0 16px 16px 0;
  background: var(--cf-primary-soft);
}

.rule-item p {
  margin: 10px 0 0;
  color: var(--cf-ink-soft);
  line-height: 1.75;
}

.feedback-score {
  min-width: 64px;
  padding: 12px 14px;
  border-radius: 16px;
  background: var(--cf-accent-soft);
  color: var(--cf-accent);
  font-size: 24px;
  font-weight: 800;
  text-align: center;
}

.feedback-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: 18px;
}

.feedback-item {
  padding: 18px;
  border-radius: 20px;
  background: var(--cf-surface-soft);
}

.feedback-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.feedback-head span {
  display: block;
  margin-top: 6px;
  color: var(--cf-ink-soft);
  font-size: 12px;
}

.feedback-rate {
  color: var(--cf-primary);
  font-weight: 800;
}

.feedback-item p {
  margin: 12px 0;
  color: var(--cf-ink-soft);
  line-height: 1.8;
}

.action-panel {
  position: sticky;
  top: 108px;
}

.action-status {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 18px;
  padding: 16px;
  border-radius: 18px;
  background: var(--cf-surface-soft);
  color: var(--cf-ink-soft);
  font-size: 13px;
}

.action-buttons {
  margin-top: 20px;
}

.timeline-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: 18px;
}

.timeline-item {
  padding: 16px;
  border-radius: 18px;
  background: var(--cf-surface-soft);
}

.timeline-item span {
  color: var(--cf-ink-soft);
  font-size: 12px;
}

.timeline-item strong {
  display: block;
  margin-top: 8px;
  line-height: 1.7;
}

@media (max-width: 960px) {
  .hero-media {
    min-height: 360px;
    padding: 24px;
  }

  .hero-facts,
  .overview-grid {
    grid-template-columns: 1fr;
  }

  .action-panel {
    position: static;
  }
}
</style>
