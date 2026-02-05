import { useState, useEffect } from 'react'
import {
  Card, Table, Space, Typography, Button, Input, Tag,
  message, Modal, Descriptions, Tabs
} from 'antd'
import {
  DatabaseOutlined, EyeOutlined, SearchOutlined,
  ReloadOutlined, InfoCircleOutlined, DeleteOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons'
import { queryAPI } from '../api'

const { Title, Text } = Typography
const { Search } = Input

function DBManagePage() {
  const [tables, setTables] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchText, setSearchText] = useState('')
  const [selectedTable, setSelectedTable] = useState(null)
  const [tableData, setTableData] = useState(null)
  const [tableSchema, setTableSchema] = useState(null)
  const [previewLoading, setPreviewLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('list')

  useEffect(() => {
    loadTables()
  }, [])

  const loadTables = async () => {
    setLoading(true)
    try {
      const response = await queryAPI.getTables()
      if (response.data.success) {
        setTables(response.data.tables)
      }
    } catch (err) {
      message.error('加载表列表失败: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const previewTable = async (tableName, limit = 50) => {
    setSelectedTable(tableName)
    setPreviewLoading(true)
    setTableData(null)
    setTableSchema(null)

    try {
      // 并行获取表数据和表结构
      const [dataRes, schemaRes] = await Promise.all([
        queryAPI.previewTable(tableName, limit),
        queryAPI.getTableSchema(tableName)
      ])

      if (dataRes.data.success) {
        setTableData(dataRes.data)
      }

      if (schemaRes.data) {
        setTableSchema(schemaRes.data)
      }

      message.success(`已加载表 ${tableName}`)
      // 自动切换到预览标签页
      setActiveTab('preview')
    } catch (err) {
      message.error('预览表失败: ' + err.message)
    } finally {
      setPreviewLoading(false)
    }
  }

  const deleteTable = (tableName) => {
    Modal.confirm({
      title: '确认删除',
      icon: <ExclamationCircleOutlined />,
      content: `确定要删除表 "${tableName}" 吗？此操作不可恢复！`,
      okText: '确认删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          const response = await queryAPI.deleteTable(tableName)
          if (response.data.success) {
            message.success(response.data.message || '表删除成功')
            // 刷新表列表
            loadTables()
            // 如果删除的是当前预览的表，清空预览
            if (selectedTable === tableName) {
              setSelectedTable(null)
              setTableData(null)
              setTableSchema(null)
              setActiveTab('list')
            }
          } else {
            message.error('删除失败: ' + (response.data.error || '未知错误'))
          }
        } catch (err) {
          message.error('删除失败: ' + err.message)
        }
      }
    })
  }

  const filteredTables = tables.filter(table =>
    table.toLowerCase().includes(searchText.toLowerCase())
  )

  const tableColumns = [
    {
      title: '序号',
      key: 'index',
      width: 80,
      render: (_, __, index) => index + 1
    },
    {
      title: '表名',
      dataIndex: 'name',
      key: 'name',
      render: (name) => (
        <Space>
          <DatabaseOutlined />
          <Text strong>{name}</Text>
        </Space>
      )
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_, record) => (
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => previewTable(record.name)}
          >
            预览
          </Button>
          <Button
            danger
            size="small"
            icon={<DeleteOutlined />}
            onClick={() => deleteTable(record.name)}
          >
            删除
          </Button>
        </Space>
      )
    }
  ]

  const tableListDataSource = filteredTables.map(name => ({
    key: name,
    name
  }))

  const dataColumns = tableData?.columns?.map(col => ({
    title: col,
    dataIndex: col,
    key: col,
    ellipsis: true,
    width: 150
  })) || []

  const dataSource = tableData?.data?.map((row, idx) => ({
    ...row,
    key: idx
  })) || []

  const tabItems = [
    {
      key: 'list',
      label: (
        <span>
          <DatabaseOutlined /> 表列表
        </span>
      ),
      children: (
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <Space>
            <Search
              placeholder="搜索表名"
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              style={{ width: 300 }}
              allowClear
            />
            <Button
              icon={<ReloadOutlined />}
              onClick={loadTables}
              loading={loading}
            >
              刷新
            </Button>
            <Tag color="blue">{filteredTables.length} 个表</Tag>
          </Space>

          <Table
            columns={tableColumns}
            dataSource={tableListDataSource}
            loading={loading}
            pagination={{
              pageSize: 20,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 个表`
            }}
          />
        </Space>
      )
    },
    {
      key: 'preview',
      label: (
        <span>
          <EyeOutlined /> 数据预览
        </span>
      ),
      children: (
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          {!selectedTable ? (
            <Card>
              <div style={{ textAlign: 'center', padding: '60px 0' }}>
                <DatabaseOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />
                <Text type="secondary" style={{ marginTop: 16, display: 'block', fontSize: 16 }}>
                  请从表列表中选择一个表进行预览
                </Text>
              </div>
            </Card>
          ) : (
            <>
              {tableSchema && (
                <Card
                  title={
                    <Space>
                      <InfoCircleOutlined />
                      <Text strong>表结构: {selectedTable}</Text>
                    </Space>
                  }
                  size="small"
                >
                  <pre className="sql-code">{tableSchema.build_statement}</pre>
                </Card>
              )}

              <Card
                title={
                  <Space>
                    <EyeOutlined />
                    <Text strong>数据预览: {selectedTable}</Text>
                    {tableData && (
                      <Tag color="blue">{tableData.total_rows} 条记录</Tag>
                    )}
                  </Space>
                }
                extra={
                  <Space>
                    <Button
                      size="small"
                      onClick={() => previewTable(selectedTable, 100)}
                      loading={previewLoading}
                    >
                      加载更多 (100条)
                    </Button>
                    <Button
                      size="small"
                      onClick={() => previewTable(selectedTable, 500)}
                      loading={previewLoading}
                    >
                      加载更多 (500条)
                    </Button>
                  </Space>
                }
              >
                {previewLoading ? (
                  <div style={{ textAlign: 'center', padding: '40px 0' }}>
                    <Text type="secondary">加载中...</Text>
                  </div>
                ) : tableData ? (
                  <Table
                    columns={dataColumns}
                    dataSource={dataSource}
                    pagination={{
                      pageSize: 20,
                      showSizeChanger: true,
                      showTotal: (total) => `共 ${total} 条记录`
                    }}
                    scroll={{ x: 'max-content' }}
                    size="small"
                  />
                ) : (
                  <div style={{ textAlign: 'center', padding: '40px 0' }}>
                    <Text type="secondary">暂无数据</Text>
                  </div>
                )}
              </Card>
            </>
          )}
        </Space>
      )
    }
  ]

  return (
    <div className="page-container">
      <div className="page-header">
        <Title level={2}>
          <DatabaseOutlined /> 数据库管理
        </Title>
        <Text type="secondary">
          浏览数据库表结构和数据，支持快速预览和搜索
        </Text>
      </div>

      <Card bordered={false}>
        <Tabs items={tabItems} activeKey={activeTab} onChange={setActiveTab} />
      </Card>
    </div>
  )
}

export default DBManagePage
