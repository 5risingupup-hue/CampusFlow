<template>
  <div class="list-stack">
    <section class="hero-panel glass-card notice-hero">
      <div class="hero-head">
        <div>
          <div class="soft-tag">Notification Center</div>
          <h1 class="page-title">消息通知中心</h1>
          <p class="page-subtitle">统一查看报名审核结果、入队消息、系统公告和活动提醒，避免信息散落在多个入口。</p>
        </div>

        <div class="hero-stats">
          <div class="hero-stat">
            <span>当前列表</span>
            <strong>{{ page.total }}</strong>
          </div>
          <div class="hero-stat">
            <span>未读消息</span>
            <strong>{{ unreadCount }}</strong>
          </div>
        </div>
      </div>

      <div class="hero-actions">
        <el-button round @click="fetchNotices">刷新</el-button>
        <el-button type="primary" round @click="markAllRead">全部已读</el-button>
      </div>
    </section>

    <section class="glass-card filter-panel">
      <div class="panel-head">
        <div>
          <h2 class="section-title">筛选消息</h2>
          <p class="section-subtitle">按已读状态或消息类型快速缩小范围，优先处理影响流程推进的提醒</p>
        </div>
      </div>

      <el-form :model="query" class="filter-form">
        <div class="filter-grid">
          <el-form-item label="已读状态">
            <el-select v-model="query.isRead" clearable placeholder="全部">
              <el-option :value="false" label="未读" />
              <el-option :value="true" label="已读" />
            </el-select>
          </el-form-item>
          <el-form-item label="类型">
            <el-input v-model="query.type" clearable placeholder="如 review_result / announcement" />
          </el-form-item>
          <div class="filter-actions">
            <el-button type="primary" round @click="fetchNotices">筛选</el-button>
            <el-button round @click="resetFilters">重置条件</el-button>
          </div>
        </div>
      </el-form>
    </section>

    <section class="list-stack">
      <article v-for="item in page.records" :key="item.id" class="glass-card notice-card">
        <div class="notice-top">
          <div class="notice-main">
            <div class="notice-title-row">
              <h3>{{ item.title }}</h3>
              <el-tag size="small" :type="item.isRead ? 'info' : 'primary'" round>
                {{ item.isRead ? '已读' : '未读' }}
              </el-tag>
            </div>
            <p>{{ item.content }}</p>
          </div>

          <div class="notice-side">
            <span>{{ formatDateTime(item.createdAt) }}</span>
            <div class="notice-actions">
              <el-button v-if="!item.isRead" type="primary" round plain @click="markOne(item.id)">标记已读</el-button>
            </div>
          </div>
        </div>
      </article>
      <el-empty v-if="!page.records.length" description="当前没有消息" />
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
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../../api'
import { useNoticeStore } from '../../stores/notice'
import type { NotificationItem, PageResult } from '../../types'
import { formatDateTime } from '../../utils/format'

const noticeStore = useNoticeStore()
const query = reactive({
  isRead: undefined as boolean | undefined,
  type: '',
  pageNum: 1,
  pageSize: 12
})
const page = ref<PageResult<NotificationItem>>({ total: 0, records: [] })

const unreadCount = computed(() => page.value.records.filter((item) => !item.isRead).length)

const fetchNotices = async () => {
  const response = await api.getNotices(query)
  page.value = response.data
  await noticeStore.fetchUnreadCount()
}

const resetFilters = async () => {
  query.isRead = undefined
  query.type = ''
  query.pageNum = 1
  await fetchNotices()
}

const handlePageChange = async (pageNum: number) => {
  query.pageNum = pageNum
  await fetchNotices()
}

const markOne = async (id: number) => {
  await api.markNoticeRead([id])
  ElMessage.success('已标记为已读')
  await fetchNotices()
}

const markAllRead = async () => {
  await api.markAllRead()
  ElMessage.success('全部消息已读')
  await fetchNotices()
}

onMounted(fetchNotices)
</script>

<style scoped>
.hero-head {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-start;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  min-width: 250px;
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

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 20px;
}

.filter-panel,
.notice-card {
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

.notice-top {
  display: flex;
  justify-content: space-between;
  gap: 18px;
}

.notice-main {
  flex: 1;
}

.notice-title-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.notice-title-row h3 {
  margin: 0;
}

.notice-main p {
  margin: 12px 0 0;
  color: var(--cf-ink-soft);
  line-height: 1.8;
}

.notice-side {
  min-width: 160px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  align-items: flex-end;
  color: var(--cf-ink-soft);
  font-size: 13px;
}

.pagination-row {
  display: flex;
  justify-content: center;
}

@media (max-width: 900px) {
  .hero-head,
  .notice-top,
  .filter-grid {
    grid-template-columns: 1fr;
    display: grid;
  }

  .hero-stats {
    min-width: 0;
  }

  .notice-side {
    min-width: 0;
    align-items: flex-start;
  }
}
</style>
