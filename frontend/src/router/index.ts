import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'
import { pinia } from '../stores/pinia'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/auth/LoginView.vue'),
      meta: { public: true }
    },
    {
      path: '/',
      component: () => import('../layouts/MainLayout.vue'),
      children: [
        {
          path: '',
          redirect: '/activities'
        },
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('../views/home/DashboardView.vue')
        },
        {
          path: 'activities',
          name: 'activities',
          component: () => import('../views/activity/ActivityListView.vue'),
          meta: { public: true }
        },
        {
          path: 'activities/:id',
          name: 'activity-detail',
          component: () => import('../views/activity/ActivityDetailView.vue'),
          meta: { public: true }
        },
        {
          path: 'teams/create',
          name: 'team-create',
          component: () => import('../views/team/CreateTeamView.vue')
        },
        {
          path: 'teams/join',
          name: 'team-join',
          component: () => import('../views/team/JoinTeamView.vue')
        },
        {
          path: 'teams/:id',
          name: 'team-detail',
          component: () => import('../views/team/TeamDetailView.vue')
        },
        {
          path: 'organizer/reviews',
          name: 'organizer-reviews',
          component: () => import('../views/organizer/ReviewListView.vue'),
          meta: { roles: ['organizer', 'admin'] }
        },
        {
          path: 'organizer/activities',
          name: 'organizer-activities',
          component: () => import('../views/organizer/ActivityManageView.vue'),
          meta: { roles: ['organizer', 'admin'] }
        },
        {
          path: 'notices',
          name: 'notices',
          component: () => import('../views/notice/NoticeListView.vue')
        },
        {
          path: 'sign',
          name: 'sign',
          component: () => import('../views/sign/SignView.vue')
        },
        {
          path: 'feedback/:activityId',
          name: 'feedback',
          component: () => import('../views/feedback/FeedbackView.vue')
        },
        {
          path: 'admin/announcements',
          name: 'admin-announcements',
          component: () => import('../views/admin/AnnouncementView.vue'),
          meta: { roles: ['admin'] }
        }
      ]
    }
  ],
  scrollBehavior() {
    return { top: 0 }
  }
})

router.beforeEach(async (to) => {
  const userStore = useUserStore(pinia)
  if (userStore.token && !userStore.profile) {
    try {
      await userStore.fetchProfile()
    } catch {
      userStore.logout()
    }
  }
  if (to.meta.public) {
    return true
  }
  if (!userStore.isLoggedIn) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  const allowedRoles = to.meta.roles as string[] | undefined
  if (allowedRoles && !allowedRoles.includes(userStore.role)) {
    return { path: '/activities' }
  }
  return true
})

export default router
