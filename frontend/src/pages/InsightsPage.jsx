import React, { useState, useEffect } from 'react'
import {
  Row, Col, Card, Statistic, Table, Select, Typography,
  Spin, Tag, Alert, Tabs
} from 'antd'
import {
  TeamOutlined, GlobalOutlined, ApartmentOutlined, TrophyOutlined
} from '@ant-design/icons'
import { getOverviewInsights, getCountryInsights, getJobTitleInsights, getDepartmentInsights } from '../services/api'

const { Title, Text } = Typography
const { Option } = Select

function fmtSalary(val, currency = '') {
  return `${currency} ${Number(val).toLocaleString(undefined, { maximumFractionDigits: 0 })}`.trim()
}

function OverviewCards({ data }) {
  if (!data) return null
  return (
    <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
      <Col xs={12} sm={6}>
        <Card>
          <Statistic title="Total Employees" value={data.total_employees} prefix={<TeamOutlined />} />
        </Card>
      </Col>
      <Col xs={12} sm={6}>
        <Card>
          <Statistic title="Active Employees" value={data.active_employees} valueStyle={{ color: '#3f8600' }} />
        </Card>
      </Col>
      <Col xs={12} sm={6}>
        <Card>
          <Statistic title="Countries" value={data.total_countries} prefix={<GlobalOutlined />} />
        </Card>
      </Col>
      <Col xs={12} sm={6}>
        <Card>
          <Statistic title="Departments" value={data.total_departments} prefix={<ApartmentOutlined />} />
        </Card>
      </Col>
    </Row>
  )
}

function TopEarners({ earners }) {
  const columns = [
    { title: '#', render: (_, __, i) => i + 1, width: 40 },
    { title: 'Name', dataIndex: 'full_name' },
    { title: 'Title', dataIndex: 'job_title' },
    { title: 'Dept', dataIndex: 'department' },
    { title: 'Country', dataIndex: 'country', render: v => <Tag color="blue">{v}</Tag> },
    { title: 'Salary', render: (_, r) => fmtSalary(r.salary, r.currency) },
  ]
  return (
    <Card title={<><TrophyOutlined style={{ color: '#faad14', marginRight: 8 }} />Top 5 Earners</>}>
      <Table dataSource={earners} columns={columns} rowKey="id" pagination={false} size="small" />
    </Card>
  )
}

function EmploymentBreakdown({ breakdown }) {
  const colors = { 'Full-time': '#52c41a', 'Part-time': '#faad14', 'Contract': '#722ed1' }
  const total = Object.values(breakdown).reduce((a, b) => a + b, 0)
  return (
    <Card title="Employment Type Breakdown" style={{ height: '100%' }}>
      {Object.entries(breakdown).map(([type, count]) => (
        <div key={type} style={{ marginBottom: 12 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
            <Tag color={colors[type] || 'default'}>{type}</Tag>
            <Text>{count.toLocaleString()} ({((count / total) * 100).toFixed(1)}%)</Text>
          </div>
          <div style={{ background: '#f5f5f5', borderRadius: 4, height: 8 }}>
            <div style={{
              background: colors[type] || '#1677ff',
              width: `${(count / total) * 100}%`,
              height: '100%',
              borderRadius: 4,
            }} />
          </div>
        </div>
      ))}
    </Card>
  )
}

function CountryInsightsTab() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getCountryInsights().then(setData).finally(() => setLoading(false))
  }, [])

  const columns = [
    { title: 'Country', dataIndex: 'country', sorter: (a, b) => a.country.localeCompare(b.country) },
    { title: 'Code', dataIndex: 'country_code', render: c => <Tag color="blue">{c}</Tag>, width: 80 },
    { title: 'Currency', dataIndex: 'currency', width: 90 },
    { title: 'Headcount', dataIndex: 'headcount', sorter: (a, b) => a.headcount - b.headcount },
    { title: 'Min Salary', dataIndex: 'min_salary', render: (v, r) => fmtSalary(v, r.currency), sorter: (a, b) => a.min_salary - b.min_salary },
    { title: 'Max Salary', dataIndex: 'max_salary', render: (v, r) => fmtSalary(v, r.currency), sorter: (a, b) => a.max_salary - b.max_salary },
    { title: 'Avg Salary', dataIndex: 'avg_salary', render: (v, r) => fmtSalary(v, r.currency), sorter: (a, b) => a.avg_salary - b.avg_salary },
  ]

  return (
    <Table
      dataSource={data}
      columns={columns}
      rowKey="country_code"
      loading={loading}
      pagination={false}
      size="small"
    />
  )
}

