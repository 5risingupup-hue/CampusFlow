<template>
  <div class="list-stack">
    <section class="hero-panel glass-card dashboard-hero">
      <div class="hero-top">
        <div class="hero-copy">
          <div class="soft-tag">Workspace</div>
          <h1 class="page-title">你好，{{ userStore.profile?.nickname || '同学' }}</h1>
          <p class="page-subtitle">
            把活动进展、协作入口、通知提醒和今日待办集中到同一页里，
            减少在“找页面”和“确认状态”上消耗的时间。
          </p>
        </div>

        <div class="hero-side">
          <div class="role-card">
            <span>当前身份</span>
            <strong>{{ roleLabelMap[userStore.role] || userStore.role }}</strong>
          </div>
          <el-button type="primary" round @click="router.push(primaryAction.path)">
            {{ primaryAction.label }}
          </el-button>
        </div>
      </div>
    </section>

    <section class="card-grid metrics-grid">
      <MetricCard label="活动总量" :value="overview?.activityCount ?? 0" caption="当前角色可见或可管理的活动数" />
      <MetricCard label="协作队伍" :value="overview?.teamCount ?? 0" caption="围绕活动形成的队伍与协作规模" />
      <MetricCard label="待处理事项" :value="overview?.pendingCount ?? 0" caption="待审核、待跟进或待确认的任务" />
      <MetricCard label="未读通知" :value="overview?.unreadCount ?? 0" caption="报名结果、公告和系统提醒" />
    </section>

    <section class="card-grid dashboard-main">
      <article class="glass-card task-panel">
        <div class="panel-head">
          <div>
            <h2 class="section-title">今日重点</h2>
            <p class="section-subtitle">优先处理对流程影响最大的事项，避免消息积压和审核延迟</p>
          </div>
        </div>

        <div class="task-list">
          <div v-for="item in focusItems" :key="item.label" class="task-item">
            <div>
              <div class="task-label">{{ item.label }}</div>
              <div class="task-value">{{ item.value }}</div>
              <p>{{ item.caption }}</p>
            </div>
            <el-button :type="item.primary ? 'primary' : undefined" round @click="router.push(item.path)">
              {{ item.button }}
            </el-button>
          </div>
        </div>
      </article>

      <article class="glass-card schedule-panel">
        <div class="panel-head">
          <div>
            <h2 class="section-title">近期排期</h2>
            <p class="section-subtitle">查看最近的活动节点，便于安排审核、签到和值班节奏</p>
          </div>
        </div>

        <div class="schedule-list">
          <article v-for="item in overview?.upcomingActivities || []" :key="item.id" class="schedule-item">
            <div class="schedule-date">
              <strong>{{ formatShortDate(item.startTime).split(' ')[0] }}</strong>
              <span>{{ formatShortDate(item.startTime).split(' ')[1] || '--' }}</span>
            </div>
            <div class="schedule-copy">
              <div class="schedule-title">{{ item.title }}</div>
              <div class="schedule-meta">{{ item.location }} · {{ item.organizerName }}</div>
            </div>
            <div class="schedule-side">
              <el-tag size="small" :type="statusTagTypeMap[item.status] || 'info'">
                {{ statusLabelMap[item.status] || item.status }}
              </el-tag>
              <el-button round @click="router.push(`/activities/${item.id}`)">查看</el-button>
            </div>
          </article>
          <el-empty v-if="!(overview?.upcomingActivities?.length)" description="暂无活动数据" />
        </div>
      </article>
    </section>

    <section class="card-grid lower-grid">
      <article class="glass-card chart-panel">
        <div class="panel-head">
          <div>
            <h2 class="section-title">活动类型分布</h2>
            <p class="section-subtitle">帮助你快速判断当前平台活动结构和资源投入方向</p>
          </div>
        </div>
        <div ref="chartRef" class="chart-box" />
      </article>

      <article class="glass-card quick-panel">
        <div class="panel-head">
          <div>
            <h2 class="section-title">快捷动作</h2>
            <p class="section-subtitle">把高频入口固定在这里，减少重复回主导航寻找</p>
          </div>
        </div>

        <div class="quick-grid">
          <div v-for="item in quickActions" :key="item.label" class="quick-card">
            <strong>{{ item.label }}</strong>
            <p>{{ item.caption }}</p>
            <el-button :type="item.primary ? 'primary' : undefined" round @click="router.push(item.path)">
              {{ item.button }}
            </el-button>
          </div>
        </div>
      </article>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { api } from '../../api'
