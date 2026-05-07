<template>
  <div class="list-stack landing-shell">
    <section class="hero-stage">
      <HomeHeroCluster side="left" class="cluster-left" />

      <div class="hero-center">
        <div class="hero-eyebrow">CampusFlow Platform</div>
        <h1 class="hero-title">
          CampusFlow
          <span class="hero-title-cn">把校园活动从找机会推进到完成闭环</span>
        </h1>
        <p class="hero-copy">
          在首页先完成“看懂流程、判断适配、进入报名”三件事。筛选结果会直接承接到活动详情、组队报名、审核和签到反馈。
        </p>

        <div class="hero-cta">
          <el-button type="primary" round class="hero-button" @click="goPrimaryAction">进入主流程</el-button>
        </div>

        <div class="hero-meta">
          <span class="hero-meta-pill">活动总数 {{ activityStore.pageResult.total || 0 }}</span>
          <span class="hero-meta-pill">开放报名 {{ signupOpenCount }}</span>
          <span class="hero-meta-pill">团队协作 {{ requireTeamCount }}</span>
        </div>
      </div>

      <HomeHeroCluster side="right" class="cluster-right" />
    </section>

    <section id="ai-screening" class="glass-card ai-module">
      <div class="panel-head ai-module-head">
        <div>
          <div class="soft-tag">AI Assist</div>
          <h2 class="section-title">AI 活动筛选模块</h2>
          <p class="section-subtitle">上传文件。</p>
        </div>
      </div>

      <div class="ai-module-form">
          <el-form-item label="你的诉求">
            <el-input
              v-model="aiForm.prompt"
              type="textarea"
              :rows="5"
              placeholder="例如：找一个适合组队、偏技术实践的活动"
            />
          </el-form-item>

          <div class="ai-inline-grid ai-inline-grid-single">
            <el-form-item label="参与方式偏好">
              <el-select v-model="teamPreference" placeholder="不限">
                <el-option label="不限" value="all" />
                <el-option label="优先组队" value="team" />
                <el-option label="优先个人参与" value="solo" />
              </el-select>
            </el-form-item>
          </div>

          <div class="upload-panel">
            <div class="upload-copy">
              <strong>上传文件</strong>
              <p>支持 `.txt`、`.md`、`.json`、`.csv`。</p>
            </div>
            <label class="upload-trigger">
              <input type="file" accept=".txt,.md,.json,.csv,text/plain,application/json,text/csv" @change="handleFileChange" />
              <span>{{ aiForm.attachmentName || '选择文件并读取内容' }}</span>
            </label>
            <div class="upload-actions">
              <el-button round @click="useQuickPrompt('我想找一个能快速报名、流程清晰、近期可以参加的活动')">快速找近期活动</el-button>
              <el-button round @click="useQuickPrompt('我想找适合做作品集、偏技术和协作实践的活动')">偏技术协作</el-button>
              <el-button round @click="clearAttachment" :disabled="!aiForm.attachmentName">清空附件</el-button>
            </div>
          </div>

          <div class="ai-actions">
            <el-button type="primary" round :loading="screeningLoading" @click="runAiScreening">开始分析</el-button>
            <el-button round @click="applyAiResultToFilters" :disabled="!screening?.recommendedActivities.length">带入推荐条件</el-button>
            <el-button round @click="resetAiForm">重置 AI 工作台</el-button>
          </div>

          <div class="api-config-foot">
            配置在后端。
          </div>
      </div>

      <div class="ai-result-toggle">
        <div class="ai-result-status">
          <strong>分析结果</strong>
          <span>{{ screening ? screening.summary : '等待分析结果' }}</span>
        </div>
        <div class="ai-status-badges">
          <span v-if="screening" class="result-mode-badge">
            {{ screening.configStatus.configured ? '真实模型已启用' : '内置分析模式' }}
          </span>
          <el-button round @click="showAiResultDetails = !showAiResultDetails" :disabled="!screening">
            {{ showAiResultDetails ? '收起结果' : '展开结果' }}
          </el-button>
        </div>
      </div>

      <transition name="fade">
        <div v-if="screening && showAiResultDetails" class="ai-result-panel">
          <div class="ai-result-head">
          <div>
            <h3 class="section-title">筛选建议</h3>
            <p class="section-subtitle">关键结果。</p>
          </div>
        </div>

          <div class="result-summary">
            <p>{{ screening.summary }}</p>
          </div>

          <div class="result-chip-groups">
            <div>
              <span class="result-group-title">识别重点</span>
              <div class="cf-chip-row">
                <span v-for="item in screening.extractedContext" :key="item" class="cf-chip">{{ item }}</span>
              </div>
            </div>
            <div>
              <span class="result-group-title">推荐标签</span>
              <div class="cf-chip-row">
                <span v-for="item in screening.focusTags" :key="item" class="cf-chip">{{ item }}</span>
              </div>
            </div>
          </div>

          <div class="suggestion-list">
            <div v-for="item in screening.suggestedActions" :key="item" class="suggestion-item">
              {{ item }}
            </div>
          </div>

          <div class="recommendation-list">
            <article v-for="item in screening.recommendedActivities" :key="item.activityId" class="recommendation-card">
              <div class="recommendation-head">
                <div>
                  <strong>{{ item.title }}</strong>
                  <p>{{ item.reason }}</p>
                </div>
                <div class="recommendation-score">{{ item.score }}</div>
              </div>
              <div class="cf-chip-row">
                <span class="cf-chip">{{ item.type }}</span>
                <span class="cf-chip">{{ item.requireTeam ? '组队参与' : '个人参与' }}</span>
                <span class="cf-chip">{{ statusLabelMap[item.status] || item.status }}</span>
                <span v-for="highlight in item.matchHighlights" :key="highlight" class="cf-chip">{{ highlight }}</span>
              </div>
              <div class="recommendation-foot">
                <span>{{ item.nextStep }}</span>
                <div class="recommendation-actions">
                  <el-button round @click="locateRecommendation(item)">带入筛选</el-button>
                  <el-button type="primary" round @click="router.push(`/activities/${item.activityId}`)">进入活动</el-button>
                </div>
              </div>
            </article>
          </div>
        </div>
      </transition>
    </section>

    <section class="glass-card workflow-panel">
      <div class="panel-head">
        <div>
          <h2 class="section-title">核心流程</h2>
          <p class="section-subtitle">先判断活动是否合适，再进入报名、审核、签到和反馈闭环，不再靠用户自己猜下一步。</p>
        </div>
      </div>

      <div class="workflow-grid">
        <div v-for="item in workflows" :key="item.title" class="workflow-card">
          <div class="workflow-index">{{ item.step }}</div>
          <strong>{{ item.title }}</strong>
          <p>{{ item.caption }}</p>
          <el-button round class="workflow-button" @click="router.push(item.path)">{{ item.button }}</el-button>
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
          <ActivityCard :activity="activity" :index="index" />
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
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../../api'
import ActivityCard from '../../components/ActivityCard.vue'
import HomeHeroCluster from '../../components/HomeHeroCluster.vue'
import { useActivityStore } from '../../stores/activity'
import { useUserStore } from '../../stores/user'
import type { AiScreeningRecommendation, AiScreeningResult, AnnouncementItem } from '../../types'
import { statusLabelMap } from '../../utils/format'

