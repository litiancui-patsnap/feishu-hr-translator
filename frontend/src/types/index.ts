// API Response Types

export interface User {
  id: number
  username: string
  email?: string
  full_name?: string
  feishu_user_id?: string
  avatar_url?: string
  role: string
  is_active: boolean
  created_at?: string
  last_login_at?: string
}

export interface LoginRequest {
  username: string
  password: string
  remember_me?: boolean
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface DashboardStats {
  weekly_reports: number
  monthly_reports: number
  high_risk_items: number
  okr_completion: number
  weekly_trend: number
  monthly_trend: number
  risk_trend: number
  okr_trend: number
}

export interface ReportSummary {
  id: number
  user_name: string
  period_type: string
  period_start?: string
  period_end?: string
  created_at: string
  risk_level: 'low' | 'medium' | 'high'
  hr_summary: string
}

export interface RiskDistribution {
  low: number
  medium: number
  high: number
}

export interface ReportDetail {
  id: number
  user_id: string
  user_name: string
  period_type: string
  period_start: string
  period_end: string
  created_at: string
  raw_text: string
  hr_summary: string
  risk_level: 'low' | 'medium' | 'high'
  risks?: string | string[]
  needs?: string | string[]
  hit_objectives?: string | string[]
  hit_krs?: string | string[]
  okr_gaps?: string | string[]
  okr_confidence?: string
  next_actions?: string | string[]
  okr_brief?: string
}
