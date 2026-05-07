<template>
  <article class="activity-card glass-card" :class="{ 'is-reversed': index % 2 === 1 }">
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
          {{ activity.requireTeam ? '创建队伍即成为队长，也可以申请加入已有队伍。' : '个人报名通过后可签到并提交反馈。' }}
        </p>
        <div class="footer-actions">
          <el-button round @click="router.push(`/activities/${activity.id}`)">查看详情</el-button>
          <el-button
            v-if="activity.status === 'signup_open'"
            type="primary"
            round
            plain
            @click="router.push(`/activities/${activity.id}`)"
          >
            {{ activity.requireTeam ? '组队报名' : '个人报名' }}
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

withDefaults(defineProps<{
  activity: ActivityCard
  index?: number
}>(), {
  index: 0
})

const router = useRouter()
const fallbackCover =
  'https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=1200&q=80'
</script>

<style scoped>
.activity-card {
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: minmax(420px, 1.18fr) minmax(0, 0.82fr);
  min-height: 472px;
  border-radius: 40px;
  background:
    radial-gradient(circle at 0% 0%, color-mix(in srgb, var(--cf-primary) 10%, transparent), transparent 34%),
    radial-gradient(circle at 100% 100%, color-mix(in srgb, var(--cf-accent) 11%, transparent), transparent 30%),
    linear-gradient(180deg, var(--cf-card-start), var(--cf-card-end));
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.activity-card::before {
  content: '';
  position: absolute;
  inset: auto 26px 18px;
  height: 34px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--cf-primary) 12%, transparent);
  filter: blur(20px);
  opacity: 0.55;
  pointer-events: none;
}

.activity-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 34px 96px color-mix(in srgb, var(--cf-primary) 14%, rgba(16, 29, 52, 0.22));
}

.activity-card.is-reversed .cover {
  order: 2;
  margin: 16px 16px 16px 0;
}

.activity-card.is-reversed .body {
  order: 1;
}

.cover {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 100%;
  margin: 16px 0 16px 16px;
  padding: 28px;
  border-radius: 34px;
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
  display: flex;
  flex-direction: column;
  gap: 12px;
  justify-content: flex-end;
}

.type-pill {
  display: inline-flex;
  align-items: center;
  padding: 10px 14px;
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
  margin: 0;
  max-width: 10ch;
  font-size: clamp(32px, 3vw, 48px);
  line-height: 1;
  letter-spacing: -0.04em;
}

.body {
  display: flex;
  flex: 1;
  flex-direction: column;
  padding: 30px 30px 28px;
  position: relative;
  z-index: 1;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.meta-item {
  padding: 18px 18px 16px;
  border-radius: 22px;
  border: 1px solid color-mix(in srgb, var(--cf-line) 82%, transparent);
  background: color-mix(in srgb, var(--cf-surface-soft) 78%, transparent);
  backdrop-filter: blur(10px);
}

.meta-label {
  display: block;
  margin-bottom: 8px;
  color: var(--cf-ink-soft);
  font-size: 12px;
}

.meta-item strong {
  font-size: 15px;
  line-height: 1.6;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 22px;
}

.mini-tag {
  padding: 8px 12px;
  border-radius: 999px;
  background: var(--cf-primary-soft);
  color: var(--cf-primary-deep);
  font-size: 12px;
  font-weight: 700;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-end;
  margin-top: auto;
  padding-top: 28px;
}

.footer-copy {
  margin: 0;
  color: var(--cf-ink-soft);
  max-width: 28ch;
  font-size: 14px;
  line-height: 1.8;
}

.footer-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
}

@media (max-width: 760px) {
  .activity-card,
  .activity-card.is-reversed {
    grid-template-columns: 1fr;
    min-height: auto;
  }

  .cover {
    min-height: 228px;
    margin: 14px 14px 0;
  }

  .activity-card.is-reversed .cover {
    order: 1;
    margin: 14px 14px 0;
  }

  .activity-card.is-reversed .body {
    order: 2;
  }

  .meta-grid,
  .card-footer {
    grid-template-columns: 1fr;
    flex-direction: column;
    align-items: stretch;
  }

  .body {
    padding: 24px 20px 22px;
  }

  h3 {
    max-width: none;
    font-size: 34px;
  }

  .footer-actions {
    justify-content: stretch;
  }
}
</style>