import MetricCard from '../../components/MetricCard.vue'
import { useThemeStore } from '../../stores/theme'
import { useUserStore } from '../../stores/user'
import type { DashboardOverview } from '../../types'
import { formatShortDate, roleLabelMap, statusLabelMap, statusTagTypeMap } from '../../utils/format'

const router = useRouter()
const userStore = useUserStore()
const themeStore = useThemeStore()
const overview = ref<DashboardOverview | null>(null)
const chartRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null
let resizeHandler: (() => void) | null = null

const isOrganizer = computed(() => ['organizer', 'admin'].includes(userStore.role))
const isAdmin = computed(() => userStore.role === 'admin')

const primaryAction = computed(() => {
  if (isAdmin.value) {
    return { label: '进入公告治理', path: '/admin/announcements' }
  }
  if (isOrganizer.value) {
    return { label: '处理审核待办', path: '/organizer/reviews' }
  }
  if (userStore.role === 'captain') {
    return { label: '进入队伍协作', path: '/teams/join' }
  }
  return { label: '查看可参与活动', path: '/activities' }
})

const focusItems = computed(() => [
  {
    label: '待处理事项',
    value: overview.value?.pendingCount ?? 0,
    caption: isOrganizer.value ? '建议优先清空审核积压和待跟进事项。' : '建议优先查看最近影响参与进度的事项。',
    button: isOrganizer.value ? '立即处理' : '查看进展',
    path: isOrganizer.value ? '/organizer/reviews' : '/notices',
    primary: true
  },
  {
    label: '未读通知',
    value: overview.value?.unreadCount ?? 0,
    caption: '报名结果、公告广播和系统提醒都会统一沉淀到消息中心。',
    button: '查看消息',
    path: '/notices',
    primary: false
  },
  {
    label: '现场签到',
    value: overview.value?.signedCount ?? 0,
    caption: '签到进度能帮助你快速判断活动执行和到场情况。',
    button: '查看活动',
    path: '/activities',
    primary: false
  }
])

const quickActions = computed(() =>
  [
    {
      label: '活动广场',
      caption: '查看活动详情、规则和参与入口。',
      button: '浏览活动',
      path: '/activities',
      primary: !userStore.isLoggedIn
    },
    userStore.isLoggedIn
      ? {
          label: '队伍协作',
          caption: '查找队伍、处理入队和跟进提交状态。',
          button: '进入协作',
          path: '/teams/join',
          primary: userStore.role === 'captain'
        }
      : null,
    isOrganizer.value
      ? {
          label: '活动管理',
          caption: '创建、编辑和维护活动信息与时间窗口。',
          button: '管理活动',
          path: '/organizer/activities',
          primary: true
        }
      : null,
    isOrganizer.value
      ? {
          label: '审核中心',
          caption: '集中查看队伍报名并快速作出审核决策。',
          button: '处理审核',
          path: '/organizer/reviews',
          primary: false
        }
      : null,
    isAdmin.value
      ? {
          label: '公告治理',
          caption: '全站公告、制度更新和统一广播入口。',
          button: '发布公告',
          path: '/admin/announcements',
          primary: false
        }
      : null,
    {
      label: '消息中心',
      caption: '跟进报名结果、入队提醒和系统通知。',
      button: '查看消息',
      path: '/notices',
      primary: false
    }
  ].filter(Boolean) as Array<{ label: string; caption: string; button: string; path: string; primary: boolean }>
)