const router = useRouter()
const userStore = useUserStore()
const activityStore = useActivityStore()
const announcements = ref<AnnouncementItem[]>([])
const screening = ref<AiScreeningResult | null>(null)
const screeningLoading = ref(false)
const showAiResultDetails = ref(false)
const teamPreference = ref<'all' | 'team' | 'solo'>('all')
const aiForm = reactive({
  prompt: '',
  attachmentName: '',
  attachmentText: ''
})

const signupOpenCount = computed(() =>
  activityStore.pageResult.records.filter((item) => item.status === 'signup_open').length
)

const requireTeamCount = computed(() =>
  activityStore.pageResult.records.filter((item) => item.requireTeam).length
)

const workflows = computed(() => [
  {
    step: '01',
    title: 'AI 预筛选',
    caption: '先根据诉求和上传材料缩小活动范围，减少无效浏览。',
    button: '开始分析',
    path: '/activities'
  },
  {
    step: '02',
    title: '进入报名',
    caption: '个人活动可直接报名，团队活动先创建或加入队伍。',
    button: '浏览活动',
    path: '/activities'
  },
  {
    step: '03',
    title: '队伍协作',
    caption: '队长维护成员、处理申请，再统一提交报名。',
    button: userStore.isLoggedIn ? '进入协作' : '登录后进入',
    path: userStore.isLoggedIn ? '/teams/join' : '/login'
  },
  {
    step: '04',
    title: '组织审核',
    caption: '组织者审核队伍或个人报名，结果自动进入通知中心。',
    button: ['organizer', 'admin'].includes(userStore.role) ? '处理审核' : '查看通知',
    path: ['organizer', 'admin'].includes(userStore.role) ? '/organizer/reviews' : '/notices'
  },
  {
    step: '05',
    title: '签到反馈',
    caption: '审核通过后进入签到，活动结束后沉淀反馈和复盘。',
    button: userStore.isLoggedIn ? '查看我的进展' : '登录查看',
    path: userStore.isLoggedIn ? '/dashboard' : '/login'
  }
])

