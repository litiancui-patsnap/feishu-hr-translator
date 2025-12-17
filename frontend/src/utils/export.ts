import * as XLSX from 'xlsx'
import type { ReportSummary, ReportDetail } from '../types'

/**
 * Export reports list to Excel file
 */
export const exportReportsToExcel = (reports: ReportSummary[], filename: string = 'reports') => {
  const data = reports.map(report => ({
    'ID': report.id,
    '提交人': report.user_name,
    '报告周期': getPeriodTypeText(report.period_type),
    '开始日期': report.period_start || '',
    '结束日期': report.period_end || '',
    '创建时间': report.created_at,
    '风险等级': getRiskLevelText(report.risk_level),
    'HR总结': report.hr_summary,
  }))

  const worksheet = XLSX.utils.json_to_sheet(data)
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, '报告列表')

  // Set column widths
  worksheet['!cols'] = [
    { wch: 10 },  // ID
    { wch: 15 },  // 提交人
    { wch: 10 },  // 报告周期
    { wch: 15 },  // 开始日期
    { wch: 15 },  // 结束日期
    { wch: 20 },  // 创建时间
    { wch: 10 },  // 风险等级
    { wch: 50 },  // HR总结
  ]

  const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
  XLSX.writeFile(workbook, `${filename}_${timestamp}.xlsx`)
}

/**
 * Export single report detail to Excel file
 */
export const exportReportDetailToExcel = (report: ReportDetail, filename?: string) => {
  // Create basic info sheet
  const basicInfo = [
    ['字段', '内容'],
    ['报告ID', report.id],
    ['提交人', report.user_name],
    ['报告周期', getPeriodTypeText(report.period_type)],
    ['开始日期', report.period_start || ''],
    ['结束日期', report.period_end || ''],
    ['创建时间', report.created_at],
    ['风险等级', getRiskLevelText(report.risk_level)],
    [],
    ['HR总结', report.hr_summary],
    [],
    ['原始内容', report.raw_text],
  ]

  // Helper function to normalize string or array
  const normalizeArray = (value: string | string[] | undefined): string[] => {
    if (!value) return []
    return Array.isArray(value) ? value : [value]
  }

  // Add risks
  const risks = normalizeArray(report.risks)
  if (risks.length > 0) {
    basicInfo.push([])
    basicInfo.push(['风险项', ''])
    risks.forEach(risk => {
      basicInfo.push(['', risk])
    })
  }

  // Add needs
  const needs = normalizeArray(report.needs)
  if (needs.length > 0) {
    basicInfo.push([])
    basicInfo.push(['需求和帮助', ''])
    needs.forEach(need => {
      basicInfo.push(['', need])
    })
  }

  // Add OKR information
  const hitObjectives = normalizeArray(report.hit_objectives)
  if (hitObjectives.length > 0) {
    basicInfo.push([])
    basicInfo.push(['命中的目标', ''])
    hitObjectives.forEach(obj => {
      basicInfo.push(['', obj])
    })
  }

  const hitKrs = normalizeArray(report.hit_krs)
  if (hitKrs.length > 0) {
    basicInfo.push([])
    basicInfo.push(['命中的关键结果', ''])
    hitKrs.forEach(kr => {
      basicInfo.push(['', kr])
    })
  }

  const okrGaps = normalizeArray(report.okr_gaps)
  if (okrGaps.length > 0) {
    basicInfo.push([])
    basicInfo.push(['OKR差距', ''])
    okrGaps.forEach(gap => {
      basicInfo.push(['', gap])
    })
  }

  const nextActions = normalizeArray(report.next_actions)
  if (nextActions.length > 0) {
    basicInfo.push([])
    basicInfo.push(['下一步行动', ''])
    nextActions.forEach(action => {
      basicInfo.push(['', action])
    })
  }

  const worksheet = XLSX.utils.aoa_to_sheet(basicInfo)
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, '报告详情')

  // Set column widths
  worksheet['!cols'] = [
    { wch: 20 },  // Field name
    { wch: 80 },  // Content
  ]

  const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
  const finalFilename = filename || `report_${report.id}`
  XLSX.writeFile(workbook, `${finalFilename}_${timestamp}.xlsx`)
}

/**
 * Download file from backend export endpoint
 */
export const downloadExportFile = async (url: string, filename: string) => {
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      throw new Error('Export failed')
    }

    const blob = await response.blob()
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)
  } catch (error) {
    console.error('Download failed:', error)
    throw error
  }
}

// Helper functions
const getPeriodTypeText = (type: string): string => {
  const map: Record<string, string> = {
    daily: '日报',
    weekly: '周报',
    monthly: '月报',
  }
  return map[type] || type
}

const getRiskLevelText = (level: string): string => {
  const map: Record<string, string> = {
    low: '低',
    medium: '中',
    high: '高',
  }
  return map[level] || level
}
