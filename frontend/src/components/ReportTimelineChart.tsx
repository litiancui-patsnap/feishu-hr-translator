import { Card } from 'antd'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

interface ReportTimelineChartProps {
  data: Array<{
    date: string
    total: number
    daily: number
    weekly: number
    monthly: number
  }>
}

export default function ReportTimelineChart({ data }: ReportTimelineChartProps) {
  if (!data || data.length === 0) {
    return (
      <Card title="报告提交时间线">
        <div style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}>
          暂无数据
        </div>
      </Card>
    )
  }

  // Format data for display - only show every 3rd date label to avoid crowding
  const formattedData = data.map((item, index) => ({
    ...item,
    dateLabel: index % 3 === 0 ? item.date.substring(5) : '', // Show MM-DD format
  }))

  return (
    <Card title="报告提交时间线（最近30天）">
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={formattedData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="dateLabel"
            angle={-45}
            textAnchor="end"
            height={80}
            tick={{ fontSize: 12 }}
          />
          <YAxis label={{ value: '报告数量', angle: -90, position: 'insideLeft' }} />
          <Tooltip
            labelFormatter={(value, payload) => {
              if (payload && payload.length > 0) {
                return payload[0].payload.date
              }
              return value
            }}
            formatter={(value: any, name: string) => {
              const nameMap: Record<string, string> = {
                daily: '日报',
                weekly: '周报',
                monthly: '月报',
                total: '总计',
              }
              return [value, nameMap[name] || name]
            }}
          />
          <Legend
            formatter={(value: string) => {
              const nameMap: Record<string, string> = {
                daily: '日报',
                weekly: '周报',
                monthly: '月报',
                total: '总计',
              }
              return nameMap[value] || value
            }}
          />
          <Bar dataKey="daily" stackId="a" fill="#52c41a" name="daily" />
          <Bar dataKey="weekly" stackId="a" fill="#1890ff" name="weekly" />
          <Bar dataKey="monthly" stackId="a" fill="#fa8c16" name="monthly" />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  )
}
