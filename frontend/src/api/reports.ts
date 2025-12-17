import apiClient from './client'
import type { ReportDetail } from '../types'

export const reportsAPI = {
  /**
   * Get report details by ID
   */
  getReportById: async (reportId: number): Promise<ReportDetail> => {
    const response = await apiClient.get<ReportDetail>(`/api/dashboard/reports/${reportId}`)
    return response.data
  },
}

export default reportsAPI
