<template>
  <div v-if="teamStore.currentTeam" class="card-grid two-col">
    <section class="glass-card detail-panel">
      <div class="header-row">
        <div>
          <div class="soft-tag">{{ teamStore.currentTeam.activityTitle }}</div>
          <h1 class="page-title">{{ teamStore.currentTeam.teamName }}</h1>
          <p class="page-subtitle">
            {{ teamStore.currentTeam.leaderName }} 带队 · 当前 {{ teamStore.currentTeam.currentSize }} /
            {{ teamStore.currentTeam.maxTeamSize }} 人
          </p>
        </div>
        <el-tag :type="statusTagTypeMap[teamStore.currentTeam.status] || 'info'" round>
          {{ statusLabelMap[teamStore.currentTeam.status] || teamStore.currentTeam.status }}
        </el-tag>
      </div>

      <div class="overview-grid">
        <div class="overview-card">
          <span>邀请码</span>
          <strong>{{ teamStore.currentTeam.inviteCode }}</strong>
          <p>可用于线下快速确认队伍信息</p>
        </div>
        <div class="overview-card">
          <span>报名门槛</span>
          <strong>{{ teamStore.currentTeam.minTeamSize }} - {{ teamStore.currentTeam.maxTeamSize }} 人</strong>
          <p>系统会在提交报名时自动校验人数</p>
        </div>
        <div class="overview-card">
          <span>待审核申请</span>
          <strong>{{ teamStore.currentTeam.pendingApplications.length }}</strong>
          <p>队长可直接在本页完成审批</p>
        </div>
      </div>

      <div class="summary-panel">
        <p><strong>队伍口号：</strong>{{ teamStore.currentTeam.slogan || '暂无口号' }}</p>
        <p><strong>队伍简介：</strong>{{ teamStore.currentTeam.description || '暂无简介' }}</p>
      </div>

      <div class="content-block">
        <h2 class="section-title">成员列表</h2>
        <div class="member-list">
          <div v-for="member in teamStore.currentTeam.members" :key="member.userId" class="member-item">
            <div>
              <strong>{{ member.nickname }}</strong>
              <p>{{ member.memberRole }} · {{ member.joinStatus }}</p>
            </div>
            <span>{{ member.joinedAt ? formatDateTime(member.joinedAt) : '待加入' }}</span>
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
        <div class="action-list">
          <el-button round @click="copyInviteCode">复制邀请码</el-button>
          <el-button
            v-if="teamStore.currentTeam.canManage"
            type="primary"
            round
            @click="submitSignup"
          >
            提交队伍报名
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
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '../../api'
import { useTeamStore } from '../../stores/team'
import { formatDateTime, statusLabelMap, statusTagTypeMap } from '../../utils/format'

const route = useRoute()
const router = useRouter()
const teamStore = useTeamStore()

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

onMounted(loadTeam)
</script>

<style scoped>
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

.overview-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 22px;
}

.overview-card {
  padding: 18px;
  border-radius: 20px;
  background: var(--cf-surface-soft);
}

.overview-card span {
  color: var(--cf-ink-soft);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.overview-card strong {
  display: block;
  margin-top: 14px;
  font-size: 24px;
  line-height: 1.2;
  letter-spacing: -0.04em;
}

.overview-card p {
  margin: 10px 0 0;
  color: var(--cf-ink-soft);
  font-size: 13px;
  line-height: 1.7;
}

.summary-panel {
  margin-top: 20px;
  padding: 18px;
  border-radius: 20px;
  background: var(--cf-primary-soft);
}

.summary-panel p {
  margin: 8px 0;
  line-height: 1.8;
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
  border-radius: 18px;
  background: var(--cf-surface-soft);
}

.member-item p,
.application-item p,
.process-item p {
  margin: 8px 0 0;
  color: var(--cf-ink-soft);
  line-height: 1.75;
}

.application-copy {
  flex: 1;
}

.actions,
.action-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.action-list {
  margin-top: 18px;
}

@media (max-width: 960px) {
  .overview-grid {
    grid-template-columns: 1fr;
  }

  .header-row,
  .member-item,
  .application-item {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
