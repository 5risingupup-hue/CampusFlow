<template>
  <div v-if="teamStore.currentTeam" class="list-stack">
    <section class="glass-card team-hero">
      <div class="header-row">
        <div>
          <div class="soft-tag">{{ teamStore.currentTeam.activityTitle }}</div>
          <h1 class="page-title">{{ teamStore.currentTeam.teamName }}</h1>
          <p class="page-subtitle">
            {{ teamStore.currentTeam.leaderName }} 带队 · 当前 {{ teamStore.currentTeam.currentSize }} /
            {{ teamStore.currentTeam.maxTeamSize }} 人
          </p>
        </div>
        <el-tag :type="statusTagTypeMap[teamStore.currentTeam.status] || 'info'" round effect="dark">
          {{ statusLabelMap[teamStore.currentTeam.status] || teamStore.currentTeam.status }}
        </el-tag>
      </div>

      <div class="team-hero-grid">
        <div class="hero-stat">
          <span>邀请码</span>
          <strong>{{ teamStore.currentTeam.inviteCode }}</strong>
        </div>
        <div class="hero-stat">
          <span>人数要求</span>
          <strong>{{ teamStore.currentTeam.minTeamSize }} - {{ teamStore.currentTeam.maxTeamSize }} 人</strong>
        </div>
        <div class="hero-stat">
          <span>待审核申请</span>
          <strong>{{ teamStore.currentTeam.pendingApplications.length }}</strong>
        </div>
      </div>

      <div class="team-journey">
        <div v-for="item in workflowHints" :key="item.title" class="journey-chip">
          <span>{{ item.step }}</span>
          <strong>{{ item.title }}</strong>
        </div>
      </div>
    </section>

    <div class="card-grid two-col">
      <section class="glass-card detail-panel">
        <div class="overview-grid">
          <div class="overview-card">
            <span>提交状态</span>
            <strong>{{ statusLabelMap[teamStore.currentTeam.status] || teamStore.currentTeam.status }}</strong>
            <p>当前队伍处于哪个流程阶段，一眼就能判断下一步动作。</p>
          </div>
          <div class="overview-card">
            <span>队伍容量</span>
            <strong>{{ teamStore.currentTeam.currentSize }} / {{ teamStore.currentTeam.maxTeamSize }}</strong>
            <p>提交报名时系统会按活动人数门槛自动校验。</p>
          </div>
          <div class="overview-card">
            <span>管理权限</span>
            <strong>{{ teamStore.currentTeam.canManage ? '我是队长' : '普通成员' }}</strong>
            <p>{{ teamStore.currentTeam.canManage ? '可处理申请、转让队长和提交报名。' : '可跟进进度，必要时退出队伍。' }}</p>
          </div>
        </div>

        <div class="summary-panel">
          <p><strong>队伍口号：</strong>{{ teamStore.currentTeam.slogan || '暂无口号' }}</p>
          <p><strong>队伍简介：</strong>{{ teamStore.currentTeam.description || '暂无简介' }}</p>
        </div>

        <div class="flow-callout">
          <strong>当前建议</strong>
          <p>{{ teamActionHint }}</p>
        </div>

        <div class="content-block">
          <h2 class="section-title">成员列表</h2>
          <div class="member-list">
            <div v-for="member in teamStore.currentTeam.members" :key="member.userId" class="member-item">
              <div class="member-copy">
                <strong>{{ member.nickname }}</strong>
                <p>{{ member.memberRole }} · {{ member.joinStatus }}</p>
              </div>
              <div class="member-side">
                <span>{{ member.joinedAt ? formatDateTime(member.joinedAt) : '待加入' }}</span>
                <div
                  v-if="teamStore.currentTeam.canManage && canMutateTeam && member.userId !== teamStore.currentTeam.leaderId"
                  class="member-actions"
                >
                  <el-button size="small" @click="transferLeader(member.userId)">转为队长</el-button>
                  <el-button size="small" type="danger" plain @click="removeMember(member.userId)">移除</el-button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="teamStore.currentTeam.pendingApplications.length" class="content-block">
          <div class="section-head">
            <div>
              <h2 class="section-title">待审核申请</h2>
              <p class="section-subtitle">队长可以在本页直接完成通过或拒绝，无需切到其他页面</p>
            </div>
          </div>
          <div class="application-list">
            <div v-for="item in teamStore.currentTeam.pendingApplications" :key="item.id" class="application-item">
              <div class="application-copy">
                <strong>{{ item.applicantName }}</strong>
                <p>{{ item.reason || '该同学未填写申请理由。' }}</p>
              </div>
              <div v-if="teamStore.currentTeam.canManage" class="actions">
                <el-button size="small" type="success" @click="review(item.id, true)">通过</el-button>
                <el-button size="small" type="danger" @click="review(item.id, false)">拒绝</el-button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <aside class="list-stack">
        <article class="glass-card action-panel">
          <h2 class="section-title">队伍操作</h2>
          <p class="section-subtitle">围绕当前队伍最常用的动作做直达入口，避免重复切页。</p>
          <div class="action-status">
            <span class="status-dot">{{ statusLabelMap[teamStore.currentTeam.status] || teamStore.currentTeam.status }}</span>
            <span>{{ teamActionHint }}</span>
          </div>
          <div class="action-list">
            <el-button round @click="copyInviteCode">复制邀请码</el-button>
            <el-button
              v-if="teamStore.currentTeam.canManage && canMutateTeam"
              type="primary"
              round
              @click="submitSignup"
            >
              提交队伍报名
            </el-button>
            <el-button
              v-if="canLeaveTeam"
              type="danger"
              plain
              round
              @click="leaveTeam"
            >
              退出队伍
            </el-button>
            <el-button
              v-if="teamStore.currentTeam.canManage && canMutateTeam"
              type="danger"
              plain
              round
              @click="disbandTeam"
            >
              解散队伍
            </el-button>
            <el-button round @click="router.push(`/activities/${teamStore.currentTeam.activityId}`)">返回活动详情</el-button>
          </div>
        </article>

        <article class="glass-card process-panel">
          <h3 class="section-title">当前流程</h3>
          <div class="process-list">
            <div class="process-item">
              <strong>1. 维护成员</strong>
              <p>确认人数、分工和申请状态，确保队伍满足活动要求。</p>
            </div>
            <div class="process-item">
              <strong>2. 提交报名</strong>
              <p>队长在本页提交报名说明，组织者审核后自动触发通知。</p>
            </div>
            <div class="process-item">
              <strong>3. 进入执行</strong>
              <p>审核通过后，成员按照活动安排完成签到与反馈。</p>
            </div>
          </div>
        </article>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '../../api'
