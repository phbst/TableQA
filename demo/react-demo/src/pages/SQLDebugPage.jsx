import { useState, useEffect } from 'react'
import {
  Card, Input, Button, Table, Space, Typography, Tag,
  message, Alert, Tabs
} from 'antd'
import {
  PlayCircleOutlined, CodeOutlined, HistoryOutlined,
  DeleteOutlined, SaveOutlined
} from '@ant-design/icons'
import { queryAPI } from '../api'

const { TextArea } = Input
const { Title, Text } = Typography

function SQLDebugPage() {
  const [sql, setSql] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [history, setHistory] = useState([])

  useEffect(() => {
    // 从 localStorage 加载历史记录
    const savedHistory = localStorage.getItem('sql_history')
    if (savedHistory) {
      try {
        setHistory(JSON.parse(savedHistory))
      } catch (e) {
        console.error('Failed to load history:', e)
      }
    }
  }, [])

  const saveToHistory = (sqlText, success, resultData = null, errorMsg = null) => {
    const newItem = {
      id: Date.now(),
      sql: sqlText,
      success,
      result: resultData,
      error: errorMsg,
      timestamp: new Date().toLocaleString()
    }

    const newHistory = [newItem, ...history].slice(0, 20) // 保留最近20条
    setHistory(newHistory)
    localStorage.setItem('sql_history', JSON.stringify(newHistory))
  }

  const handleExecute = async () => {
    if (!sql.trim()) {
      message.warning('请输入 SQL 语句')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await queryAPI.executeRawSQL({ sql: sql.trim() })

      if (response.data.success) {
        setResult(response.data)
        message.success('执行成功!')
        saveToHistory(sql.trim(), true, response.data)
      } else {
        const errorMsg = response.data.error || '执行失败'
        setError(errorMsg)
        message.error('执行失败')
        saveToHistory(sql.trim(), false, null, errorMsg)
      }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message
      setError(errorMsg)
      message.error('请求失败: ' + errorMsg)
      saveToHistory(sql.trim(), false, null, errorMsg)
    } finally {
      setLoading(false)
    }
  }

  const loadFromHistory = (item) => {
    setSql(item.sql)
    if (item.success && item.result) {
      setResult(item.result)
      setError(null)
    } else if (item.error) {
      setError(item.error)
      setResult(null)
    }
  }

  const clearHistory = () => {
    setHistory([])
    localStorage.removeItem('sql_history')
    message.success('历史记录已清空')
  }

  const columns = result?.columns?.map(col => ({
    title: col,
    dataIndex: col,
    key: col,
    ellipsis: true,
  })) || []

  const dataSource = result?.data?.map((row, idx) => ({
    ...row,
    key: idx
  })) || []

  const tabItems = [
    {
      key: 'editor',
      label: (
        <span>
          <CodeOutlined /> SQL 编辑器
        </span>
      ),
      children: (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div>
            <Space style={{ marginBottom: 8 }}>
              <Text strong>SQL 语句</Text>
              <Text type="secondary" style={{ fontSize: 12 }}>
                (仅支持 SELECT 查询)
              </Text>
            </Space>
            <TextArea
              value={sql}
              onChange={(e) => setSql(e.target.value)}
              placeholder="输入 SQL 语句，例如: SELECT * FROM table_name LIMIT 10"
              autoSize={{ minRows: 10, maxRows: 20 }}
              style={{ fontFamily: 'Monaco, Consolas, monospace', fontSize: 14 }}
            />
          </div>

          <Space>
            <Button
              type="primary"
              size="large"
              icon={<PlayCircleOutlined />}
              onClick={handleExecute}
              loading={loading}
            >
              执行查询
            </Button>
            <Button
              onClick={() => {
                setSql('')
                setResult(null)
                setError(null)
              }}
            >
              清空
            </Button>
          </Space>

          {error && (
            <Alert
              message="执行错误"
              description={error}
              type="error"
              showIcon
              closable
              onClose={() => setError(null)}
            />
          )}

          {result && (
            <Card
              title={
                <Space>
                  <Text strong>查询结果</Text>
                  <Tag color="blue">{result.total_rows} 条记录</Tag>
                </Space>
              }
              bordered={false}
            >
              <Table
                columns={columns}
                dataSource={dataSource}
                pagination={{
                  pageSize: 20,
                  showSizeChanger: true,
                  showTotal: (total) => `共 ${total} 条记录`,
                }}
                scroll={{ x: 'max-content' }}
                size="middle"
              />
            </Card>
          )}
        </Space>
      ),
    },
    {
      key: 'history',
      label: (
        <span>
          <HistoryOutlined /> 执行历史
        </span>
      ),
      children: (
        <div>
          <Space style={{ marginBottom: 16 }}>
            <Text strong>最近执行的 SQL ({history.length})</Text>
            {history.length > 0 && (
              <Button
                danger
                size="small"
                icon={<DeleteOutlined />}
                onClick={clearHistory}
              >
                清空历史
              </Button>
            )}
          </Space>

          {history.length === 0 ? (
            <Card>
              <div style={{ textAlign: 'center', padding: '40px 0' }}>
                <HistoryOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
                <Text type="secondary" style={{ marginTop: 16, display: 'block' }}>
                  暂无执行历史
                </Text>
              </div>
            </Card>
          ) : (
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              {history.map((item) => (
                <Card
                  key={item.id}
                  size="small"
                  className={item.success ? 'history-success' : 'history-error'}
                  extra={
                    <Space>
                      <Tag color={item.success ? 'success' : 'error'}>
                        {item.success ? '成功' : '失败'}
                      </Tag>
                      <Button
                        type="link"
                        size="small"
                        onClick={() => loadFromHistory(item)}
                      >
                        加载
                      </Button>
                    </Space>
                  }
                >
                  <Space direction="vertical" size="small" style={{ width: '100%' }}>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {item.timestamp}
                    </Text>
                    <pre className="sql-code-small">{item.sql}</pre>
                    {item.error && (
                      <Text type="danger" style={{ fontSize: 12 }}>
                        错误: {item.error}
                      </Text>
                    )}
                    {item.success && item.result && (
                      <Text type="success" style={{ fontSize: 12 }}>
                        返回 {item.result.total_rows} 条记录
                      </Text>
                    )}
                  </Space>
                </Card>
              ))}
            </Space>
          )}
        </div>
      ),
    },
  ]

  return (
    <div className="page-container">
      <div className="page-header">
        <Title level={2}>
          <CodeOutlined /> SQL 调试工具
        </Title>
        <Text type="secondary">
          直接执行自定义 SQL 查询，支持历史记录管理
        </Text>
      </div>

      <Card bordered={false}>
        <Tabs items={tabItems} />
      </Card>
    </div>
  )
}

export default SQLDebugPage
