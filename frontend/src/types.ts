export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface PageResult<T> {
  total: number
  records: T[]
}

export interface UserProfile {
  id: number
  username: string
  nickname: string
  avatar?: string
  email?: string
  role: string
}

export interface LoginResponse {
  token: string
  userInfo: UserProfile
}

export interface ActivityCard {
  id: number
  title: string
  coverUrl?: string
  organizerName: string
  type: string
  location: string
  startTime: string
  signupDeadline: string
  requireTeam: boolean
  status: string
  tags: string[]
}

export interface ActivityDetail extends ActivityCard {
  description: string
  organizerId: number
  endTime: string
  minTeamSize: number
  maxTeamSize: number
  teamCount: number
  myTeamId?: number
  myApplicationStatus?: string
  canCreateTeam: boolean
  canApplyTeam: boolean
  canSignIn: boolean
  canFeedback: boolean
  resultSummary?: string
}

export interface TeamMember {
  userId: number
  nickname: string
  avatar?: string
  memberRole: string
  joinStatus: string
  joinedAt?: string
}

export interface ApplicationRecord {
  id: number
  applicantId: number
  applicantName: string
  type: string
  status: string
  reason?: string
  reviewComment?: string
  createdAt: string
}

export interface TeamDetail {
  id: number
  activityId: number
  activityTitle: string
  teamName: string
  leaderId: number
  leaderName: string
  slogan?: string
  description?: string
  inviteCode: string
  status: string
  currentSize: number
  minTeamSize: number
  maxTeamSize: number
  canManage: boolean
  members: TeamMember[]
  pendingApplications: ApplicationRecord[]
}

export interface TeamListItem {
  id: number
  activityId: number
  activityTitle: string
  teamName: string
  slogan?: string
  description?: string
  leaderId: number
  leaderName: string
  currentSize: number
  maxTeamSize: number
  status: string
  applied: boolean
}

export interface ReviewItem {
  id: number
  type: string
  status: string
  activityId: number
  activityTitle: string
  teamId: number
  teamName: string
  applicantId: number
  applicantName: string
  reason?: string
  memberCount: number
  reviewComment?: string
  createdAt: string
}

export interface NotificationItem {
  id: number
  title: string
  content: string
  type: string
  isRead: boolean
  createdAt: string
}

export interface SignStatus {
  activityId: number
  activityTitle: string
  status: string
  eligible: boolean
  signWindowOpen: boolean
  signTime?: string
}

export interface FeedbackItem {
  userId: number
  nickname: string
  score: number
  content?: string
  tags: string[]
  willingRejoin?: boolean
  createdAt: string
}

export interface FeedbackSummary {
  averageScore: number
  total: number
  records: FeedbackItem[]
}

export interface AnnouncementItem {
  id: number
  title: string
  content: string
  createdBy: number
  creatorName: string
  createdAt: string
}

export interface NameValuePair {
  name: string
  value: number
}

export interface DashboardOverview {
  role: string
  activityCount: number
  teamCount: number
  pendingCount: number
  unreadCount: number
  signedCount: number
  feedbackAverage: number
  activityTypeDistribution: NameValuePair[]
  upcomingActivities: ActivityCard[]
}