const roleEntries = computed(() => [
  {
    title: '学生',
    caption: '浏览活动、走个人报名，或根据活动要求进入队伍协作。',
    button: userStore.isLoggedIn ? '查看活动' : '登录后参与',
    path: userStore.isLoggedIn ? '/activities' : '/login',
    primary: !userStore.isLoggedIn
  },
  {
    title: '队长',
    caption: '处理入队申请、维护成员并提交队伍报名。',
    button: userStore.isLoggedIn ? '进入协作' : '登录查看',
    path: userStore.isLoggedIn ? '/teams/join' : '/login',
    primary: userStore.role === 'captain'
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

const useQuickPrompt = (value: string) => {
  aiForm.prompt = value
}

const clearAttachment = () => {
  aiForm.attachmentName = ''
  aiForm.attachmentText = ''
}

const handleFileChange = async (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (file.size > 160 * 1024) {
    ElMessage.warning('文件请控制在 160KB 以内，便于首页快速分析')
    input.value = ''
    return
  }
  try {
    aiForm.attachmentText = await file.text()
    aiForm.attachmentName = file.name
    ElMessage.success(`已读取 ${file.name}`)
  } catch {
    ElMessage.error('文件读取失败，请更换为 txt、md、json 或 csv')
  } finally {
    input.value = ''
  }
}

const runAiScreening = async () => {
  if (!aiForm.prompt.trim() && !aiForm.attachmentText.trim()) {
    ElMessage.warning('请先输入活动诉求或上传一个说明文件')
    return
  }
  screeningLoading.value = true
  try {
    const response = await api.screenActivitiesWithAi({
      prompt: aiForm.prompt.trim(),
      attachmentName: aiForm.attachmentName || undefined,
      attachmentText: aiForm.attachmentText || undefined,
      requireTeam: teamPreference.value === 'all' ? undefined : teamPreference.value === 'team'
    })
    screening.value = response.data
    showAiResultDetails.value = false
  } catch (error) {
    const message = error instanceof Error ? error.message : 'AI 筛选失败'
    ElMessage.error(message)
  } finally {
    screeningLoading.value = false
  }
}

const locateRecommendation = async (item: AiScreeningRecommendation) => {
  activityStore.filters.keyword = item.title
  activityStore.filters.type = item.type
  activityStore.filters.requireTeam = item.requireTeam
  activityStore.filters.pageNum = 1
  await fetchActivities()
}

const applyAiResultToFilters = async () => {
  const target = screening.value?.recommendedActivities[0]
  if (!target) return
  await locateRecommendation(target)
}

const resetAiForm = () => {
  aiForm.prompt = ''
  aiForm.attachmentName = ''
  aiForm.attachmentText = ''
  teamPreference.value = 'all'
  screening.value = null
  showAiResultDetails.value = false
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
  max-width: 700px;
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
.ai-module,
.filter-panel {
  padding: 26px;
}

.ai-module {
  scroll-margin-top: 110px;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-start;
}

.ai-module-head {
  align-items: flex-start;
}

.ai-status-badges {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}

.ai-inline-note {
  max-width: 280px;
  color: var(--cf-ink-soft);
  font-size: 12px;
  line-height: 1.7;
  text-align: right;
}

.ai-module-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.12fr) minmax(320px, 0.88fr);
  gap: 18px;
  margin-top: 22px;
}

.ai-module-form,
.ai-module-result {
  padding: 22px;
  border-radius: 24px;
  background: var(--cf-surface-soft);
  border: 1px solid color-mix(in srgb, var(--cf-line) 84%, transparent);
}

.ai-inline-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(220px, 0.72fr);
  gap: 16px;
  align-items: start;
}

.ai-inline-grid-single {
  grid-template-columns: 1fr;
}

.api-inline-grid {
  margin-top: 4px;
}

.upload-panel,
.result-summary,
.ai-placeholder {
  margin-top: 18px;
  padding: 18px;
  border-radius: 20px;
  background: color-mix(in srgb, var(--cf-paper-strong) 70%, transparent);
}

.upload-copy p,
.ai-placeholder p,
.result-summary p {
  margin: 10px 0 0;
  color: var(--cf-ink-soft);
  line-height: 1.8;
  font-size: 13px;
}

.upload-trigger {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 104px;
  margin-top: 14px;
  border: 1px dashed color-mix(in srgb, var(--cf-primary) 28%, transparent);
  border-radius: 18px;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--cf-primary-soft) 92%, transparent), transparent),
    var(--cf-paper);
  cursor: pointer;
  transition: border-color 0.24s ease, transform 0.24s ease;
}

