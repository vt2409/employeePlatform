import React, { useState, useEffect, useCallback } from 'react'
import {
  Table, Button, Input, Select, Space, Tag, Typography, Modal,
  Form, InputNumber, DatePicker, Popconfirm, message, Card, Tooltip
} from 'antd'
import {
  PlusOutlined, SearchOutlined, EditOutlined, DeleteOutlined, EyeOutlined
} from '@ant-design/icons'
import dayjs from 'dayjs'
import { getEmployees, createEmployee, updateEmployee, deleteEmployee } from '../services/api'

const { Title } = Typography
const { Option } = Select

const EMPLOYMENT_TYPES = ['Full-time', 'Part-time', 'Contract']
const COUNTRIES = [
  { label: 'India', value: 'IN' },
  { label: 'United States', value: 'US' },
  { label: 'United Kingdom', value: 'GB' },
  { label: 'Germany', value: 'DE' },
  { label: 'Canada', value: 'CA' },
  { label: 'Australia', value: 'AU' },
  { label: 'Singapore', value: 'SG' },
  { label: 'Japan', value: 'JP' },
]
const COUNTRY_CURRENCY = { IN: 'INR', US: 'USD', GB: 'GBP', DE: 'EUR', CA: 'CAD', AU: 'AUD', SG: 'SGD', JP: 'JPY' }
const COUNTRY_NAME = Object.fromEntries(COUNTRIES.map(c => [c.value, c.label]))

