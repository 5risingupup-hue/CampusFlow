<template>
  <div class="list-stack">
    <section class="hero-panel glass-card join-hero">
      <div class="hero-head">
        <div>
          <div class="soft-tag">Team Plaza</div>
          <h1 class="page-title">队伍广场</h1>
          <p class="page-subtitle">
            所有学生都可以在这里查看正在招募的队伍、当前人数和剩余席位。
            创建队伍的人就是队长，申请加入并审核通过的人才是队员。
          </p>
        </div>

        <div class="hero-side">
          <div class="hero-stats">
            <div class="hero-stat">
              <span>可见队伍</span>
              <strong>{{ page.total }}</strong>
            </div>
            <div class="hero-stat">
              <span>剩余席位</span>
              <strong>{{ openSeatCount }}</strong>
            </div>
            <div class="hero-stat">
              <span>我的申请</span>
              <strong>{{ appliedCount }}</strong>
            </div>
          </div>
          <el-button type="primary" round @click="goCreateTeam">创建我的队伍</el-button>
        </div>
      </div>
    </section>

    <section class="glass-card filter-panel">
      <div class="panel-head">
        <div>
          <h2 class="section-title">筛选队伍</h2>
          <p class="section-subtitle">先按活动范围和关键词缩小结果，再查看详情或直接提交申请</p>
        </div>
      </div>

      <el-form :model="query" class="filter-form">
        <div class="filter-grid">
          <el-form-item label="活动 ID">
            <el-input v-model.number="query.activityId" clearable placeholder="可从活动详情页带入" />
          </el-form-item>
          <el-form-item label="队伍关键词">
            <el-input v-model="query.keyword" clearable placeholder="如 Spark / Masters" />
          </el-form-item>
          <div class="filter-actions">
            <el-button type="primary" round @click="fetchTeams">查询队伍</el-button>
            <el-button round @click="goCreateTeam">创建队伍</el-button>
            <el-button round @click="resetFilters">重置条件</el-button>
          </div>
        </div>
      </el-form>
    </section>

    <section class="team-grid">
      <article v-for="team in page.records" :key="team.id" class="glass-card team-card">
        <div class="team-head">
          <div>
            <h3>{{ team.teamName }}</h3>
            <p>{{ team.activityTitle }}</p>
          </div>
          <el-tag :type="statusTagTypeMap[team.status] || 'info'" round>
            {{ statusLabelMap[team.status] || team.status }}
          </el-tag>
        </div>

        <div class="team-meta-grid">
          <div class="meta-item">
            <span>队长</span>
            <strong>{{ team.leaderName }}</strong>
          </div>
          <div class="meta-item">
            <span>当前人数</span>
            <strong>{{ team.currentSize }} / {{ team.maxTeamSize }}</strong>
          </div>
          <div class="meta-item">
            <span>剩余席位</span>
            <strong>{{ team.maxTeamSize - team.currentSize }}</strong>
          </div>
        </div>

        <p class="summary">{{ team.description || team.slogan || '队长暂未补充详细介绍。' }}</p>

        <div class="team-actions">
          <el-button round @click="router.push(`/teams/${team.id}`)">查看详情</el-button>
          <el-button
            type="primary"
            round
            :disabled="!team.joined && !team.canApply"
            @click="handleTeamAction(team)"
          >
            {{ teamActionText(team) }}
          </el-button>
        </div>
      </article>
      <el-empty v-if="!page.records.length" description="暂无可加入队伍">
        <el-button type="primary" round @click="goCreateTeam">创建第一个队伍</el-button>
      </el-empty>
    </section>

    <section class="pagination-row" v-if="page.total > query.pageSize">
      <el-pagination
        layout="prev, pager, next"
        :total="page.total"
        :page-size="query.pageSize"
        :current-page="query.pageNum"
        @current-change="handlePageChange"
      />
    </section>

    <el-dialog v-model="dialogVisible" title="提交入队申请" width="520px">
      <el-input v-model="applyReason" type="textarea" :rows="4" placeholder="简要说明你的能力或加入理由" />
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitApply">确认申请</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../../api'
import type { PageResult, TeamListItem } from '../../types'
import { statusLabelMap, statusTagTypeMap } from '../../utils/format'

