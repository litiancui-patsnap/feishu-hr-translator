import { Card } from 'antd'
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

interface OkrTrendChartProps {
  data: Array<{
    date: string
    okr_completion: number
    report_count: number
  }>
}

export default function OkrTrendChart({ data }: OkrTrendChartProps) {
  if (!data || data.length === 0) {
    return (
      <Card title="OKR 完成趋势">
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
    <Card title="OKR 完成趋势（最近30天）">
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={formattedData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="dateLabel"
            angle={-45}
            textAnchor="end"
            height={80}
            tick={{ fontSize: 12 }}
          />
          <YAxis
            label={{ value: 'OKR 完成度 (%)', angle: -90, position: 'insideLeft' }}
            domain={[0, 100]}
          />
          <Tooltip
            labelFormatter={(value, payload) => {
              if (payload && payload.length > 0) {
                return payload[0].payload.date
              }
              return value
            }}
            formatter={(value: any, name: string) => {
              if (name === 'okr_completion') {
                return [`${value}%`, 'OKR 完成度']
              }
              if (name === 'report_count') {
                return [value, '报告数量']
              }
              return [value, name]
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="okr_completion"
            stroke="#1890ff"
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
            name="OKR 完成度"
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  )
}
