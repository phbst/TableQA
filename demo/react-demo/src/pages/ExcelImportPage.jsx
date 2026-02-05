import { useState } from 'react'
import {
  Card, Steps, Input, Button, Table, Space, Typography, message,
  Select, Upload, Alert, Tag, Divider
} from 'antd'
import {
  UploadOutlined, FileExcelOutlined, EyeOutlined,
  CheckCircleOutlined, DatabaseOutlined, ReloadOutlined,
  InboxOutlined
} from '@ant-design/icons'
import { queryAPI } from '../api'

const { Title, Text } = Typography
const { Dragger } = Upload

function ExcelImportPage() {
  const [currentStep, setCurrentStep] = useState(0)
  const [uploadedFile, setUploadedFile] = useState(null)
  const [filePath, setFilePath] = useState('')
  const [sheets, setSheets] = useState([])
  const [selectedSheet, setSelectedSheet] = useState(null)
  const [tableName, setTableName] = useState('')
  const [previewData, setPreviewData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [importResult, setImportResult] = useState(null)

  // 文件上传配置
  const uploadProps = {
    name: 'file',
    multiple: false,
    accept: '.xlsx,.xls',
    beforeUpload: (file) => {
      // 检查文件类型
      const isExcel = file.name.endsWith('.xlsx') || file.name.endsWith('.xls')
      if (!isExcel) {
        message.error('只能上传 Excel 文件（.xlsx 或 .xls）')
        return false
      }

      // 检查文件大小（限制50MB）
      const isLt50M = file.size / 1024 / 1024 < 50
      if (!isLt50M) {
        message.error('文件大小不能超过 50MB')
        return false
      }

      handleFileUpload(file)
      return false // 阻止自动上传
    },
    onDrop: (e) => {
      console.log('Dropped files', e.dataTransfer.files)
    },
  }

  // 处理文件上传
  const handleFileUpload = async (file) => {
    setLoading(true)
    try {
      const response = await queryAPI.uploadExcel(file)

      if (response.data.success) {
        setUploadedFile(file)
        setFilePath(response.data.file_path)
        message.success(`文件上传成功: ${file.name}`)

        // 自动读取工作表
        await handleGetSheets(response.data.file_path)
      } else {
        message.error('文件上传失败')
      }
    } catch (err) {
      message.error('文件上传失败: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  // 获取Excel文件的sheets
  const handleGetSheets = async (path) => {
    setLoading(true)
    try {
      const response = await queryAPI.getExcelSheets({ excel_path: path })

      if (response.data.success) {
        setSheets(response.data.sheets)
        message.success(`成功读取 ${response.data.count} 个工作表`)
        setCurrentStep(1)
      } else {
        message.error(response.data.error || '读取失败')
      }
    } catch (err) {
      message.error('读取Excel文件失败: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  // 预览选中的sheet
  const handlePreview = async () => {
    if (!selectedSheet) {
      message.warning('请选择一个工作表')
      return
    }

    if (!tableName.trim()) {
      message.warning('请输入目标表名')
      return
    }

    setLoading(true)
    try {
      const response = await queryAPI.importExcel({
        excel_path: filePath,
        sheet_name: selectedSheet,
        table_name: `preview_${tableName.trim()}`,
        if_exists: 'replace'
      })

      if (response.data.success) {
        setPreviewData(response.data)
        message.success('预览数据加载成功')
        setCurrentStep(2)
      } else {
        message.error(response.data.error || '预览失败')
      }
    } catch (err) {
      message.error('预览失败: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  // 确认导入
  const handleImport = async () => {
    setLoading(true)
    try {
      const response = await queryAPI.importExcel({
        excel_path: filePath,
        sheet_name: selectedSheet,
        table_name: tableName.trim(),
        if_exists: 'replace'
      })

      if (response.data.success) {
        setImportResult(response.data)

        // 自动更新配置
        try {
          await queryAPI.updateConfig({ mode: 'add' })
          message.success('数据导入成功，配置已更新！')
        } catch (configErr) {
          message.warning('数据导入成功，但配置更新失败')
        }

        setCurrentStep(3)
      } else {
        message.error(response.data.error || '导入失败')
      }
    } catch (err) {
      message.error('导入失败: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  // 重置
  const handleReset = () => {
    setCurrentStep(0)
    setUploadedFile(null)
    setFilePath('')
    setSheets([])
    setSelectedSheet(null)
    setTableName('')
    setPreviewData(null)
    setImportResult(null)
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <Title level={2}>
          <UploadOutlined /> Excel 表格导入
        </Title>
        <Text type="secondary">
          拖拽或选择Excel文件导入到数据库，支持预览和自动配置更新
        </Text>
      </div>

      <Card bordered={false}>
        <Steps current={currentStep} style={{ marginBottom: 32 }}>
          <Steps.Step title="上传文件" icon={<UploadOutlined />} />
          <Steps.Step title="选择工作表" icon={<FileExcelOutlined />} />
          <Steps.Step title="预览数据" icon={<EyeOutlined />} />
          <Steps.Step title="完成导入" icon={<CheckCircleOutlined />} />
        </Steps>

        {/* 步骤0: 上传文件 */}
        {currentStep === 0 && (
          <Card title="步骤 1: 上传Excel文件" size="small">
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <Dragger {...uploadProps} disabled={loading}>
                <p className="ant-upload-drag-icon">
                  <InboxOutlined style={{ color: '#1890ff' }} />
                </p>
                <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
                <p className="ant-upload-hint">
                  支持 .xlsx 和 .xls 格式，文件大小不超过 50MB
                </p>
              </Dragger>

              {uploadedFile && (
                <Alert
                  message="文件已上传"
                  description={
                    <Space direction="vertical">
                      <Text>文件名: {uploadedFile.name}</Text>
                      <Text>大小: {(uploadedFile.size / 1024).toFixed(2)} KB</Text>
                    </Space>
                  }
                  type="success"
                  showIcon
                />
              )}
            </Space>
          </Card>
        )}

        {/* 步骤1: 选择Sheet和表名 */}
        {currentStep === 1 && (
          <Card title="步骤 2: 选择工作表和目标表名" size="small">
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <Alert
                message="已上传文件"
                description={uploadedFile?.name}
                type="info"
                showIcon
                closable={false}
              />

              <div>
                <Text strong>选择工作表</Text>
                <Select
                  value={selectedSheet}
                  onChange={setSelectedSheet}
                  placeholder="选择一个工作表"
                  size="large"
                  style={{ width: '100%', marginTop: 8 }}
                >
                  {sheets.map(sheet => (
                    <Select.Option key={sheet} value={sheet}>
                      <Space>
                        <FileExcelOutlined />
                        {sheet}
                      </Space>
                    </Select.Option>
                  ))}
                </Select>
              </div>

              <div>
                <Text strong>目标表名</Text>
                <Input
                  value={tableName}
                  onChange={(e) => setTableName(e.target.value)}
                  placeholder="例如: user_data"
                  size="large"
                  style={{ marginTop: 8 }}
                  prefix={<DatabaseOutlined />}
                />
                <Text type="secondary" style={{ fontSize: 12, marginTop: 4, display: 'block' }}>
                  数据将导入到此表名，如果表已存在将被替换
                </Text>
              </div>

              <Space>
                <Button onClick={handleReset}>
                  重新上传
                </Button>
                <Button
                  type="primary"
                  size="large"
                  icon={<EyeOutlined />}
                  onClick={handlePreview}
                  loading={loading}
                  disabled={!selectedSheet || !tableName}
                >
                  预览数据
                </Button>
              </Space>
            </Space>
          </Card>
        )}

        {/* 步骤2: 预览数据 */}
        {currentStep === 2 && previewData && (
          <Card title="步骤 3: 预览数据" size="small">
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <Alert
                message="数据预览"
                description={
                  <Space direction="vertical">
                    <Text>文件: {uploadedFile?.name}</Text>
                    <Text>工作表: {selectedSheet}</Text>
                    <Text>目标表: {tableName}</Text>
                    <Space>
                      <Tag color="blue">行数: {previewData.row_count}</Tag>
                      <Tag color="green">列数: {previewData.column_count}</Tag>
                    </Space>
                  </Space>
                }
                type="success"
                showIcon
              />

              <div>
                <Text strong>列名映射</Text>
                <Table
                  size="small"
                  pagination={false}
                  style={{ marginTop: 8 }}
                  columns={[
                    { title: '原始列名', dataIndex: 'original', key: 'original' },
                    { title: '标准化列名', dataIndex: 'normalized', key: 'normalized' }
                  ]}
                  dataSource={previewData.original_columns?.map((col, idx) => ({
                    key: idx,
                    original: col,
                    normalized: previewData.normalized_columns[idx]
                  }))}
                />
              </div>

              <Divider />

              <div>
                <Text strong>建表语句</Text>
                <pre className="sql-code">{previewData.create_statement}</pre>
              </div>

              <Space>
                <Button onClick={() => setCurrentStep(1)}>
                  上一步
                </Button>
                <Button
                  type="primary"
                  size="large"
                  icon={<DatabaseOutlined />}
                  onClick={handleImport}
                  loading={loading}
                >
                  确认导入
                </Button>
              </Space>
            </Space>
          </Card>
        )}

        {/* 步骤3: 导入完成 */}
        {currentStep === 3 && importResult && (
          <Card title="步骤 4: 导入完成" size="small">
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <Alert
                message="导入成功！"
                description={
                  <Space direction="vertical">
                    <Text>表名: {importResult.table_name}</Text>
                    <Text>导入行数: {importResult.row_count}</Text>
                    <Text>列数: {importResult.column_count}</Text>
                  </Space>
                }
                type="success"
                showIcon
                icon={<CheckCircleOutlined />}
              />

              <div>
                <Text strong>建表语句</Text>
                <pre className="sql-code">{importResult.create_statement}</pre>
              </div>

              <Button
                type="primary"
                size="large"
                icon={<ReloadOutlined />}
                onClick={handleReset}
                block
              >
                导入更多数据
              </Button>
            </Space>
          </Card>
        )}
      </Card>
    </div>
  )
}

export default ExcelImportPage