const route = useRoute()
const router = useRouter()
const query = reactive({
  activityId: Number(route.query.activityId || 0) || undefined,
  keyword: '',
  pageNum: 1,
  pageSize: 12
})
const page = ref<PageResult<TeamListItem>>({ total: 0, records: [] })
const dialogVisible = ref(false)
const currentTeamId = ref<number | null>(null)
const applyReason = ref('')

const openSeatCount = computed(() =>
  page.value.records.reduce((total, item) => total + Math.max(item.maxTeamSize - item.currentSize, 0), 0)
)
const appliedCount = computed(() => page.value.records.filter((item) => item.applied).length)

const fetchTeams = async () => {
  const response = await api.getJoinableTeams(query)
  page.value = response.data
}

const resetFilters = async () => {
  query.activityId = undefined
  query.keyword = ''
  query.pageNum = 1
  await fetchTeams()
}

const handlePageChange = async (pageNum: number) => {
  query.pageNum = pageNum
  await fetchTeams()
}

const goCreateTeam = () => {
  router.push(query.activityId ? `/teams/create?activityId=${query.activityId}` : '/teams/create')
}

const teamActionText = (team: TeamListItem) => {
  if (team.joined) return '进入队伍'
  if (team.applied) return '审核中'
  if (team.canApply) return '申请加入'
  return '不可申请'
}

const handleTeamAction = (team: TeamListItem) => {
  if (team.joined) {
    router.push(`/teams/${team.id}`)
    return
  }
  if (!team.canApply) return
  currentTeamId.value = team.id
  dialogVisible.value = true
}

const submitApply = async () => {
  if (!currentTeamId.value) return
  try {
    await api.applyJoinTeam(currentTeamId.value, { reason: applyReason.value })
    ElMessage.success('申请已提交')
    dialogVisible.value = false
    applyReason.value = ''
    await fetchTeams()
  } catch (error) {
    ElMessage.error((error as Error).message)
  }
}

onMounted(fetchTeams)
</script>

<style scoped>
.hero-head {
  display: flex;
  justify-content: space-between;
  gap: 22px;
  align-items: flex-start;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.hero-side {
  display: grid;
  gap: 14px;
  min-width: 420px;
}

.hero-stat {
  padding: 18px;
  border-radius: 20px;
  background: var(--cf-surface-soft);
}

.hero-stat span {
  color: var(--cf-ink-soft);
  font-size: 12px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.hero-stat strong {
  display: block;
  margin-top: 14px;
  font-size: 28px;
  letter-spacing: -0.04em;
}

.filter-panel {
  padding: 24px;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.filter-grid {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 16px;
  align-items: end;
}

.filter-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding-bottom: 2px;
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.team-card {
  padding: 24px;
}

.team-head {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: flex-start;
}

.team-head h3 {
  margin: 0;
  font-size: 26px;
  letter-spacing: -0.04em;
}

.team-head p {
  margin: 10px 0 0;
  color: var(--cf-ink-soft);
}

.team-meta-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 18px;
}

.meta-item {
  padding: 15px;
  border-radius: 18px;
  background: var(--cf-surface-soft);
}

.meta-item span {
  color: var(--cf-ink-soft);
  font-size: 12px;
}

.meta-item strong {
  display: block;
  margin-top: 8px;
}

.summary {
  margin: 18px 0 0;
  color: var(--cf-ink-soft);
  line-height: 1.8;
}

.team-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 20px;
}

.pagination-row {
  display: flex;
  justify-content: center;
}

@media (max-width: 1180px) {
  .team-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 960px) {
  .hero-head,
  .filter-grid {
    grid-template-columns: 1fr;
    display: grid;
  }

  .hero-side,
  .hero-stats,
  .team-meta-grid {
    min-width: 0;
    grid-template-columns: 1fr;
  }
}
</style>