export default function EmployeesPage() {
  const [employees, setEmployees] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [countryFilter, setCountryFilter] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingEmployee, setEditingEmployee] = useState(null)
  const [viewEmployee, setViewEmployee] = useState(null)
  const [form] = Form.useForm()

  const fetchEmployees = useCallback(async () => {
    setLoading(true)
    try {
      const params = { page }
      if (search) params.search = search
      if (countryFilter) params.country_code = countryFilter
      const data = await getEmployees(params)
      setEmployees(data.results)
      setTotal(data.count)
    } catch {
      message.error('Failed to fetch employees')
    } finally {
      setLoading(false)
    }
  }, [page, search, countryFilter])

  useEffect(() => { fetchEmployees() }, [fetchEmployees])

  const openCreate = () => {
    setEditingEmployee(null)
    form.resetFields()
    setModalOpen(true)
  }

  const openEdit = (record) => {
    setEditingEmployee(record)
    form.setFieldsValue({
      ...record,
      date_joined: dayjs(record.date_joined),
    })
    setModalOpen(true)
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      const payload = {
        ...values,
        date_joined: values.date_joined.format('YYYY-MM-DD'),
        currency: COUNTRY_CURRENCY[values.country_code] || 'USD',
        country: COUNTRY_NAME[values.country_code] || values.country_code,
      }
      if (editingEmployee) {
        await updateEmployee(editingEmployee.id, payload)
        message.success('Employee updated')
      } else {
        await createEmployee(payload)
        message.success('Employee created')
      }
      setModalOpen(false)
      fetchEmployees()
    } catch (err) {
      if (err?.response?.data) {
        const errors = Object.entries(err.response.data)
          .map(([k, v]) => `${k}: ${v}`)
          .join(', ')
        message.error(errors)
      }
    }
  }

  const handleDelete = async (id) => {
    try {
      await deleteEmployee(id)
      message.success('Employee deactivated')
      fetchEmployees()
    } catch {
      message.error('Failed to delete employee')
    }
  }

  const columns = [
    {
      title: 'Name', dataIndex: 'full_name', key: 'full_name',
      sorter: true, fixed: 'left', width: 180,
    },
    { title: 'Job Title', dataIndex: 'job_title', key: 'job_title', width: 180 },
    { title: 'Department', dataIndex: 'department', key: 'department', width: 140 },
    {
      title: 'Country', dataIndex: 'country_code', key: 'country_code', width: 120,
      render: (code) => <Tag color="blue">{code}</Tag>,
    },
    {
      title: 'Salary', dataIndex: 'salary', key: 'salary', width: 150,
      sorter: true,
      render: (salary, record) =>
        `${record.currency} ${Number(salary).toLocaleString()}`,
    },
    {
      title: 'Type', dataIndex: 'employment_type', key: 'employment_type', width: 110,
      render: (t) => {
        const colors = { 'Full-time': 'green', 'Part-time': 'orange', 'Contract': 'purple' }
        return <Tag color={colors[t] || 'default'}>{t}</Tag>
      },
    },
    {
      title: 'Joined', dataIndex: 'date_joined', key: 'date_joined', width: 110,
      render: d => dayjs(d).format('MMM D, YYYY'),
    },
    {
      title: 'Actions', key: 'actions', fixed: 'right', width: 120,
      render: (_, record) => (
        <Space>
          <Tooltip title="View">
            <Button size="small" icon={<EyeOutlined />} onClick={() => setViewEmployee(record)} />
          </Tooltip>
          <Tooltip title="Edit">
            <Button size="small" icon={<EditOutlined />} type="primary" ghost onClick={() => openEdit(record)} />
          </Tooltip>
          <Popconfirm
            title="Deactivate this employee?"
            onConfirm={() => handleDelete(record.id)}
            okText="Yes" cancelText="No"
          >
            <Tooltip title="Delete">
              <Button size="small" icon={<DeleteOutlined />} danger />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <Card>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={4} style={{ margin: 0 }}>Employees ({total.toLocaleString()})</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>Add Employee</Button>
      </div>

      <Space style={{ marginBottom: 16 }} wrap>
        <Input
          placeholder="Search name, title, department..."
          prefix={<SearchOutlined />}
          style={{ width: 280 }}
          value={search}
          onChange={e => { setSearch(e.target.value); setPage(1) }}
          allowClear
        />
        <Select
          placeholder="Filter by country"
          style={{ width: 180 }}
          allowClear
          onChange={v => { setCountryFilter(v); setPage(1) }}
        >
          {COUNTRIES.map(c => <Option key={c.value} value={c.value}>{c.label}</Option>)}
        </Select>
      </Space>

      <Table
        dataSource={employees}
        columns={columns}
        rowKey="id"
        loading={loading}
        scroll={{ x: 1100 }}
        pagination={{
          current: page,
          pageSize: 20,
          total,
          showSizeChanger: false,
          showTotal: (t) => `${t} employees`,
          onChange: setPage,
        }}
        size="small"
      />

      {/* Create / Edit Modal */}
      <Modal
        open={modalOpen}
        title={editingEmployee ? 'Edit Employee' : 'Add Employee'}
        onOk={handleSubmit}
        onCancel={() => setModalOpen(false)}
        okText={editingEmployee ? 'Update' : 'Create'}
        width={600}
        destroyOnClose
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="full_name" label="Full Name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="job_title" label="Job Title" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="department" label="Department" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="country_code" label="Country" rules={[{ required: true }]}>
            <Select>
              {COUNTRIES.map(c => <Option key={c.value} value={c.value}>{c.label}</Option>)}
            </Select>
          </Form.Item>
          <Form.Item name="salary" label="Salary" rules={[{ required: true }]}>
            <InputNumber style={{ width: '100%' }} min={0} step={1000} formatter={v => `${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')} />
          </Form.Item>
          <Form.Item name="employment_type" label="Employment Type" rules={[{ required: true }]}>
            <Select>
              {EMPLOYMENT_TYPES.map(t => <Option key={t} value={t}>{t}</Option>)}
            </Select>
          </Form.Item>
          <Form.Item name="date_joined" label="Date Joined" rules={[{ required: true }]}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>

      {/* View Modal */}
      <Modal
        open={!!viewEmployee}
        title="Employee Details"
        footer={<Button onClick={() => setViewEmployee(null)}>Close</Button>}
        onCancel={() => setViewEmployee(null)}
      >
        {viewEmployee && (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            {[
              ['Full Name', viewEmployee.full_name],
              ['Job Title', viewEmployee.job_title],
              ['Department', viewEmployee.department],
              ['Country', viewEmployee.country],
              ['Salary', `${viewEmployee.currency} ${Number(viewEmployee.salary).toLocaleString()}`],
              ['Employment Type', viewEmployee.employment_type],
              ['Date Joined', dayjs(viewEmployee.date_joined).format('MMMM D, YYYY')],
            ].map(([label, value]) => (
              <tr key={label} style={{ borderBottom: '1px solid #f0f0f0' }}>
                <td style={{ padding: '8px', color: '#888', width: '40%' }}>{label}</td>
                <td style={{ padding: '8px', fontWeight: 500 }}>{value}</td>
              </tr>
            ))}
          </table>
        )}
      </Modal>
    </Card>
  )
}
