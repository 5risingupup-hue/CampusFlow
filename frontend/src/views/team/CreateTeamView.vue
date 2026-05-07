<template>
  <div class="card-grid two-col">
    <section class="glass-card form-panel">
      <div class="soft-tag">Create Team</div>
      <h1 class="page-title">创建活动队伍</h1>
      <p class="page-subtitle">所有学生都可以创建队伍。谁创建队伍，谁就是队长；其他同学申请加入并通过审核后才会成为队员。</p>

      <el-form :model="form" label-position="top">
        <el-form-item label="目标活动">
          <el-select v-model="form.activityId" placeholder="请选择活动">
            <el-option v-for="item in activities" :key="item.id" :label="item.title" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="队伍名称">
          <el-input v-model="form.teamName" placeholder="例如 Campus Masters" />
        </el-form-item>
        <el-form-item label="队伍口号">
          <el-input v-model="form.slogan" placeholder="一句话说明队伍方向" />
        </el-form-item>
        <el-form-item label="队伍简介">
          <el-input v-model="form.description" type="textarea" :rows="5" placeholder="介绍团队优势、分工或招募方向" />
        </el-form-item>
        <el-button type="primary" round :loading="loading" @click="handleSubmit">创建并进入队伍页</el-button>
      </el-form>
    </section>

    <aside class="glass-card tip-panel">
      <h2 class="section-title">创建前建议</h2>
      <div class="list-stack">
        <div class="tip-item">先确认目标活动要求组队，再创建队伍。</div>
        <div class="tip-item">队伍名称尽量明确，便于申请者快速识别方向。</div>
        <div class="tip-item">创建完成后先补齐介绍和口号，再开放成员加入。</div>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../../api'
import type { ActivityCard } from '../../types'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const activities = ref<ActivityCard[]>([])
const form = reactive({
  activityId: Number(route.query.activityId || 0),
  teamName: '',
  slogan: '',
  description: ''
})

onMounted(async () => {
  const response = await api.getActivities({ pageNum: 1, pageSize: 50, requireTeam: true })
  activities.value = response.data.records
})

const handleSubmit = async () => {
  try {
    loading.value = true
    const response: any = await api.createTeam(form)
    ElMessage.success('队伍创建成功')
    router.push(`/teams/${response.data.teamId}`)
  } catch (error) {
    ElMessage.error((error as Error).message)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.form-panel,
.tip-panel {
  padding: 24px;
}

.tip-item {
  padding: 16px 18px;
  border-radius: 18px;
  background: var(--cf-surface-soft);
  line-height: 1.8;
  color: var(--cf-ink-soft);
}
</style>
