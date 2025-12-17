import { apiClient } from './client'

export interface UserSubmissionStats {
  user_name: string
  total_reports: number
  weekly_reports: number
  monthly_reports: number
  high_risk_count: number
  avg_okr_confidence: number
}

export interface RiskTrendData {
  date: string
  low: number
  medium: number
  high: number
  total: number
}

export interface OkrRankingData {
  user_name: string
  avg_confidence: number
  report_count: number
  hit_objectives_count: number
  hit_krs_count: number
}

export interface TeamStatistics {
  total_users: number
  total_reports: number
  avg_reports_per_user: number
  risk_distribution: {
    low: number
    medium: number
    high: number
  }
  period_distribution: {
    daily: number
    weekly: number
    monthly: number
  }
  avg_okr_confidence: number
  high_risk_rate: number
}

export const analyticsAPI = {
  // Get user submission statistics
  getUserSubmissions: async (days: number = 30): Promise<UserSubmissionStats[]> => {
    const response = await apiClient.get<UserSubmissionStats[]>('/api/dashboard/analytics/user-submissions', {
      params: { days },
    })
    return response.data
  },

  // Get risk trend data
  getRiskTrend: async (days: number = 30): Promise<RiskTrendData[]> => {
    const response = await apiClient.get<RiskTrendData[]>('/api/dashboard/analytics/risk-trend', {
      params: { days },
    })
    return response.data
  },

  // Get OKR ranking
  getOkrRanking: async (days: number = 30): Promise<OkrRankingData[]> => {
    const response = await apiClient.get<OkrRankingData[]>('/api/dashboard/analytics/okr-ranking', {
      params: { days },
    })
    return response.data
  },

  // Get team statistics
  getTeamStats: async (): Promise<TeamStatistics> => {
    const response = await apiClient.get<TeamStatistics>('/api/dashboard/analytics/team-stats')
    return response.data
  },
}
