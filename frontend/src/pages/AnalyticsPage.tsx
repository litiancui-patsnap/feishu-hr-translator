import { useEffect, useState } from 'react'
import {
  Layout,
  Card,
  Row,
  Col,
  Statistic,
  Table,
  Typography,
  Space,
  Button,
  message,
  Progress,
  Tag,
} from 'antd'
import {
  TeamOutlined,
  FileTextOutlined,
  WarningOutlined,
  TrophyOutlined,
  LogoutOutlined,
  DashboardOutlined,
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { analyticsAPI } from '../api/analytics'
import type {
  UserSubmissionStats,
  RiskTrendData,
  OkrRankingData,
  TeamStatistics,
} from '../api/analytics'
import { useAuth } from '../contexts/AuthContext'

const { Header, Content } = Layout
const { Title, Text } = Typography

export default function AnalyticsPage() {
  const [userSubmissions, setUserSubmissions] = useState<UserSubmissionStats[]>([])
  const [riskTrend, setRiskTrend] = useState<RiskTrendData[]>([])
  const [okrRanking, setOkrRanking] = useState<OkrRankingData[]>([])
  const [teamStats, setTeamStats] = useState<TeamStatistics | null>(null)
  const [loading, setLoading] = useState(true)
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    loadAnalyticsData()
  }, [])

  const loadAnalyticsData = async () => {
    try {
      setLoading(true)
      const [submissions, risk, okr, team] = await Promise.all([
        analyticsAPI.getUserSubmissions(30),
        analyticsAPI.getRiskTrend(30),
        analyticsAPI.getOkrRanking(30),
        analyticsAPI.getTeamStats(),
      ])
      setUserSubmissions(submissions)
      setRiskTrend(risk)
      setOkrRanking(okr)
      setTeamStats(team)
    } catch (error) {
      message.error('加载统计数据失败')
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

  // User submission table columns
  const submissionColumns = [
    {
      title: '排名',
      key: 'rank',
      width: 80,
      render: (_: any, __: any, index: number) => index + 1,
    },
    {
      title: '姓名',
      dataIndex: 'user_name',
      key: 'user_name',
    },
    {
      title: '总报告数',
      dataIndex: 'total_reports',
      key: 'total_reports',
      sorter: (a: UserSubmissionStats, b: UserSubmissionStats) => a.total_reports - b.total_reports,
    },
    {
      title: '周报',
      dataIndex: 'weekly_reports',
      key: 'weekly_reports',
    },
    {
      title: '月报',
      dataIndex: 'monthly_reports',
      key: 'monthly_reports',
    },
    {
      title: '高风险项',
      dataIndex: 'high_risk_count',
      key: 'high_risk_count',
      render: (count: number) => (
        <Tag color={count > 0 ? 'red' : 'green'}>{count}</Tag>
      ),
    },
    {
      title: '平均OKR信心',
      dataIndex: 'avg_okr_confidence',
      key: 'avg_okr_confidence',
      render: (value: number) => (
        <Progress
          percent={Math.round(value)}
          size="small"
          status={value >= 70 ? 'success' : value >= 50 ? 'normal' : 'exception'}
        />
      ),
    },
  ]

  // OKR ranking table columns
  const okrColumns = [
    {
      title: '排名',
      key: 'rank',
      width: 80,
      render: (_: any, __: any, index: number) => {
        if (index === 0) return <Text strong style={{ color: '#faad14', fontSize: 18 }}>🥇</Text>
        if (index === 1) return <Text strong style={{ color: '#d9d9d9', fontSize: 18 }}>🥈</Text>
        if (index === 2) return <Text strong style={{ color: '#cd7f32', fontSize: 18 }}>🥉</Text>
        return index + 1
      },
    },
    {
      title: '姓名',
      dataIndex: 'user_name',
      key: 'user_name',
    },
    {
      title: 'OKR信心度',
      dataIndex: 'avg_confidence',
      key: 'avg_confidence',
      render: (value: number) => `${Math.round(value)}%`,
      sorter: (a: OkrRankingData, b: OkrRankingData) => a.avg_confidence - b.avg_confidence,
    },
    {
      title: '报告数',
      dataIndex: 'report_count',
      key: 'report_count',
    },
    {
      title: '命中目标数',
      dataIndex: 'hit_objectives_count',
      key: 'hit_objectives_count',
    },
    {
      title: '命中KR数',
      dataIndex: 'hit_krs_count',
      key: 'hit_krs_count',
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
          Feishu HR Translator - 统计分析
        </Title>
        <Space>
          <Button
            icon={<DashboardOutlined />}
            onClick={() => navigate('/dashboard')}
          >
            返回仪表盘
          </Button>
          <Text>欢迎, {user?.full_name || user?.username}</Text>
          <Button icon={<LogoutOutlined />} onClick={handleLogout}>
            退出
          </Button>
        </Space>
      </Header>

      <Content style={{ padding: 24 }}>
        <Title level={3} style={{ marginBottom: 24 }}>
          数据统计分析
        </Title>

        {/* Team Statistics Cards */}
        {teamStats && (
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="团队总人数"
                  value={teamStats.total_users}
                  prefix={<TeamOutlined />}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="总报告数"
                  value={teamStats.total_reports}
                  prefix={<FileTextOutlined />}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="人均报告数"
                  value={teamStats.avg_reports_per_user.toFixed(1)}
                  prefix={<FileTextOutlined />}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="高风险率"
                  value={Math.round(teamStats.high_risk_rate * 100)}
                  suffix="%"
                  prefix={<WarningOutlined />}
                  valueStyle={{
                    color: teamStats.high_risk_rate > 0.3 ? '#cf1322' : '#3f8600',
                  }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="平均OKR信心度"
                  value={Math.round(teamStats.avg_okr_confidence)}
                  suffix="%"
                  prefix={<TrophyOutlined />}
                  valueStyle={{
                    color: teamStats.avg_okr_confidence >= 70 ? '#3f8600' : '#cf1322',
                  }}
                />
              </Card>
            </Col>
          </Row>
        )}

        {/* Risk Trend Chart */}
        <Card title="风险趋势分析（最近30天）" style={{ marginBottom: 24 }}>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={riskTrend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                angle={-45}
                textAnchor="end"
                height={80}
                tick={{ fontSize: 12 }}
              />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="high"
                stroke="#f5222d"
                strokeWidth={2}
                name="高风险"
              />
              <Line
                type="monotone"
                dataKey="medium"
                stroke="#faad14"
                strokeWidth={2}
                name="中风险"
              />
              <Line
                type="monotone"
                dataKey="low"
                stroke="#52c41a"
                strokeWidth={2}
                name="低风险"
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        {/* User Submission Ranking */}
        <Card title="用户提交统计（最近30天）" style={{ marginBottom: 24 }}>
          <Table
            dataSource={userSubmissions}
            columns={submissionColumns}
            rowKey="user_name"
            loading={loading}
            pagination={{ pageSize: 10 }}
          />
        </Card>

        {/* OKR Achievement Ranking */}
        <Card title="OKR达成排行榜（最近30天）" style={{ marginBottom: 24 }}>
          <Table
            dataSource={okrRanking}
            columns={okrColumns}
            rowKey="user_name"
            loading={loading}
            pagination={{ pageSize: 10 }}
          />
        </Card>
      </Content>
    </Layout>
  )
}
