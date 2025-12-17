import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Card,
  Descriptions,
  Tag,
  Typography,
  Space,
  Button,
  Spin,
  Alert,
  Divider,
  Row,
  Col,
} from 'antd'
import {
  ArrowLeftOutlined,
  UserOutlined,
  CalendarOutlined,
  AlertOutlined,
  CheckCircleOutlined,
  DownloadOutlined,
} from '@ant-design/icons'
import { message } from 'antd'
import { reportsAPI } from '../api/reports'
import type { ReportDetail } from '../types'
import { exportReportDetailToExcel, downloadExportFile } from '../utils/export'

const { Title, Paragraph, Text } = Typography

export default function ReportDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [report, setReport] = useState<ReportDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadReportDetail()
  }, [id])

  const loadReportDetail = async () => {
    if (!id) return

    try {
      setLoading(true)
      setError(null)
      const data = await reportsAPI.getReportById(parseInt(id))
      setReport(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || '加载报告失败')
    } finally {
      setLoading(false)
    }
  }

  const handleExportExcel = () => {
    if (!report) return
    try {
      exportReportDetailToExcel(report)
      message.success('导出成功')
    } catch (error) {
      message.error('导出失败')
      console.error(error)
    }
  }

  const handleExportCSV = async () => {
    if (!id) return
    try {
      const url = `http://localhost:8080/api/dashboard/reports/${id}/export`
      const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
      await downloadExportFile(url, `report_${id}_${timestamp}.csv`)
      message.success('导出成功')
    } catch (error) {
      message.error('导出失败')
      console.error(error)
    }
  }

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'high':
        return 'error'
      case 'medium':
        return 'warning'
      case 'low':
        return 'success'
      default:
        return 'default'
    }
  }

  const getRiskLevelText = (level: string) => {
    switch (level) {
      case 'high':
        return '高'
      case 'medium':
        return '中'
      case 'low':
        return '低'
      default:
        return level
    }
  }

  const getPeriodTypeText = (type: string) => {
    switch (type) {
      case 'daily':
        return '日报'
      case 'weekly':
        return '周报'
      case 'monthly':
        return '月报'
      default:
        return type
    }
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="加载中..." />
      </div>
    )
  }

  if (error) {
    return (
      <div style={{ padding: '24px' }}>
        <Alert
          message="错误"
          description={error}
          type="error"
          showIcon
          action={
            <Button type="primary" onClick={() => navigate('/dashboard')}>
              返回仪表盘
            </Button>
          }
        />
      </div>
    )
  }

  if (!report) {
    return (
      <div style={{ padding: '24px' }}>
        <Alert
          message="未找到报告"
          description="该报告不存在或已被删除"
          type="warning"
          showIcon
          action={
            <Button type="primary" onClick={() => navigate('/dashboard')}>
              返回仪表盘
            </Button>
          }
        />
      </div>
    )
  }

  return (
    <div style={{ padding: '24px', backgroundColor: '#f0f2f5', minHeight: '100vh' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* Header */}
        <Card>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Space>
              <Button
                icon={<ArrowLeftOutlined />}
                onClick={() => navigate('/dashboard')}
              >
                返回
              </Button>
              <Title level={2} style={{ margin: 0 }}>
                报告详情
              </Title>
            </Space>
            <Space>
              <Button
                type="default"
                icon={<DownloadOutlined />}
                onClick={handleExportExcel}
              >
                导出 Excel
              </Button>
              <Button
                type="default"
                icon={<DownloadOutlined />}
                onClick={handleExportCSV}
              >
                导出 CSV
              </Button>
            </Space>
          </div>
        </Card>

        {/* Basic Info */}
        <Card title="基本信息">
          <Descriptions column={2} bordered>
            <Descriptions.Item label="提交人" span={1}>
              <Space>
                <UserOutlined />
                {report.user_name}
              </Space>
            </Descriptions.Item>
            <Descriptions.Item label="报告类型" span={1}>
              <Tag color="blue">{getPeriodTypeText(report.period_type)}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="报告周期" span={2}>
              <Space>
                <CalendarOutlined />
                {report.period_start} 至 {report.period_end}
              </Space>
            </Descriptions.Item>
            <Descriptions.Item label="提交时间" span={1}>
              {new Date(report.created_at).toLocaleString('zh-CN')}
            </Descriptions.Item>
            <Descriptions.Item label="风险等级" span={1}>
              <Tag color={getRiskLevelColor(report.risk_level)} icon={<AlertOutlined />}>
                {getRiskLevelText(report.risk_level)}
              </Tag>
            </Descriptions.Item>
          </Descriptions>
        </Card>

        {/* HR Summary */}
        <Card title="HR 友好总结">
          <Paragraph style={{ fontSize: '16px', lineHeight: '1.8' }}>
            {report.hr_summary}
          </Paragraph>
        </Card>

        {/* Original Text */}
        <Card title="原始内容">
          <Paragraph style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
            {report.raw_text}
          </Paragraph>
        </Card>

        {/* Risk Analysis */}
        {report.risks && (
          <Card title="风险分析" extra={<Tag color="warning">需关注</Tag>}>
            <Paragraph style={{ fontSize: '15px', lineHeight: '1.8' }}>
              {report.risks}
            </Paragraph>
          </Card>
        )}

        {/* Needs */}
        {report.needs && (
          <Card title="资源需求">
            <Paragraph style={{ fontSize: '15px', lineHeight: '1.8' }}>
              {report.needs}
            </Paragraph>
          </Card>
        )}

        {/* OKR Information */}
        <Card title="OKR 信息">
          <Row gutter={[16, 16]}>
            <Col span={12}>
              <Card type="inner" title="命中目标">
                <Text strong>{report.hit_objectives || '未识别'}</Text>
              </Card>
            </Col>
            <Col span={12}>
              <Card type="inner" title="命中关键结果">
                <Text strong>{report.hit_krs || '未识别'}</Text>
              </Card>
            </Col>
            <Col span={12}>
              <Card type="inner" title="OKR 差距">
                <Text type="warning">{report.okr_gaps || '无'}</Text>
              </Card>
            </Col>
            <Col span={12}>
              <Card type="inner" title="完成信心度">
                <Space>
                  <CheckCircleOutlined style={{ color: '#52c41a' }} />
                  <Text strong>
                    {report.okr_confidence
                      ? `${(parseFloat(report.okr_confidence) * 100).toFixed(0)}%`
                      : '未评估'}
                  </Text>
                </Space>
              </Card>
            </Col>
          </Row>

          {report.okr_brief && (
            <>
              <Divider />
              <Title level={5}>OKR 详细信息</Title>
              <Paragraph style={{ whiteSpace: 'pre-wrap', fontSize: '14px' }}>
                {report.okr_brief}
              </Paragraph>
            </>
          )}
        </Card>

        {/* Next Actions */}
        {report.next_actions && (
          <Card title="后续行动计划">
            <Paragraph style={{ fontSize: '15px', lineHeight: '1.8' }}>
              {report.next_actions}
            </Paragraph>
          </Card>
        )}
      </Space>
    </div>
  )
}
