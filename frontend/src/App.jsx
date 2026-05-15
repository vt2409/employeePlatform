import React from 'react'
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu, Typography, theme } from 'antd'
import {
  TeamOutlined,
  BarChartOutlined,
  DashboardOutlined,
} from '@ant-design/icons'
import EmployeesPage from './pages/EmployeesPage'
import InsightsPage from './pages/InsightsPage'

const { Header, Sider, Content } = Layout
const { Title } = Typography

export default function App() {
  const navigate = useNavigate()
  const location = useLocation()
  const { token } = theme.useToken()

  const menuItems = [
    { key: '/employees', icon: <TeamOutlined />, label: 'Employees' },
    { key: '/insights', icon: <BarChartOutlined />, label: 'Insights' },
  ]

  const selectedKey = location.pathname === '/' ? '/employees' : location.pathname

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider theme="dark" width={220}>
        <div style={{ padding: '20px 16px', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
          <DashboardOutlined style={{ color: '#1677ff', fontSize: 20, marginRight: 8 }} />
          <span style={{ color: '#fff', fontWeight: 700, fontSize: 16 }}>SalaryManager</span>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedKey]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ marginTop: 8 }}
        />
      </Sider>

      <Layout>
        <Header style={{
          background: token.colorBgContainer,
          borderBottom: `1px solid ${token.colorBorderSecondary}`,
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
        }}>
          <Title level={5} style={{ margin: 0, color: token.colorTextSecondary }}>
            HR Management Portal
          </Title>
        </Header>

        <Content style={{ margin: '24px', background: token.colorBgLayout }}>
          <Routes>
            <Route path="/" element={<EmployeesPage />} />
            <Route path="/employees" element={<EmployeesPage />} />
            <Route path="/insights" element={<InsightsPage />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  )
}
