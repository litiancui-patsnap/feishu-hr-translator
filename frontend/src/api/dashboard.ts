import { apiClient } from './client'
import { DashboardStats, ReportSummary, RiskDistribution } from '../types'

export const dashboardAPI = {
  // Get dashboard statistics
  getStats: async (): Promise<DashboardStats> => {
    const response = await apiClient.get<DashboardStats>('/api/dashboard/stats')
    return response.data
  },

  // Get recent reports
  getRecentReports: async (limit: number = 10): Promise<ReportSummary[]> => {
    const response = await apiClient.get<ReportSummary[]>('/api/dashboard/recent-reports', {
      params: { limit },
    })
    return response.data
  },

  // Get risk distribution
  getRiskDistribution: async (): Promise<RiskDistribution> => {
    const response = await apiClient.get<RiskDistribution>('/api/dashboard/risk-distribution')
    return response.data
  },

  // Get OKR trend data
  getOkrTrend: async (days: number = 30): Promise<any[]> => {
    const response = await apiClient.get('/api/dashboard/okr-trend', {
      params: { days },
    })
    return response.data
  },

  // Get report timeline data
  getReportTimeline: async (days: number = 30): Promise<any[]> => {
    const response = await apiClient.get('/api/dashboard/report-timeline', {
      params: { days },
    })
    return response.data
  },

  // Get reports list with filters and pagination
  getReportsList: async (params: {
    page?: number
    page_size?: number
    risk_level?: string
    period_type?: string
    user_name?: string
    search?: string
    start_date?: string
    end_date?: string
  }): Promise<{
    total: number
    page: number
    page_size: number
    total_pages: number
    items: ReportSummary[]
  }> => {
    const response = await apiClient.get('/api/dashboard/reports', { params })
    return response.data
  },
}