import { useTeamStore } from '../../stores/team'
import { useUserStore } from '../../stores/user'
import { formatDateTime, statusLabelMap, statusTagTypeMap } from '../../utils/format'

const route = useRoute()
const router = useRouter()
const teamStore = useTeamStore()
const userStore = useUserStore()

const canMutateTeam = computed(() =>
  Boolean(teamStore.currentTeam && !['submitted', 'approved', 'disbanded'].includes(teamStore.currentTeam.status))
)
const canLeaveTeam = computed(() =>
  Boolean(
    teamStore.currentTeam &&
    canMutateTeam.value &&
    !teamStore.currentTeam.canManage &&
    teamStore.currentTeam.members.some((member) => member.userId === userStore.profile?.id)
  )
)
const workflowHints = computed(() => [
  { step: '01', title: '先补齐成员' },
  { step: '02', title: '再统一提交报名' },
  { step: '03', title: '等待组织者审核' },
  { step: '04', title: '通过后签到反馈' }
])
const teamActionHint = computed(() => {
  if (!teamStore.currentTeam) return ''
  if (teamStore.currentTeam.status === 'forming') {
    return teamStore.currentTeam.canManage
      ? '优先确认人数是否达标，再处理待审核申请并提交报名。'
      : '当前队伍仍在组建中，等待队长处理申请或补齐成员。'
  }
  if (teamStore.currentTeam.status === 'submitted') return '队伍报名已提交，当前以等待审核结果和通知为主。'
  if (teamStore.currentTeam.status === 'approved') return '队伍已通过审核，接下来按活动安排组织签到与反馈。'
  if (teamStore.currentTeam.status === 'rejected') return '本次报名未通过，建议回看原因后再决定是否重组。'
  return '当前以跟进队伍状态为主。'
})

const loadTeam = async () => {
  await teamStore.fetchTeam(Number(route.params.id))
}

const copyInviteCode = async () => {
  if (!teamStore.currentTeam) return
  try {
    await navigator.clipboard.writeText(teamStore.currentTeam.inviteCode)
    ElMessage.success('邀请码已复制')
  } catch {
    ElMessage.warning(`邀请码：${teamStore.currentTeam.inviteCode}`)
  }
}

const review = async (reviewId: number, approve: boolean) => {
  const title = approve ? '确认通过这条申请吗？' : '确认拒绝这条申请吗？'
  const action = approve ? api.approveReview : api.rejectReview
  const { value } = await ElMessageBox.prompt(title, '审核申请', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputPlaceholder: '可填写审核备注'
  })
  await action(reviewId, { comment: value })
  ElMessage.success(approve ? '已通过' : '已拒绝')
  await loadTeam()
}

