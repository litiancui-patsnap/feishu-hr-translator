import { useEffect, useState } from 'react'
import {
  Layout,
  Card,
  Table,
  Tag,
  Button,
  Space,
  Input,
  Select,
  DatePicker,
  message,
  Avatar,
  Typography,
} from 'antd'
import {
  SearchOutlined,
  ReloadOutlined,
  UserOutlined,
  LogoutOutlined,
  DownloadOutlined,
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { Dayjs } from 'dayjs'
import { dashboardAPI } from '../api/dashboard'
import { useAuth } from '../contexts/AuthContext'
import type { ReportSummary } from '../types'
import { exportReportsToExcel, downloadExportFile } from '../utils/export'

const { Header, Content } = Layout
const { Title, Text } = Typography
const { RangePicker } = DatePicker

export default function ReportsListPage() {
  const [reports, setReports] = useState<ReportSummary[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)

  // Filter states
  const [riskLevel, setRiskLevel] = useState<string | undefined>(undefined)
  const [periodType, setPeriodType] = useState<string | undefined>(undefined)
  const [userName, setUserName] = useState<string>('')
  const [searchKeyword, setSearchKeyword] = useState<string>('')
  const [dateRange, setDateRange] = useState<[Dayjs | null, Dayjs | null] | null>(null)

  const { user, logout } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    loadReports()
  }, [currentPage, pageSize, riskLevel, periodType, userName, searchKeyword, dateRange])

  const loadReports = async () => {
    setLoading(true)
    try {
      const result = await dashboardAPI.getReportsList({
        page: currentPage,
        page_size: pageSize,
        risk_level: riskLevel,
        period_type: periodType,
        user_name: userName || undefined,
        search: searchKeyword || undefined,
        start_date: dateRange?.[0]?.format('YYYY-MM-DD'),
        end_date: dateRange?.[1]?.format('YYYY-MM-DD'),
      })
      setReports(result.items)
      setTotal(result.total)
    } catch (error) {
      message.error('加载报告列表失败')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setRiskLevel(undefined)
    setPeriodType(undefined)
    setUserName('')
    setSearchKeyword('')
    setDateRange(null)
    setCurrentPage(1)
  }

  const handleExportExcel = () => {
    if (reports.length === 0) {
      message.warning('没有数据可导出')
      return
    }
    try {
      exportReportsToExcel(reports, '报告列表')
      message.success('导出成功')
    } catch (error) {
      message.error('导出失败')
      console.error(error)
    }
  }

  const handleExportCSV = async () => {
    try {
      const params = new URLSearchParams()
      if (riskLevel) params.append('risk_level', riskLevel)
      if (periodType) params.append('period_type', periodType)
      if (userName) params.append('user_name', userName)
      if (searchKeyword) params.append('search', searchKeyword)
      if (dateRange?.[0]) params.append('start_date', dateRange[0].format('YYYY-MM-DD'))
      if (dateRange?.[1]) params.append('end_date', dateRange[1].format('YYYY-MM-DD'))

      const url = `http://localhost:8080/api/dashboard/reports/export?${params.toString()}`
      const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
      await downloadExportFile(url, `reports_export_${timestamp}.csv`)
      message.success('导出成功')
    } catch (error) {
      message.error('导出失败')
      console.error(error)
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

  const getPeriodText = (type: string) => {
    const typeMap: Record<string, string> = {
      daily: '日报',
      weekly: '周报',
      monthly: '月报',
    }
    return typeMap[type] || type
  }

  const columns = [
    {
      title: '提交人',
      dataIndex: 'user_name',
      key: 'user_name',
      width: 150,
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
      width: 100,
      render: (type: string) => getPeriodText(type),
    },
    {
      title: '报告时间',
      key: 'period',
      width: 200,
      render: (_: any, record: ReportSummary) => {
        if (record.period_start && record.period_end) {
          return `${record.period_start} ~ ${record.period_end}`
        }
        return record.created_at
      },
    },
    {
      title: '风险等级',
      dataIndex: 'risk_level',
      key: 'risk_level',
      width: 100,
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
        <Text ellipsis style={{ maxWidth: 400 }}>
          {text}
        </Text>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
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
          <Button type="link" onClick={() => navigate('/dashboard')}>
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
          报告列表
        </Title>

        {/* Filter Section */}
        <Card style={{ marginBottom: 24 }}>
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            <Space wrap>
              <Select
                placeholder="风险等级"
                style={{ width: 120 }}
                allowClear
                value={riskLevel}
                onChange={setRiskLevel}
                options={[
                  { label: '低风险', value: 'low' },
                  { label: '中风险', value: 'medium' },
                  { label: '高风险', value: 'high' },
                ]}
              />
              <Select
                placeholder="报告周期"
                style={{ width: 120 }}
                allowClear
                value={periodType}
                onChange={setPeriodType}
                options={[
                  { label: '日报', value: 'daily' },
                  { label: '周报', value: 'weekly' },
                  { label: '月报', value: 'monthly' },
                ]}
              />
              <Input
                placeholder="提交人姓名"
                style={{ width: 150 }}
                value={userName}
                onChange={(e) => setUserName(e.target.value)}
                allowClear
              />
              <RangePicker
                value={dateRange}
                onChange={setDateRange}
                format="YYYY-MM-DD"
                placeholder={['开始日期', '结束日期']}
              />
              <Input.Search
                placeholder="搜索关键词"
                style={{ width: 200 }}
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                onSearch={loadReports}
                enterButton={<SearchOutlined />}
                allowClear
              />
              <Button icon={<ReloadOutlined />} onClick={handleReset}>
                重置
              </Button>
            </Space>
          </Space>
        </Card>

        {/* Reports Table */}
        <Card
          extra={
            <Space>
              <Button
                type="default"
                icon={<DownloadOutlined />}
                onClick={handleExportExcel}
                disabled={reports.length === 0}
              >
                导出 Excel
              </Button>
              <Button
                type="default"
                icon={<DownloadOutlined />}
                onClick={handleExportCSV}
              >
                导出 CSV (全部)
              </Button>
            </Space>
          }
        >
          <Table
            dataSource={reports}
            columns={columns}
            rowKey="id"
            loading={loading}
            pagination={{
              current: currentPage,
              pageSize: pageSize,
              total: total,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `共 ${total} 条记录`,
              onChange: (page, size) => {
                setCurrentPage(page)
                setPageSize(size)
              },
              pageSizeOptions: ['10', '20', '50', '100'],
            }}
          />
        </Card>
      </Content>
    </Layout>
  )
}
