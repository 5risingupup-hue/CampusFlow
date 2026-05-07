<template>
  <div class="list-stack">
    <section class="hero-panel glass-card review-hero">
      <div class="hero-head">
        <div>
          <div class="soft-tag">Review Center</div>
          <h1 class="page-title">报名审核中心</h1>
          <p class="page-subtitle">
            把待审核队伍集中到一个工作面板里处理，审核结果会自动写入通知并同步给申请方，
            减少线下沟通和重复确认。
          </p>
        </div>

        <div class="hero-stats">
          <div class="hero-stat">
            <span>当前列表</span>
            <strong>{{ page.total }}</strong>
          </div>
          <div class="hero-stat">
            <span>待处理</span>
            <strong>{{ pendingCount }}</strong>
          </div>
          <div class="hero-stat">
            <span>已通过</span>
            <strong>{{ approvedCount }}</strong>
          </div>
          <div class="hero-stat">
            <span>已驳回</span>
            <strong>{{ rejectedCount }}</strong>
          </div>
        </div>
      </div>
    </section>

    <section class="glass-card filter-panel">
      <div class="panel-head">
        <div>
          <h2 class="section-title">筛选审核任务</h2>
          <p class="section-subtitle">按状态和说明关键词快速定位需要优先处理的报名记录</p>
        </div>
      </div>

      <el-form :model="query" class="filter-form">
        <div class="filter-grid">
          <el-form-item label="状态">
            <el-select v-model="query.status" clearable placeholder="全部">
              <el-option label="待处理" value="pending" />
              <el-option label="已通过" value="approved" />
              <el-option label="已拒绝" value="rejected" />
            </el-select>
          </el-form-item>
          <el-form-item label="说明关键词">
            <el-input v-model="query.keyword" clearable placeholder="搜索申请说明" />
          </el-form-item>
          <div class="filter-actions">
            <el-button type="primary" round @click="fetchReviews">查询</el-button>
            <el-button round @click="resetFilters">重置条件</el-button>
          </div>
        </div>
      </el-form>
    </section>

    <section class="glass-card table-panel">
      <el-table :data="page.records" stripe>
        <el-table-column label="类型" width="120">
          <template #default="{ row }">
            {{ statusLabelMap[row.type] || row.type }}
          </template>
        </el-table-column>
        <el-table-column prop="teamName" label="报名对象" min-width="180" />
        <el-table-column prop="activityTitle" label="活动" min-width="180" />
        <el-table-column prop="memberCount" label="人数" width="100" />
        <el-table-column label="提交时间" min-width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="statusTagTypeMap[row.status] || 'info'" round>
              {{ statusLabelMap[row.status] || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="230">
          <template #default="{ row }">
            <el-button size="small" @click="openDetail(row)">查看</el-button>
            <el-button v-if="row.status === 'pending'" size="small" type="success" @click="review(row.id, true)">通过</el-button>
            <el-button v-if="row.status === 'pending'" size="small" type="danger" @click="review(row.id, false)">驳回</el-button>
          </template>
        </el-table-column>
      </el-table>
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

    <el-drawer v-model="drawerVisible" title="报名详情" size="460px">
      <div v-if="currentReview" class="list-stack">
        <div class="review-block">
          <strong>报名对象</strong>
          <p>{{ currentReview.teamName }}</p>
        </div>
        <div class="review-block">
          <strong>报名类型</strong>
          <p>{{ statusLabelMap[currentReview.type] || currentReview.type }}</p>
        </div>
        <div class="review-block">
          <strong>活动</strong>
          <p>{{ currentReview.activityTitle }}</p>
        </div>
        <div class="review-block">
          <strong>成员数</strong>
          <p>{{ currentReview.memberCount }}</p>
        </div>
        <div class="review-block">
          <strong>报名说明</strong>
          <p>{{ currentReview.reason || '未填写报名说明' }}</p>
        </div>
        <div class="review-block">
          <strong>审核备注</strong>
          <p>{{ currentReview.reviewComment || '暂无备注' }}</p>
        </div>

        <div v-if="currentReview.status === 'pending'" class="drawer-actions">
          <el-button type="success" round @click="review(currentReview.id, true)">通过</el-button>
          <el-button type="danger" round @click="review(currentReview.id, false)">驳回</el-button>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '../../api'
import type { PageResult, ReviewItem } from '../../types'
import { formatDateTime, statusLabelMap, statusTagTypeMap } from '../../utils/format'

const query = reactive({
  status: '',
  keyword: '',
  pageNum: 1,
  pageSize: 10
})
const page = ref<PageResult<ReviewItem>>({ total: 0, records: [] })
const drawerVisible = ref(false)
const currentReview = ref<ReviewItem | null>(null)

const pendingCount = computed(() => page.value.records.filter((item) => item.status === 'pending').length)
const approvedCount = computed(() => page.value.records.filter((item) => item.status === 'approved').length)
const rejectedCount = computed(() => page.value.records.filter((item) => item.status === 'rejected').length)

const fetchReviews = async () => {
  const response = await api.getReviews(query)
  page.value = response.data
}

const resetFilters = async () => {
  query.status = ''
  query.keyword = ''
  query.pageNum = 1
  await fetchReviews()
}

const handlePageChange = async (pageNum: number) => {
  query.pageNum = pageNum
  await fetchReviews()
}

const openDetail = (row: ReviewItem) => {
  currentReview.value = row
  drawerVisible.value = true
}

const review = async (id: number, approve: boolean) => {
  const { value } = await ElMessageBox.prompt(
    approve ? '可选填写通过备注' : '驳回时建议填写原因',
    approve ? '通过审核' : '驳回审核',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPlaceholder: approve ? '例如：请提前准备路演材料' : '例如：队伍人数不足'
    }
  )
  if (approve) {
    await api.approveReview(id, { comment: value })
  } else {
    await api.rejectReview(id, { comment: value })
  }
  ElMessage.success(approve ? '审核通过' : '审核驳回')
  drawerVisible.value = false
  currentReview.value = null
  await fetchReviews()
}

onMounted(fetchReviews)
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
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  min-width: 460px;
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

.filter-panel,
.table-panel {
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

.pagination-row {
  display: flex;
  justify-content: center;
}

.review-block {
  padding: 16px 18px;
  border-radius: 18px;
  background: var(--cf-surface-soft);
}

.review-block p {
  margin: 10px 0 0;
  color: var(--cf-ink-soft);
  line-height: 1.8;
}

.drawer-actions {
  display: flex;
  gap: 10px;
}

@media (max-width: 1100px) {
  .hero-head,
  .filter-grid {
    grid-template-columns: 1fr;
    display: grid;
  }

  .hero-stats {
    min-width: 0;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .hero-stats {
    grid-template-columns: 1fr;
  }
}
</style>