const renderChart = async () => {
  await nextTick()
  if (!chartRef.value || !overview.value) return
  chart ??= echarts.init(chartRef.value)
  const styles = getComputedStyle(document.documentElement)
  const lineColor = styles.getPropertyValue('--cf-line').trim()
  const inkSoft = styles.getPropertyValue('--cf-ink-soft').trim()
  const primary = styles.getPropertyValue('--cf-primary').trim()
  const primaryDeep = styles.getPropertyValue('--cf-primary-deep').trim()
  chart.setOption({
    grid: { left: 8, right: 12, top: 8, bottom: 8, containLabel: true },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: {
      type: 'value',
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: inkSoft },
      splitLine: { lineStyle: { color: lineColor } }
    },
    yAxis: {
      type: 'category',
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: inkSoft, fontWeight: 700 },
      data: overview.value.activityTypeDistribution.map((item) => item.name)
    },
    series: [
      {
        type: 'bar',
        data: overview.value.activityTypeDistribution.map((item) => item.value),
        barWidth: 18,
        itemStyle: {
          borderRadius: 999,
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: primary },
            { offset: 1, color: primaryDeep }
          ])
        }
      }
    ]
  })
}

onMounted(async () => {
  const response = await api.getDashboard()
  overview.value = response.data
  await renderChart()
  resizeHandler = () => chart?.resize()
  window.addEventListener('resize', resizeHandler)
})

onBeforeUnmount(() => {
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler)
  }
  chart?.dispose()
  chart = null
})

watch(() => overview.value, renderChart)
watch(() => themeStore.theme, renderChart)
</script>

<style scoped>
.dashboard-hero {
  padding-bottom: 32px;
}

.hero-top {
  display: flex;
  justify-content: space-between;
  gap: 22px;
  align-items: flex-start;
}

.hero-copy {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.hero-side {
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-width: 220px;
}

.role-card {
  padding: 18px 20px;
  border-radius: 20px;
  background: var(--cf-surface-soft);
}

.role-card span {
  color: var(--cf-ink-soft);
  font-size: 12px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.role-card strong {
  display: block;
  margin-top: 14px;
  font-size: 24px;
  letter-spacing: -0.04em;
}

.metrics-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.dashboard-main,
.lower-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.task-panel,
.schedule-panel,
.chart-panel,
.quick-panel {
  padding: 24px;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.task-list,
.schedule-list,
.quick-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 20px;
}

.task-item,
.schedule-item,
.quick-card {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: center;
  padding: 18px;
  border-radius: 18px;
  background: var(--cf-surface-soft);
}

.task-label {
  color: var(--cf-ink-soft);
  font-size: 12px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.task-value {
  margin-top: 12px;
  font-size: 34px;
  font-weight: 800;
  letter-spacing: -0.05em;
}

.task-item p,
.quick-card p {
  margin: 10px 0 0;
  color: var(--cf-ink-soft);
  line-height: 1.75;
  font-size: 13px;
}

.schedule-date {
  min-width: 78px;
  padding: 12px 10px;
  border-radius: 16px;
  background: var(--cf-primary-soft);
  color: var(--cf-primary-deep);
  text-align: center;
}

.schedule-date strong {
  display: block;
  font-size: 18px;
}

.schedule-date span {
  display: block;
  margin-top: 6px;
  font-size: 11px;
}

.schedule-copy {
  flex: 1;
}

.schedule-title {
  font-size: 15px;
  font-weight: 800;
}

.schedule-meta {
  margin-top: 6px;
  color: var(--cf-ink-soft);
  font-size: 13px;
}

.schedule-side {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: flex-end;
}

.chart-box {
  height: 340px;
  margin-top: 18px;
}

.quick-card {
  align-items: flex-end;
}

.quick-card strong {
  font-size: 15px;
}

@media (max-width: 1180px) {
  .metrics-grid,
  .dashboard-main,
  .lower-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 820px) {
  .hero-top,
  .task-item,
  .schedule-item,
  .quick-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero-side {
    min-width: 0;
    width: 100%;
  }

  .schedule-side {
    align-items: flex-start;
  }
}
</style>
