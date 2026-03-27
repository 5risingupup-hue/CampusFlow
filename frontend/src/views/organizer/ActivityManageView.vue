<template>
  <div class="list-stack">
    <section class="hero-panel glass-card manage-hero">
      <div class="hero-head">
        <div>
          <div class="soft-tag">Organizer Workspace</div>
          <h1 class="page-title">活动发布与管理</h1>
          <p class="page-subtitle">在同一页完成活动创建、时间窗口维护和详情回看，减少运营同学在多个页面之间来回切换。</p>
        </div>
        <div class="hero-side">
          <div class="hero-stat">
            <span>我的活动</span>
            <strong>{{ activities.length }}</strong>
          </div>
          <el-button type="primary" round @click="openCreate">发布新活动</el-button>
        </div>
      </div>
    </section>

    <section class="list-stack">
      <article v-for="item in activities" :key="item.id" class="glass-card manage-card">
        <div class="card-main">
          <div class="card-top">
            <div class="soft-tag">{{ item.type }}</div>
            <el-tag :type="statusTagTypeMap[item.status] || 'info'">
              {{ statusLabelMap[item.status] || item.status }}
            </el-tag>
          </div>
          <h3>{{ item.title }}</h3>
          <p>{{ item.location }} · {{ formatDateTime(item.startTime) }}</p>
        </div>
        <div class="card-actions">
          <el-button round @click="editActivity(item.id)">编辑</el-button>
          <el-button type="primary" round plain @click="router.push(`/activities/${item.id}`)">查看详情</el-button>
        </div>
      </article>
      <el-empty v-if="!activities.length" description="你还没有发布活动" />
    </section>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑活动' : '发布活动'" width="720px">
      <el-form :model="form" label-position="top" class="activity-form">
        <el-form-item label="活动标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="活动封面"><el-input v-model="form.coverUrl" placeholder="可填写图片 URL" /></el-form-item>
        <el-form-item label="活动类型"><el-input v-model="form.type" /></el-form-item>
        <el-form-item label="活动地点"><el-input v-model="form.location" /></el-form-item>
        <el-form-item label="活动描述"><el-input v-model="form.description" type="textarea" :rows="4" /></el-form-item>
        <div class="form-grid">
          <el-form-item label="开始时间"><el-date-picker v-model="form.startTime" type="datetime" value-format="YYYY-MM-DD[T]HH:mm:ss" /></el-form-item>
          <el-form-item label="结束时间"><el-date-picker v-model="form.endTime" type="datetime" value-format="YYYY-MM-DD[T]HH:mm:ss" /></el-form-item>
          <el-form-item label="报名截止"><el-date-picker v-model="form.signupDeadline" type="datetime" value-format="YYYY-MM-DD[T]HH:mm:ss" /></el-form-item>
          <el-form-item label="签到开始"><el-date-picker v-model="form.signStartTime" type="datetime" value-format="YYYY-MM-DD[T]HH:mm:ss" /></el-form-item>
          <el-form-item label="签到结束"><el-date-picker v-model="form.signEndTime" type="datetime" value-format="YYYY-MM-DD[T]HH:mm:ss" /></el-form-item>
          <el-form-item label="签到码"><el-input v-model="form.signCode" /></el-form-item>
          <el-form-item label="最小人数"><el-input-number v-model="form.minTeamSize" :min="1" /></el-form-item>
          <el-form-item label="最大人数"><el-input-number v-model="form.maxTeamSize" :min="1" /></el-form-item>
          <el-form-item label="活动状态">
            <el-select v-model="form.status">
              <el-option label="已发布" value="published" />
              <el-option label="报名中" value="signup_open" />
              <el-option label="报名截止" value="signup_closed" />
              <el-option label="已结束" value="finished" />
            </el-select>
          </el-form-item>
          <el-form-item label="需要组队">
            <el-switch v-model="form.requireTeam" />
          </el-form-item>
        </div>
        <el-form-item label="标签"><el-input v-model="form.tags" placeholder="使用英文逗号分隔" /></el-form-item>
        <el-form-item label="结果总结"><el-input v-model="form.resultSummary" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存活动</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../../api'
import type { ActivityCard, ActivityDetail } from '../../types'
import { formatDateTime, statusLabelMap, statusTagTypeMap } from '../../utils/format'

const router = useRouter()
const activities = ref<ActivityCard[]>([])
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const form = reactive<any>({
  title: '',
  coverUrl: '',
  description: '',
  type: '',
  location: '',
  startTime: '',
  endTime: '',
  signupDeadline: '',
  requireTeam: true,
  minTeamSize: 3,
  maxTeamSize: 5,
  status: 'signup_open',
  tags: '',
  signCode: '',
  signStartTime: '',
  signEndTime: '',
  resultSummary: ''
})

const fetchActivities = async () => {
  const response = await api.getMyActivities()
  activities.value = response.data
}

const resetForm = () => {
  Object.assign(form, {
    title: '',
    coverUrl: '',
    description: '',
    type: '',
    location: '',
    startTime: '',
    endTime: '',
    signupDeadline: '',
    requireTeam: true,
    minTeamSize: 3,
    maxTeamSize: 5,
    status: 'signup_open',
    tags: '',
    signCode: '',
    signStartTime: '',
    signEndTime: '',
    resultSummary: ''
  })
}

const openCreate = () => {
  editingId.value = null
  resetForm()
  dialogVisible.value = true
}

const editActivity = async (id: number) => {
  const response = await api.getActivityDetail(id)
  const detail = response.data as ActivityDetail
  editingId.value = id
  Object.assign(form, detail)
  form.tags = detail.tags.join(',')
  dialogVisible.value = true
}

const submitForm = async () => {
  try {
    if (editingId.value) {
      await api.updateActivity(editingId.value, form)
    } else {
      await api.createActivity(form)
    }
    ElMessage.success('活动保存成功')
    dialogVisible.value = false
    await fetchActivities()
  } catch (error) {
    ElMessage.error((error as Error).message)
  }
}

onMounted(fetchActivities)
</script>

<style scoped>
.hero-head {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-start;
}

.hero-side {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 200px;
}

.hero-stat {
  padding: 18px;
  border-radius: 20px;
  background: var(--cf-surface-soft);
}

.hero-stat span {
  color: var(--cf-ink-soft);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.hero-stat strong {
  display: block;
  margin-top: 14px;
  font-size: 28px;
}

.manage-card {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: center;
  padding: 24px;
}

.card-main {
  flex: 1;
}

.card-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.manage-card h3 {
  margin: 14px 0 10px;
  font-size: 28px;
  letter-spacing: -0.04em;
}

.manage-card p {
  margin: 0;
  color: var(--cf-ink-soft);
}

.card-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.activity-form .form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0 16px;
}

@media (max-width: 900px) {
  .hero-head,
  .manage-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero-side {
    min-width: 0;
    width: 100%;
  }

  .activity-form .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
