import http from './http'
import type {
  ActivityCard,
  ActivityDetail,
  AnnouncementItem,
  ApiResponse,
  DashboardOverview,
  FeedbackSummary,
  LoginResponse,
  NotificationItem,
  PageResult,
  ReviewItem,
  SignStatus,
  TeamDetail,
  TeamListItem,
  UserProfile
} from '../types'

export const api = {
  login: (payload: { username: string; password: string }) =>
    http.post<any, ApiResponse<LoginResponse>>('/api/auth/login', payload),
  getProfile: () => http.get<any, ApiResponse<UserProfile>>('/api/user/profile'),
  updateProfile: (payload: Partial<UserProfile>) =>
    http.put<any, ApiResponse<UserProfile>>('/api/user/profile', payload),
  getDashboard: () => http.get<any, ApiResponse<DashboardOverview>>('/api/dashboard/overview'),
  getActivities: (params: Record<string, unknown>) =>
    http.get<any, ApiResponse<PageResult<ActivityCard>>>('/api/activities', { params }),
  getMyActivities: () => http.get<any, ApiResponse<ActivityCard[]>>('/api/activities/mine'),
  getActivityDetail: (id: number) =>
    http.get<any, ApiResponse<ActivityDetail>>(`/api/activities/${id}`),
  createActivity: (payload: Record<string, unknown>) =>
    http.post<any, ApiResponse<ActivityDetail>>('/api/activities', payload),
  updateActivity: (id: number, payload: Record<string, unknown>) =>
    http.put<any, ApiResponse<ActivityDetail>>(`/api/activities/${id}`, payload),
  createTeam: (payload: Record<string, unknown>) =>
    http.post('/api/teams', payload),
  getTeamDetail: (id: number) =>
    http.get<any, ApiResponse<TeamDetail>>(`/api/teams/${id}`),
  getJoinableTeams: (params: Record<string, unknown>) =>
    http.get<any, ApiResponse<PageResult<TeamListItem>>>('/api/teams/joinable', { params }),
  applyJoinTeam: (id: number, payload: { reason?: string }) =>
    http.post(`/api/teams/${id}/apply`, payload),
  submitTeam: (id: number, payload?: { reason?: string }) =>
    http.post(`/api/teams/${id}/submit`, payload || {}),
  getReviews: (params: Record<string, unknown>) =>
    http.get<any, ApiResponse<PageResult<ReviewItem>>>('/api/reviews', { params }),
  approveReview: (id: number, payload?: { comment?: string }) =>
    http.post(`/api/reviews/${id}/approve`, payload || {}),
  rejectReview: (id: number, payload?: { comment?: string }) =>
    http.post(`/api/reviews/${id}/reject`, payload || {}),
  getNotices: (params: Record<string, unknown>) =>
    http.get<any, ApiResponse<PageResult<NotificationItem>>>('/api/notices', { params }),
  markNoticeRead: (ids: number[]) => http.post('/api/notices/read', { ids }),
  markAllRead: () => http.post('/api/notices/read-all'),
  getUnreadCount: () => http.get<any, ApiResponse<{ count: number }>>('/api/notices/unread-count'),
  getSignStatus: (activityId: number) =>
    http.get<any, ApiResponse<SignStatus>>(`/api/sign/status/${activityId}`),
  checkIn: (payload: { activityId: number; signCode: string }) =>
    http.post('/api/sign/check-in', payload),
  submitFeedback: (payload: Record<string, unknown>) =>
    http.post('/api/feedback', payload),
  getFeedback: (activityId: number) =>
    http.get<any, ApiResponse<FeedbackSummary>>(`/api/feedback/activity/${activityId}`),
  getAnnouncements: () => http.get<any, ApiResponse<AnnouncementItem[]>>('/api/announcements'),
  createAnnouncement: (payload: { title: string; content: string }) =>
    http.post<any, ApiResponse<AnnouncementItem>>('/api/announcements', payload)
}