function JobTitleInsightsTab() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [country, setCountry] = useState(null)

  const COUNTRIES = [
    { label: 'India', value: 'IN' }, { label: 'United States', value: 'US' },
    { label: 'United Kingdom', value: 'GB' }, { label: 'Germany', value: 'DE' },
    { label: 'Canada', value: 'CA' }, { label: 'Australia', value: 'AU' },
    { label: 'Singapore', value: 'SG' }, { label: 'Japan', value: 'JP' },
  ]

  const load = (c) => {
    setLoading(true)
    getJobTitleInsights(c ? { country_code: c } : {}).then(setData).finally(() => setLoading(false))
  }

  useEffect(() => { load(country) }, [country])

  const columns = [
    { title: 'Job Title', dataIndex: 'job_title', sorter: (a, b) => a.job_title.localeCompare(b.job_title) },
    { title: 'Country', dataIndex: 'country_code', render: c => <Tag color="blue">{c}</Tag> },
    { title: 'Headcount', dataIndex: 'headcount', sorter: (a, b) => a.headcount - b.headcount },
    { title: 'Avg Salary', dataIndex: 'avg_salary', render: v => Number(v).toLocaleString(undefined, { maximumFractionDigits: 0 }), sorter: (a, b) => a.avg_salary - b.avg_salary },
  ]

  return (
    <>
      <Select
        placeholder="Filter by country"
        style={{ width: 200, marginBottom: 16 }}
        allowClear
        onChange={v => setCountry(v || null)}
      >
        {COUNTRIES.map(c => <Option key={c.value} value={c.value}>{c.label}</Option>)}
      </Select>
      <Table
        dataSource={data}
        columns={columns}
        rowKey={(r) => `${r.job_title}-${r.country_code}`}
        loading={loading}
        pagination={{ pageSize: 15 }}
        size="small"
      />
    </>
  )
}

function DepartmentInsightsTab() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getDepartmentInsights().then(setData).finally(() => setLoading(false))
  }, [])

  const columns = [
    { title: 'Department', dataIndex: 'department', sorter: (a, b) => a.department.localeCompare(b.department) },
    { title: 'Headcount', dataIndex: 'headcount', sorter: (a, b) => a.headcount - b.headcount },
    { title: 'Avg Salary', dataIndex: 'avg_salary', render: v => Number(v).toLocaleString(undefined, { maximumFractionDigits: 0 }), sorter: (a, b) => a.avg_salary - b.avg_salary },
    { title: 'Total Payroll', dataIndex: 'total_payroll', render: v => Number(v).toLocaleString(undefined, { maximumFractionDigits: 0 }), sorter: (a, b) => a.total_payroll - b.total_payroll },
  ]

  return (
    <Table
      dataSource={data}
      columns={columns}
      rowKey="department"
      loading={loading}
      pagination={false}
      size="small"
    />
  )
}

export default function InsightsPage() {
  const [overview, setOverview] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getOverviewInsights().then(setOverview).finally(() => setLoading(false))
  }, [])

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '80px auto' }} />

  const tabItems = [
    { key: 'country', label: 'By Country', children: <CountryInsightsTab /> },
    { key: 'jobtitle', label: 'By Job Title', children: <JobTitleInsightsTab /> },
    { key: 'department', label: 'By Department', children: <DepartmentInsightsTab /> },
  ]

  return (
    <>
      <Title level={4} style={{ marginBottom: 16 }}>Salary Insights</Title>

      <OverviewCards data={overview} />

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={14}>
          {overview && <TopEarners earners={overview.top_earners} />}
        </Col>
        <Col xs={24} lg={10}>
          {overview && <EmploymentBreakdown breakdown={overview.employment_type_breakdown} />}
        </Col>
      </Row>

      <Card>
        <Tabs items={tabItems} defaultActiveKey="country" />
      </Card>
    </>
  )
}
