<template>
  <div class="card-grid two-col">
    <section class="glass-card list-panel">
      <div class="soft-tag">Announcement Center</div>
      <h1 class="page-title">公告治理</h1>
      <p class="page-subtitle">统一管理面向全站用户的公告发布，规则更新后会自动同步到通知系统。</p>

      <div class="list-stack announcement-list">
        <article v-for="item in announcements" :key="item.id" class="announcement-card">
          <div class="announcement-head">
            <strong>{{ item.title }}</strong>
            <span>{{ item.creatorName }} · {{ formatDateTime(item.createdAt) }}</span>
          </div>
          <p>{{ item.content }}</p>
        </article>
      </div>
    </section>

    <aside class="glass-card editor-panel">
      <h2 class="section-title">发布新公告</h2>
      <p class="section-subtitle">建议用简短标题说明影响范围，正文补充具体执行要求。</p>
      <el-form :model="form" label-position="top">
        <el-form-item label="标题">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="form.content" type="textarea" :rows="6" />
        </el-form-item>
        <el-button type="primary" round @click="submitAnnouncement">立即发布</el-button>
      </el-form>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../../api'
import type { AnnouncementItem } from '../../types'
import { formatDateTime } from '../../utils/format'

const announcements = ref<AnnouncementItem[]>([])
const form = reactive({
  title: '',
  content: ''
})

const fetchAnnouncements = async () => {
  const response = await api.getAnnouncements()
  announcements.value = response.data
}

const submitAnnouncement = async () => {
  try {
    await api.createAnnouncement(form)
    ElMessage.success('公告发布成功')
    form.title = ''
    form.content = ''
    await fetchAnnouncements()
  } catch (error) {
    ElMessage.error((error as Error).message)
  }
}

onMounted(fetchAnnouncements)
</script>

<style scoped>
.list-panel,
.editor-panel {
  padding: 24px;
}

.announcement-list {
  margin-top: 20px;
}

.announcement-card {
  padding: 18px;
  border-radius: 18px;
  background: var(--cf-surface-soft);
}

.announcement-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.announcement-card p {
  margin: 12px 0 0;
  color: var(--cf-ink-soft);
  line-height: 1.8;
}

@media (max-width: 760px) {
  .announcement-head {
    flex-direction: column;
  }
}
</style>
