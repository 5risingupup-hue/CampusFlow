import dayjs from 'dayjs'

export const formatDateTime = (value?: string) =>
  value ? dayjs(value).format('YYYY-MM-DD HH:mm') : '--'

export const formatShortDate = (value?: string) =>
  value ? dayjs(value).format('MM-DD HH:mm') : '--'

export const statusTagTypeMap: Record<string, 'primary' | 'success' | 'warning' | 'danger' | 'info'> = {
  signup_open: 'success',
  published: 'primary',
  submitted: 'warning',
  approved: 'success',
  pending: 'warning',
  rejected: 'danger',
  disbanded: 'danger',
  left: 'info',
  removed: 'danger',
  finished: 'info',
  signed: 'success',
  unsigned: 'info'
}

export const statusLabelMap: Record<string, string> = {
  draft: '草稿',
  published: '已发布',
  signup_open: '报名中',
  signup_closed: '报名截止',
  finished: '已结束',
  cancelled: '已取消',
  forming: '组队中',
  submitted: '审核中',
  approved: '已通过',
  rejected: '已拒绝',
  disbanded: '已解散',
  left: '已退出',
  removed: '已移除',
  pending: '待处理',
  signed: '已签到',
  unsigned: '未签到',
  join_team: '入队申请',
  signup_team: '队伍报名',
  signup_personal: '个人报名'
}

export const roleLabelMap: Record<string, string> = {
  student: '学生',
  captain: '队长',
  organizer: '组织者',
  admin: '管理员'
}
