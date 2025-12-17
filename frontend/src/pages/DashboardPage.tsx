import { useEffect, useState } from 'react'
import { Layout, Card, Row, Col, Statistic, Table, Tag, Typography, Button, message, Space, Avatar } from 'antd'
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  FileTextOutlined,
  WarningOutlined,
  TrophyOutlined,
  UserOutlined,
  LogoutOutlined,
  BarChartOutlined,
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { dashboardAPI } from '../api/dashboard'
import { useAuth } from '../contexts/AuthContext'
import type { DashboardStats, ReportSummary, RiskDistribution } from '../types'
import RiskPieChart from '../components/RiskPieChart'
import OkrTrendChart from '../components/OkrTrendChart'
import ReportTimelineChart from '../components/ReportTimelineChart'

const { Header, Content } = Layout
const { Title, Text } = Typography

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [recentReports, setRecentReports] = useState<ReportSummary[]>([])
  const [riskDistribution, setRiskDistribution] = useState<RiskDistribution>({ low: 0, medium: 0, high: 0 })
  const [okrTrendData, setOkrTrendData] = useState<any[]>([])
  const [timelineData, setTimelineData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const [statsData, reportsData, riskData, okrData, timeline] = await Promise.all([
        dashboardAPI.getStats(),
        dashboardAPI.getRecentReports(5),
        dashboardAPI.getRiskDistribution(),
        dashboardAPI.getOkrTrend(30),
        dashboardAPI.getReportTimeline(30),
      ])
      setStats(statsData)
      setRecentReports(reportsData)
      setRiskDistribution(riskData)
      setOkrTrendData(okrData)
      setTimelineData(timeline)
    } catch (error) {
      message.error('加载数据失败')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    await logout()
    message.success('已退出登录')
    navigate('/login')
  }

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'high':
        return 'red'
      case 'medium':
        return 'orange'
      case 'low':
        return 'green'
      default:
        return 'default'
    }
  }

  const getRiskText = (level: string) => {
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

  const columns = [
    {
      title: '提交人',
      dataIndex: 'user_name',
      key: 'user_name',
      render: (name: string) => (
        <Space>
          <Avatar size="small" icon={<UserOutlined />} />
          {name}
        </Space>
      ),
    },
    {
      title: '周期',
      dataIndex: 'period_type',
      key: 'period_type',
      render: (type: string) => {
        const typeMap: Record<string, string> = {
          daily: '日报',
          weekly: '周报',
          monthly: '月报',
        }
        return typeMap[type] || type
      },
    },
    {
      title: '风险等级',
      dataIndex: 'risk_level',
      key: 'risk_level',
      render: (level: string) => (
        <Tag color={getRiskColor(level)}>{getRiskText(level)}</Tag>
      ),
    },
    {
      title: 'HR总结',
      dataIndex: 'hr_summary',
      key: 'hr_summary',
      ellipsis: true,
      render: (text: string) => (
        <Text ellipsis style={{ maxWidth: 300 }}>
          {text}
        </Text>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: ReportSummary) => (
        <Button
          type="link"
          size="small"
          onClick={() => navigate(`/reports/${record.id}`)}
        >
          查看
        </Button>
      ),
    },
  ]

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header
        style={{
          background: '#fff',
          padding: '0 24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        }}
      >
        <Title level={4} style={{ margin: 0 }}>
          Feishu HR Translator
        </Title>
        <Space>
          <Button
            type="primary"
            icon={<BarChartOutlined />}
            onClick={() => navigate('/analytics')}
          >
            统计分析
          </Button>
          <Text>欢迎, {user?.full_name || user?.username}</Text>
          <Button
            icon={<LogoutOutlined />}
            onClick={handleLogout}
          >
            退出
          </Button>
        </Space>
      </Header>

      <Content style={{ padding: 24 }}>
        <Title level={3} style={{ marginBottom: 24 }}>
          📊 仪表盘
        </Title>

        {/* Stats Cards */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="本周报告"
                value={stats?.weekly_reports || 0}
                prefix={<FileTextOutlined />}
                suffix={
                  <span style={{ fontSize: 14 }}>
                    {stats && stats.weekly_trend > 0 ? (
                      <Text type="success">
                        <ArrowUpOutlined /> {stats.weekly_trend.toFixed(1)}%
                      </Text>
                    ) : (
                      <Text type="danger">
                        <ArrowDownOutlined /> {Math.abs(stats?.weekly_trend || 0).toFixed(1)}%
                      </Text>
                    )}
                  </span>
                }
              />
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="本月报告"
                value={stats?.monthly_reports || 0}
                prefix={<FileTextOutlined />}
                suffix={
                  <span style={{ fontSize: 14 }}>
                    {stats && stats.monthly_trend > 0 ? (
                      <Text type="success">
                        <ArrowUpOutlined /> {stats.monthly_trend.toFixed(1)}%
                      </Text>
                    ) : (
                      <Text type="danger">
                        <ArrowDownOutlined /> {Math.abs(stats?.monthly_trend || 0).toFixed(1)}%
                      </Text>
                    )}
                  </span>
                }
              />
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="高风险项"
                value={stats?.high_risk_items || 0}
                prefix={<WarningOutlined />}
                valueStyle={{ color: '#cf1322' }}
                suffix={
                  <span style={{ fontSize: 14 }}>
                    {stats && stats.risk_trend < 0 ? (
                      <Text type="success">
                        <ArrowDownOutlined /> {Math.abs(stats.risk_trend).toFixed(1)}%
                      </Text>
                    ) : (
                      <Text type="danger">
                        <ArrowUpOutlined /> {stats?.risk_trend.toFixed(1)}%
                      </Text>
                    )}
                  </span>
                }
              />
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="OKR完成度"
                value={stats?.okr_completion || 0}
                prefix={<TrophyOutlined />}
                suffix={
                  <span style={{ fontSize: 14 }}>
                    %
                    {stats && stats.okr_trend > 0 ? (
                      <Text type="success" style={{ marginLeft: 8 }}>
                        <ArrowUpOutlined /> {stats.okr_trend.toFixed(1)}%
                      </Text>
                    ) : (
                      <Text type="danger" style={{ marginLeft: 8 }}>
                        <ArrowDownOutlined /> {Math.abs(stats?.okr_trend || 0).toFixed(1)}%
                      </Text>
                    )}
                  </span>
                }
              />
            </Card>
          </Col>
        </Row>

        {/* Charts Row */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={24} lg={8}>
            <RiskPieChart data={riskDistribution} />
          </Col>
          <Col xs={24} lg={16}>
            <OkrTrendChart data={okrTrendData} />
          </Col>
        </Row>

        {/* Timeline Chart */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={24}>
            <ReportTimelineChart data={timelineData} />
          </Col>
        </Row>

        {/* Recent Reports Table */}
        <Card
          title="📝 最近报告"
          style={{ marginBottom: 24 }}
          extra={
            <Button type="primary" onClick={() => navigate('/reports')}>
              查看所有报告
            </Button>
          }
        >
          <Table
            dataSource={recentReports}
            columns={columns}
            rowKey="id"
            loading={loading}
            pagination={false}
          />
        </Card>
      </Content>
    </Layout>
  )
}
