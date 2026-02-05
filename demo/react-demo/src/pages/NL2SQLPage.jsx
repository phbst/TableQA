import { useState, useEffect, useRef } from 'react'
import {
  Card, Input, Select, Button, Table, Space, Typography, Tag,
  Divider, message, Timeline, Spin
} from 'antd'
import {
  SearchOutlined, RobotOutlined, ThunderboltOutlined,
  CheckCircleOutlined, LoadingOutlined
} from '@ant-design/icons'
import { queryAPI } from '../api'

const { TextArea } = Input
const { Title, Text, Paragraph } = Typography

function NL2SQLPage() {
  const [query, setQuery] = useState('')
  const [tables, setTables] = useState([])
  const [selectedTables, setSelectedTables] = useState([])
  const [models, setModels] = useState([])
  const [selectedModel, setSelectedModel] = useState(null)
  const [loading, setLoading] = useState(false)

  // 对话历史
  const [conversationHistory, setConversationHistory] = useState([])
  const historyRef = useRef(null)

  useEffect(() => {
    loadInitialData()
  }, [])

  useEffect(() => {
    // 自动滚动到底部
    if (historyRef.current) {
      historyRef.current.scrollTop = historyRef.current.scrollHeight
    }
  }, [conversationHistory])

  const loadInitialData = async () => {
    try {
      const [tablesRes, modelsRes] = await Promise.all([
        queryAPI.getTables(),
        queryAPI.getModels()
      ])

      if (tablesRes.data.success) {
        setTables(tablesRes.data.tables)
      }

      if (modelsRes.data.success) {
        const modelList = Object.keys(modelsRes.data.models)
        setModels(modelList)
        setSelectedModel(modelsRes.data.default_model || modelList[0])
      }
    } catch (err) {
      message.error('加载初始数据失败: ' + err.message)
    }
  }

  const addToHistory = (item) => {
    setConversationHistory(prev => [...prev, { ...item, id: Date.now(), timestamp: Date.now() }])
  }

  const removeLastHistory = () => {
    setConversationHistory(prev => prev.slice(0, -1))
  }

  const handleQuery = async () => {
    if (!query.trim()) {
      message.warning('请输入查询问题')
      return
    }

    if (selectedTables.length === 0) {
      message.warning('请选择至少一个数据表')
      return
    }

    setLoading(true)

    // 添加用户问题到历史
    addToHistory({
      type: 'user',
      content: query.trim()
    })

    try {
      // 步骤1: 生成并执行 SQL
      addToHistory({
        type: 'loading',
        content: '正在生成并执行 SQL 查询...'
      })

      const queryResponse = await queryAPI.executeQuery({
        query: query.trim(),
        table_names: selectedTables,
        model_name: selectedModel
      })

      // 移除加载消息
      removeLastHistory()

      if (queryResponse.data.success) {
        // 添加完成消息
        addToHistory({
          type: 'success',
          content: '✅ SQL 查询执行完成'
        })

        // 显示 SQL 和查询结果
        addToHistory({
          type: 'sql',
          sql: queryResponse.data.sql,
          data: queryResponse.data.data,
          columns: queryResponse.data.columns,
          total_rows: queryResponse.data.total_rows
        })

        // 步骤2: 调用 Chat API 分析结果
        addToHistory({
          type: 'loading',
          content: '正在分析查询结果...'
        })

        // 将查询结果格式化为字符串
        const resultData = queryResponse.data.data
        const resultColumns = queryResponse.data.columns
        let tableInfo = ''

        if (resultData && resultData.length > 0) {
          // 格式化为表格字符串
          tableInfo = `查询结果（共 ${resultData.length} 条记录）：\n\n`
          tableInfo += resultColumns.join(' | ') + '\n'
          tableInfo += resultColumns.map(() => '---').join(' | ') + '\n'

          // 只取前10条数据，避免内容过长
          const displayData = resultData.slice(0, 20)
          displayData.forEach(row => {
            const rowValues = resultColumns.map(col => {
              const val = row[col]
              return val !== null && val !== undefined ? String(val) : ''
            })
            tableInfo += rowValues.join(' | ') + '\n'
          })

          if (resultData.length > 10) {
            tableInfo += `\n... 还有 ${resultData.length - 10} 条记录未显示`
          }
        } else {
          tableInfo = '查询结果为空'
        }

        const chatResponse = await queryAPI.chat({
          table_info: tableInfo,
          question: query.trim(),
          model_name: selectedModel
        })

        // 移除加载消息
        removeLastHistory()

        if (chatResponse.data.success) {
          // 添加完成消息
          addToHistory({
            type: 'success',
            content: '✅ 结果分析完成'
          })

          // 显示分析结果
          addToHistory({
            type: 'chat',
            content: chatResponse.data.answer,
            model: selectedModel
          })

          message.success('查询和分析完成!')
        } else {
          addToHistory({
            type: 'error',
            content: '分析失败: ' + (chatResponse.data.error || '未知错误')
          })
        }
      } else {
        addToHistory({
          type: 'error',
          content: queryResponse.data.error || 'SQL 查询失败'
        })
        message.error('查询失败')
      }
    } catch (err) {
      // 移除可能存在的加载消息
      if (conversationHistory.length > 0 && conversationHistory[conversationHistory.length - 1].type === 'loading') {
        removeLastHistory()
      }

      const errorMsg = err.response?.data?.detail || err.message
      addToHistory({
        type: 'error',
        content: '❌ 请求失败: ' + errorMsg
      })
      message.error('请求失败: ' + errorMsg)
    } finally {
      setLoading(false)
    }
  }

  const renderHistoryItem = (item) => {
    switch (item.type) {
      case 'user':
        return (
          <Card className="history-card user-card" size="small">
            <Space>
              <SearchOutlined style={{ color: '#1890ff' }} />
              <Text strong>用户问题:</Text>
            </Space>
            <Paragraph style={{ marginTop: 8, marginBottom: 0 }}>
              {item.content}
            </Paragraph>
          </Card>
        )

      case 'system':
        return (
          <Card className="history-card system-card" size="small">
            <Space>
              <LoadingOutlined style={{ color: '#faad14' }} />
              <Text type="secondary">{item.content}</Text>
            </Space>
          </Card>
        )

      case 'loading':
        return (
          <Card className="history-card system-card" size="small">
            <Space>
              <LoadingOutlined style={{ color: '#faad14' }} />
              <Text type="secondary">{item.content}</Text>
            </Space>
          </Card>
        )

      case 'success':
        return (
          <Card className="history-card" size="small" style={{ background: '#f6ffed', borderLeft: '4px solid #52c41a' }}>
            <Space>
              <CheckCircleOutlined style={{ color: '#52c41a' }} />
              <Text style={{ color: '#52c41a' }}>{item.content}</Text>
            </Space>
          </Card>
        )

      case 'chat':
        return (
          <Card className="history-card chat-card" size="small">
            <Space>
              <RobotOutlined style={{ color: '#52c41a' }} />
              <Text strong>AI 分析:</Text>
              <Tag color="green">{item.model}</Tag>
            </Space>
            <Paragraph style={{ marginTop: 8, marginBottom: 0, whiteSpace: 'pre-wrap' }}>
              {item.content}
            </Paragraph>
          </Card>
        )

      case 'sql':
        const columns = item.columns?.map(col => ({
          title: col,
          dataIndex: col,
          key: col,
          ellipsis: true,
        })) || []

        const dataSource = item.data?.map((row, idx) => ({
          ...row,
          key: idx
        })) || []

        return (
          <Card className="history-card sql-card" size="small">
            <Space>
              <CheckCircleOutlined style={{ color: '#52c41a' }} />
              <Text strong>查询结果:</Text>
              <Tag color="blue">{item.total_rows} 条记录</Tag>
            </Space>

            <div style={{ marginTop: 12 }}>
              <Text type="secondary">生成的 SQL:</Text>
              <pre className="sql-code">{item.sql}</pre>
            </div>

            <Divider style={{ margin: '12px 0' }} />

            <Table
              columns={columns}
              dataSource={dataSource}
              pagination={{
                pageSize: 5,
                size: 'small',
                showTotal: (total) => `共 ${total} 条`
              }}
              scroll={{ x: 'max-content' }}
              size="small"
            />
          </Card>
        )

      case 'error':
        return (
          <Card className="history-card error-card" size="small">
            <Space>
              <Text type="danger" strong>错误:</Text>
            </Space>
            <Paragraph type="danger" style={{ marginTop: 8, marginBottom: 0 }}>
              {item.content}
            </Paragraph>
          </Card>
        )

      default:
        return null
    }
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <Title level={2}>
          <ThunderboltOutlined /> NL2SQL + 智能对话
        </Title>
        <Text type="secondary">
          输入自然语言问题，系统将自动分析并执行查询，展示完整的推理过程
        </Text>
      </div>

      <div className="nl2sql-layout">
        <div className="input-panel">
          <Card title="查询配置" bordered={false}>
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <div>
                <Text strong>输入问题</Text>
                <TextArea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="例如: 查询所有基金的名称和规模"
                  autoSize={{ minRows: 4, maxRows: 8 }}
                  style={{ marginTop: 8 }}
                  disabled={loading}
                />
              </div>

              <div>
                <Text strong>选择数据表</Text>
                <Select
                  mode="multiple"
                  value={selectedTables}
                  onChange={setSelectedTables}
                  placeholder="选择一个或多个表"
                  style={{ width: '100%', marginTop: 8 }}
                  maxTagCount="responsive"
                  disabled={loading}
                >
                  {tables.map(table => (
                    <Select.Option key={table} value={table}>
                      {table}
                    </Select.Option>
                  ))}
                </Select>
              </div>

              <div>
                <Text strong>选择模型</Text>
                <Select
                  value={selectedModel}
                  onChange={setSelectedModel}
                  style={{ width: '100%', marginTop: 8 }}
                  disabled={loading}
                >
                  {models.map(model => (
                    <Select.Option key={model} value={model}>
                      {model}
                    </Select.Option>
                  ))}
                </Select>
              </div>

              <Button
                type="primary"
                size="large"
                icon={<SearchOutlined />}
                onClick={handleQuery}
                loading={loading}
                block
              >
                {loading ? '处理中...' : '开始查询'}
              </Button>

              {conversationHistory.length > 0 && (
                <Button
                  danger
                  onClick={() => setConversationHistory([])}
                  disabled={loading}
                  block
                >
                  清空历史
                </Button>
              )}
            </Space>
          </Card>
        </div>

        <div className="conversation-panel">
          <Card
            title="对话历史"
            bordered={false}
            className="conversation-card"
          >
            <div className="conversation-history" ref={historyRef}>
              {conversationHistory.length === 0 ? (
                <div className="empty-state">
                  <RobotOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
                  <Text type="secondary" style={{ marginTop: 16, display: 'block' }}>
                    开始提问，查看完整的查询过程
                  </Text>
                </div>
              ) : (
                <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                  {conversationHistory.map((item, idx) => (
                    <div key={idx}>
                      {renderHistoryItem(item)}
                    </div>
                  ))}
                </Space>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default NL2SQLPage
