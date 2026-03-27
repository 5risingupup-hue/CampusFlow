<template>
  <article class="activity-card glass-card">
    <div class="cover" :style="{ backgroundImage: `url(${activity.coverUrl || fallbackCover})` }">
      <div class="cover-overlay" />
      <div class="cover-top">
        <span class="type-pill">{{ activity.type }}</span>
        <el-tag :type="statusTagTypeMap[activity.status] || 'info'" round effect="dark">
          {{ statusLabelMap[activity.status] || activity.status }}
        </el-tag>
      </div>
      <div class="cover-bottom">
        <div class="organizer-line">{{ activity.organizerName }}</div>
        <h3>{{ activity.title }}</h3>
      </div>
    </div>

    <div class="body">
      <div class="meta-grid">
        <div class="meta-item">
          <span class="meta-label">活动地点</span>
          <strong>{{ activity.location }}</strong>
        </div>
        <div class="meta-item">
          <span class="meta-label">开始时间</span>
          <strong>{{ formatShortDate(activity.startTime) }}</strong>
        </div>
        <div class="meta-item">
          <span class="meta-label">报名截止</span>
          <strong>{{ formatShortDate(activity.signupDeadline) }}</strong>
        </div>
        <div class="meta-item">
          <span class="meta-label">参与模式</span>
          <strong>{{ activity.requireTeam ? '团队协作' : '个人参与' }}</strong>
        </div>
      </div>

      <div v-if="activity.tags.length" class="tag-row">
        <span v-for="tag in activity.tags.slice(0, 4)" :key="tag" class="mini-tag">{{ tag }}</span>
      </div>

      <div class="card-footer">
        <p class="footer-copy">
          {{ activity.requireTeam ? '支持查看队伍、申请加入与后续协作。' : '支持查看活动规则、签到与反馈安排。' }}
        </p>
        <div class="footer-actions">
          <el-button round @click="router.push(`/activities/${activity.id}`)">查看详情</el-button>
          <el-button
            v-if="activity.requireTeam"
            type="primary"
            round
            plain
            @click="router.push(`/teams/join?activityId=${activity.id}`)"
          >
            队伍协作
          </el-button>
        </div>
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import type { ActivityCard } from '../types'
import { formatShortDate, statusLabelMap, statusTagTypeMap } from '../utils/format'

defineProps<{
  activity: ActivityCard
}>()

const router = useRouter()
const fallbackCover =
  'https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=1200&q=80'
</script>

<style scoped>
.activity-card {
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 100%;
  transition: transform 0.24s ease, box-shadow 0.24s ease;
}

.activity-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--cf-shadow-lg);
}

.cover {
  position: relative;
  min-height: 232px;
  padding: 18px;
  background-size: cover;
  background-position: center;
  color: white;
}

.cover-overlay {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--cf-hero-overlay) 36%, transparent), var(--cf-hero-overlay)),
    linear-gradient(140deg, color-mix(in srgb, var(--cf-primary) 34%, transparent), transparent 50%);
}

.cover-top,
.cover-bottom {
  position: relative;
  z-index: 1;
}

.cover-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.cover-bottom {
  margin-top: 114px;
}

.type-pill {
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 999px;
  background: var(--cf-hero-soft-overlay);
  backdrop-filter: blur(10px);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.organizer-line {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  opacity: 0.86;
}

h3 {
  margin: 10px 0 0;
  font-size: 28px;
  line-height: 1.08;
  letter-spacing: -0.04em;
}

.body {
  display: flex;
  flex: 1;
  flex-direction: column;
  padding: 22px;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.meta-item {
  padding: 15px 16px;
  border-radius: 18px;
  background: var(--cf-surface-soft);
}

.meta-label {
  display: block;
  margin-bottom: 8px;
  color: var(--cf-ink-soft);
  font-size: 12px;
}

.meta-item strong {
  font-size: 14px;
  line-height: 1.55;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

.mini-tag {
  padding: 7px 11px;
  border-radius: 999px;
  background: var(--cf-primary-soft);
  color: var(--cf-primary-deep);
  font-size: 12px;
  font-weight: 700;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-end;
  margin-top: auto;
  padding-top: 22px;
}

.footer-copy {
  margin: 0;
  color: var(--cf-ink-soft);
  font-size: 13px;
  line-height: 1.7;
}

.footer-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
}

@media (max-width: 760px) {
  .cover {
    min-height: 214px;
  }

  .cover-bottom {
    margin-top: 86px;
  }

  .meta-grid,
  .card-footer {
    grid-template-columns: 1fr;
    flex-direction: column;
    align-items: stretch;
  }

  .footer-actions {
    justify-content: stretch;
  }
}
</style>
