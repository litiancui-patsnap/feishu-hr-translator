import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Form, Input, Button, Checkbox, Card, message, Typography } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { authAPI } from '../api/auth'
import { useAuth } from '../contexts/AuthContext'
import type { LoginRequest } from '../types'

const { Title, Text } = Typography

export default function LoginPage() {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { login } = useAuth()

  const onFinish = async (values: LoginRequest) => {
    setLoading(true)
    try {
      const response = await authAPI.login(values)
      login(response.access_token, response.user)
      message.success('登录成功！')
      navigate('/dashboard')
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || '登录失败，请检查用户名和密码'
      message.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Card
        style={{
          width: 400,
          boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
          borderRadius: 8,
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <Title level={2} style={{ marginBottom: 8 }}>
            Feishu HR Translator
          </Title>
          <Text type="secondary">AI驱动的HR报告翻译系统</Text>
        </div>

        <Form
          name="login"
          initialValues={{ remember_me: true }}
          onFinish={onFinish}
          size="large"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="用户名"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
            />
          </Form.Item>

          <Form.Item>
            <Form.Item name="remember_me" valuePropName="checked" noStyle>
              <Checkbox>记住我（7天）</Checkbox>
            </Form.Item>
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              style={{ height: 42 }}
            >
              登录
            </Button>
          </Form.Item>
        </Form>

        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <Text type="secondary">
            演示账号：admin / admin123
          </Text>
        </div>
      </Card>
    </div>
  )
}
