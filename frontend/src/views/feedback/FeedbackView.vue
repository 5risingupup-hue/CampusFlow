<template>
  <div class="card-grid two-col">
    <section class="glass-card form-panel">
      <div class="soft-tag">Feedback</div>
      <h1 class="page-title">活动反馈</h1>
      <p class="page-subtitle">活动结束并签到后即可评价，反馈会回流到活动详情页，帮助后续参与者和组织者持续优化体验。</p>

      <el-form :model="form" label-position="top">
        <el-form-item label="评分">
          <el-rate v-model="form.score" />
        </el-form-item>
        <el-form-item label="文字反馈">
          <el-input v-model="form.content" type="textarea" :rows="5" placeholder="欢迎补充你对流程、通知和组织体验的评价" />
        </el-form-item>
        <el-form-item label="快捷标签">
          <el-checkbox-group v-model="form.tags">
            <el-checkbox label="流程清晰" />
            <el-checkbox label="通知及时" />
            <el-checkbox label="组织有序" />
            <el-checkbox label="协作顺畅" />
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="是否愿意再次参加类似活动">
          <el-switch v-model="form.willingRejoin" />
        </el-form-item>
        <el-button type="warning" round @click="handleSubmit">提交反馈</el-button>
      </el-form>
    </section>

    <aside class="glass-card summary-panel">
      <h2 class="section-title">历史反馈摘要</h2>
      <p class="section-subtitle">当前活动已有 {{ summary?.total ?? 0 }} 条反馈，平均分 {{ (summary?.averageScore ?? 0).toFixed(1) }}</p>
      <div class="list-stack summary-list">
        <div v-for="item in summary?.records || []" :key="`${item.userId}-${item.createdAt}`" class="feedback-item">
          <strong>{{ item.nickname }}</strong>
          <p>{{ item.content || '未填写文字反馈' }}</p>
          <span>{{ item.score }} / 5</span>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../../api'
import type { FeedbackSummary } from '../../types'

const route = useRoute()
const router = useRouter()
const activityId = Number(route.params.activityId)
const summary = ref<FeedbackSummary | null>(null)
const form = reactive({
  activityId,
  score: 5,
  content: '',
  tags: [] as string[],
  willingRejoin: true
})

const fetchSummary = async () => {
  const response = await api.getFeedback(activityId)
  summary.value = response.data
}

const handleSubmit = async () => {
  try {
    await api.submitFeedback(form)
    ElMessage.success('反馈提交成功')
    router.push(`/activities/${activityId}`)
  } catch (error) {
    ElMessage.error((error as Error).message)
  }
}

onMounted(fetchSummary)
</script>

<style scoped>
.form-panel,
.summary-panel {
  padding: 24px;
}

.summary-list {
  margin-top: 20px;
}

.feedback-item {
  padding: 16px 18px;
  border-radius: 18px;
  background: var(--cf-warning-soft);
}

.feedback-item p {
  margin: 10px 0;
  color: var(--cf-ink-soft);
  line-height: 1.75;
}

.feedback-item span {
  font-size: 13px;
  color: var(--cf-warning);
  font-weight: 700;
}
</style>