.upload-trigger:hover {
  transform: translateY(-2px);
  border-color: color-mix(in srgb, var(--cf-primary) 48%, transparent);
}

.upload-trigger input {
  display: none;
}

.upload-trigger span {
  padding: 0 20px;
  color: var(--cf-primary-deep);
  font-weight: 700;
  text-align: center;
}

.upload-actions,
.ai-actions,
.recommendation-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.upload-actions {
  margin-top: 14px;
}

.ai-actions {
  margin-top: 20px;
}

.api-config-foot {
  margin-top: 14px;
  color: var(--cf-ink-soft);
  font-size: 12px;
  line-height: 1.8;
}

.ai-result-toggle {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: center;
  margin-top: 18px;
  padding: 16px 18px;
  border-radius: 22px;
  background: color-mix(in srgb, var(--cf-paper) 74%, transparent);
  border: 1px solid color-mix(in srgb, var(--cf-line) 84%, transparent);
}

.ai-result-status {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.ai-result-status strong {
  font-size: 15px;
}

.ai-result-status span {
  color: var(--cf-ink-soft);
  font-size: 13px;
  line-height: 1.7;
}

.ai-module-result {
  margin-top: 18px;
}

.ai-result-head,
.recommendation-head,
.recommendation-foot,
.board-head {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-start;
}

.result-mode-badge {
  padding: 10px 14px;
  border-radius: 999px;
  background: var(--cf-accent-soft);
  color: var(--cf-accent);
  font-size: 12px;
  font-weight: 800;
}

.result-chip-groups {
  display: grid;
  gap: 16px;
  margin-top: 18px;
}

.result-group-title {
  display: block;
  margin-bottom: 10px;
  color: var(--cf-ink-soft);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.06em;
}

.suggestion-list,
.recommendation-list,
.bulletin-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 18px;
}

.suggestion-item {
  padding: 14px 16px;
  border-left: 3px solid color-mix(in srgb, var(--cf-primary) 38%, transparent);
  border-radius: 0 16px 16px 0;
  background: var(--cf-primary-soft);
  color: var(--cf-ink-soft);
  line-height: 1.75;
}

.recommendation-card,
.bulletin-item,
.role-card {
  padding: 18px;
  border-radius: 20px;
  background: color-mix(in srgb, var(--cf-paper) 70%, transparent);
}

.recommendation-head strong,
.bulletin-item strong,
.role-card strong {
  display: block;
  font-size: 16px;
}

.recommendation-head p,
.bulletin-item p,
.role-card p {
  margin: 8px 0 0;
  color: var(--cf-ink-soft);
  line-height: 1.8;
  font-size: 13px;
}

.recommendation-score {
  min-width: 58px;
  padding: 10px 12px;
  border-radius: 16px;
  background: var(--cf-success-soft);
  color: var(--cf-success);
  font-size: 22px;
  font-weight: 800;
  text-align: center;
}

.recommendation-foot {
  align-items: center;
  margin-top: 16px;
  color: var(--cf-ink-soft);
  font-size: 13px;
}

.workflow-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 14px;
  margin-top: 20px;
}

.workflow-card {
  display: flex;
  flex-direction: column;
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

.workflow-button {
  margin-top: auto;
  align-self: flex-start;
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
}

.role-card p {
  flex: 1;
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
  position: sticky;
  top: var(--stack-top);
}

.pagination-row {
  display: flex;
  justify-content: center;
}

@media (max-width: 1280px) {
  .hero-stage,
  .ai-module-grid,
  .overview-grid {
    grid-template-columns: 1fr;
  }

  .hero-stage {
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

  .workflow-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .activity-grid {
    gap: 28px;
  }
}

@media (max-width: 960px) {
  .ai-inline-grid,
  .role-grid,
  .filter-grid,
  .board-head {
    grid-template-columns: 1fr;
    display: grid;
  }

  .panel-head,
  .ai-result-toggle,
  .recommendation-foot,
  .ai-result-head {
    flex-direction: column;
  }

  .ai-status-badges {
    align-items: flex-start;
  }

  .ai-inline-note {
    text-align: left;
  }

  .workflow-grid {
    grid-template-columns: 1fr;
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
