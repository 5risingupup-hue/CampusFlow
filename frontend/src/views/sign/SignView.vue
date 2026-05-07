<template>
  <div class="card-grid two-col">
    <section class="glass-card sign-panel">
      <div class="soft-tag">Check In</div>
      <h1 class="page-title">活动签到</h1>
      <p class="page-subtitle">输入活动和签到码后即可完成签到，系统会自动校验时间窗口、参与资格和重复签到状态。</p>

      <el-form :model="form" label-position="top">
        <el-form-item label="活动 ID">
          <el-input-number v-model="form.activityId" :min="1" />
        </el-form-item>
        <el-form-item label="签到码">
          <el-input v-model="form.signCode" placeholder="例如 SIGN2026" />
        </el-form-item>
        <el-button type="success" round @click="handleSign">立即签到</el-button>
      </el-form>
    </section>

    <aside class="glass-card status-panel">
      <h2 class="section-title">签到状态</h2>
      <p class="section-subtitle">签到结果会即时更新，便于确认是否处于有效签到窗口内。</p>
      <div v-if="status" class="status-card">
        <div class="status-line">
          <strong>{{ status.activityTitle }}</strong>
          <el-tag :type="statusTagTypeMap[status.status] || 'info'" round>
            {{ statusLabelMap[status.status] || status.status }}
          </el-tag>
        </div>
        <p>是否具备签到资格：{{ status.eligible ? '是' : '否' }}</p>
        <p>是否在签到时间窗口：{{ status.signWindowOpen ? '是' : '否' }}</p>
        <p>签到时间：{{ status.signTime ? formatDateTime(status.signTime) : '尚未签到' }}</p>
      </div>
      <el-empty v-else description="输入活动 ID 后可查看签到状态" />
    </aside>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../../api'
import type { SignStatus } from '../../types'
import { formatDateTime, statusLabelMap, statusTagTypeMap } from '../../utils/format'

const route = useRoute()
const form = reactive({
  activityId: Number(route.query.activityId || 0),
  signCode: ''
})
const status = ref<SignStatus | null>(null)

const fetchStatus = async () => {
  if (!form.activityId) return
  const response = await api.getSignStatus(form.activityId)
  status.value = response.data
}

const handleSign = async () => {
  try {
    const response: any = await api.checkIn(form)
    ElMessage.success(`签到成功，时间 ${formatDateTime(response.data.signTime as string)}`)
    await fetchStatus()
  } catch (error) {
    ElMessage.error((error as Error).message)
  }
}

watch(() => form.activityId, fetchStatus)

onMounted(fetchStatus)
</script>

<style scoped>
.sign-panel,
.status-panel {
  padding: 24px;
}

.status-card {
  margin-top: 18px;
  padding: 18px;
  border-radius: 18px;
  background: var(--cf-success-soft);
}

.status-line {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.status-card p {
  margin: 12px 0 0;
  color: var(--cf-ink-soft);
  line-height: 1.75;
}
</style>
