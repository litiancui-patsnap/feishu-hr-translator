import { Card } from 'antd'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

interface RiskPieChartProps {
  data: {
    low: number
    medium: number
    high: number
  }
}

const COLORS = {
  low: '#52c41a',
  medium: '#faad14',
  high: '#f5222d',
}

const RISK_LABELS = {
  low: '低风险',
  medium: '中风险',
  high: '高风险',
}

export default function RiskPieChart({ data }: RiskPieChartProps) {
  const chartData = [
    { name: RISK_LABELS.low, value: data.low, color: COLORS.low },
    { name: RISK_LABELS.medium, value: data.medium, color: COLORS.medium },
    { name: RISK_LABELS.high, value: data.high, color: COLORS.high },
  ].filter(item => item.value > 0) // Only show non-zero values

  const total = data.low + data.medium + data.high

  if (total === 0) {
    return (
      <Card title="风险分布">
        <div style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}>
          暂无数据
        </div>
      </Card>
    )
  }

  return (
    <Card title="风险分布">
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${((percent ?? 0) * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </Card>
  )
}