const submitSignup = async () => {
  const { value } = await ElMessageBox.prompt('可填写本次报名说明，便于组织者快速理解队伍情况。', '提交报名', {
    confirmButtonText: '提交',
    cancelButtonText: '取消',
    inputPlaceholder: '例如：我们已完成角色分工与赛题准备'
  })
  await api.submitTeam(Number(route.params.id), { reason: value })
  ElMessage.success('报名已提交')
  await loadTeam()
}

const removeMember = async (userId: number) => {
  await ElMessageBox.confirm('确认将该成员移出队伍吗？', '移除成员', {
    confirmButtonText: '移除',
    cancelButtonText: '取消',
    type: 'warning'
  })
  await api.removeTeamMember(Number(route.params.id), userId)
  ElMessage.success('成员已移除')
  await loadTeam()
}

const transferLeader = async (newLeaderId: number) => {
  await ElMessageBox.confirm('确认将队长转让给该成员吗？', '转让队长', {
    confirmButtonText: '转让',
    cancelButtonText: '取消',
    type: 'warning'
  })
  await api.transferTeamLeader(Number(route.params.id), { newLeaderId })
  ElMessage.success('队长已转让')
  await loadTeam()
}

const leaveTeam = async () => {
  if (!teamStore.currentTeam) return
  await ElMessageBox.confirm('确认退出当前队伍吗？', '退出队伍', {
    confirmButtonText: '退出',
    cancelButtonText: '取消',
    type: 'warning'
  })
  await api.leaveTeam(Number(route.params.id))
  ElMessage.success('已退出队伍')
  router.push(`/activities/${teamStore.currentTeam.activityId}`)
}

const disbandTeam = async () => {
  if (!teamStore.currentTeam) return
  await ElMessageBox.confirm('解散后成员和待审核申请都会终止，确认继续吗？', '解散队伍', {
    confirmButtonText: '解散',
    cancelButtonText: '取消',
    type: 'warning'
  })
  const activityId = teamStore.currentTeam.activityId
  await api.disbandTeam(Number(route.params.id))
  ElMessage.success('队伍已解散')
  router.push(`/activities/${activityId}`)
}

onMounted(loadTeam)
</script>

<style scoped>
.team-hero,
.detail-panel,
.action-panel,
.process-panel {
  padding: 24px;
}

.header-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.team-hero-grid,
.overview-grid,
.team-journey {
  display: grid;
  gap: 14px;
}

.team-hero-grid,
.overview-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin-top: 22px;
}

.team-journey {
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-top: 18px;
}

.hero-stat,
.overview-card,
.journey-chip,
.member-item,
.application-item,
.process-item {
  border-radius: 20px;
}

.hero-stat {
  padding: 18px;
  background: color-mix(in srgb, var(--cf-paper) 78%, transparent);
}

.hero-stat span,
.overview-card span,
.journey-chip span {
  color: var(--cf-ink-soft);
  font-size: 12px;
}

.hero-stat strong,
.overview-card strong {
  display: block;
  margin-top: 12px;
  font-size: 24px;
  line-height: 1.25;
  letter-spacing: -0.04em;
}

.journey-chip {
  padding: 16px;
  background: var(--cf-primary-soft);
}

.journey-chip strong {
  display: block;
  margin-top: 10px;
  font-size: 15px;
  line-height: 1.6;
}

.overview-card {
  padding: 18px;
  background: var(--cf-surface-soft);
}

.overview-card p,
.summary-panel p,
.flow-callout p,
.member-item p,
.application-item p,
.process-item p {
  margin: 10px 0 0;
  color: var(--cf-ink-soft);
  line-height: 1.75;
}

.summary-panel,
.flow-callout {
  margin-top: 20px;
  padding: 18px;
  border-radius: 20px;
}

.summary-panel {
  background: color-mix(in srgb, var(--cf-paper) 74%, transparent);
}

.flow-callout {
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--cf-primary-soft) 92%, transparent), transparent),
    color-mix(in srgb, var(--cf-paper) 76%, transparent);
  border: 1px solid color-mix(in srgb, var(--cf-primary) 12%, transparent);
}

.content-block {
  margin-top: 28px;
}

.section-head {
  margin-bottom: 14px;
}

.member-list,
.application-list,
.process-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.member-item,
.application-item,
.process-item {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: center;
  padding: 16px 18px;
  background: color-mix(in srgb, var(--cf-paper) 72%, transparent);
}

.member-copy,
.application-copy {
  flex: 1;
}

.member-side {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: flex-end;
}

.member-actions,
.actions,
.action-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
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

.action-list {
  margin-top: 18px;
}

@media (max-width: 1080px) {
  .team-hero-grid,
  .overview-grid,
  .team-journey {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 960px) {
  .header-row,
  .member-item,
  .application-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .member-side {
    align-items: flex-start;
  }
}
</style>
