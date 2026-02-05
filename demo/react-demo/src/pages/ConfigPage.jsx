import { useState, useEffect } from 'react'
import { Card, Form, Input, Button, message, Space, Divider } from 'antd'
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons'
import { queryAPI } from '../api'
import './ConfigPage.css'

const { TextArea } = Input

function ConfigPage() {
  const [loading, setLoading] = useState(false)
  const [modelConfig, setModelConfig] = useState('')
  const [chatTemplate, setChatTemplate] = useState('')
  const [inferTemplate, setInferTemplate] = useState('')
  const [form] = Form.useForm()

  // 加载配置数据
  const loadConfigs = async () => {
    setLoading(true)
    try {
      const [modelRes, chatRes, inferRes] = await Promise.all([
        queryAPI.getModelConfig(),
        queryAPI.getTemplate('chat'),
        queryAPI.getTemplate('infer')
      ])

      const modelConfigStr = JSON.stringify(modelRes.data, null, 2)
      setModelConfig(modelConfigStr)
      setChatTemplate(chatRes.data)
      setInferTemplate(inferRes.data)

      form.setFieldsValue({
        modelConfig: modelConfigStr,
        chatTemplate: chatRes.data,
        inferTemplate: inferRes.data
      })

      message.success('配置加载成功')
    } catch (error) {
      message.error('加载配置失败: ' + (error.response?.data?.error || error.message))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadConfigs()
  }, [])

  // 保存模型配置
  const handleSaveModelConfig = async () => {
    try {
      await form.validateFields(['modelConfig'])
      const configValue = form.getFieldValue('modelConfig')
      const configObj = JSON.parse(configValue)

      setLoading(true)
      await queryAPI.saveModelConfig(configObj)
      message.success('模型配置保存成功')
      setModelConfig(configValue)
    } catch (error) {
      if (error.errorFields) {
        message.error('请检查配置格式')
      } else {
        message.error('保存失败: ' + (error.response?.data?.error || error.message))
      }
    } finally {
      setLoading(false)
    }
  }

  // 保存对话模板
  const handleSaveChatTemplate = async () => {
    try {
      await form.validateFields(['chatTemplate'])
      const templateValue = form.getFieldValue('chatTemplate')

      setLoading(true)
      await queryAPI.saveTemplate('chat', { content: templateValue })
      message.success('对话模板保存成功')
      setChatTemplate(templateValue)
    } catch (error) {
      if (error.errorFields) {
        message.error('请检查模板内容')
      } else {
        message.error('保存失败: ' + (error.response?.data?.error || error.message))
      }
    } finally {
      setLoading(false)
    }
  }

  // 保存推理模板
  const handleSaveInferTemplate = async () => {
    try {
      await form.validateFields(['inferTemplate'])
      const templateValue = form.getFieldValue('inferTemplate')

      setLoading(true)
      await queryAPI.saveTemplate('infer', { content: templateValue })
      message.success('推理模板保存成功')
      setInferTemplate(templateValue)
    } catch (error) {
      if (error.errorFields) {
        message.error('请检查模板内容')
      } else {
        message.error('保存失败: ' + (error.response?.data?.error || error.message))
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="config-page">
      <div className="config-header">
        <h2>系统配置</h2>
        <Button
          icon={<ReloadOutlined />}
          onClick={loadConfigs}
          loading={loading}
        >
          重新加载
        </Button>
      </div>

      <Form form={form} layout="vertical">
        {/* Model Config Section */}
        <Card
          title="模型配置 (model_config.json)"
          className="config-card"
          extra={
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={handleSaveModelConfig}
              loading={loading}
            >
              保存模型配置
            </Button>
          }
        >
          <Form.Item
            name="modelConfig"
            rules={[
              { required: true, message: '请输入模型配置' },
              {
                validator: (_, value) => {
                  try {
                    JSON.parse(value)
                    return Promise.resolve()
                  } catch (e) {
                    return Promise.reject(new Error('JSON 格式不正确'))
                  }
                }
              }
            ]}
          >
            <TextArea
              rows={15}
              placeholder="请输入 JSON 格式的模型配置"
              style={{ fontFamily: 'monospace' }}
            />
          </Form.Item>
        </Card>

        <Divider />

        {/* Chat Template Section */}
        <Card
          title="对话模板 (chat.template)"
          className="config-card"
          extra={
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={handleSaveChatTemplate}
              loading={loading}
            >
              保存对话模板
            </Button>
          }
        >
          <Form.Item
            name="chatTemplate"
            rules={[{ required: true, message: '请输入对话模板' }]}
          >
            <TextArea
              rows={10}
              placeholder="请输入对话模板内容"
              style={{ fontFamily: 'monospace' }}
            />
          </Form.Item>
        </Card>

        <Divider />

        {/* Infer Template Section */}
        <Card
          title="推理模板 (infer.template)"
          className="config-card"
          extra={
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={handleSaveInferTemplate}
              loading={loading}
            >
              保存推理模板
            </Button>
          }
        >
          <Form.Item
            name="inferTemplate"
            rules={[{ required: true, message: '请输入推理模板' }]}
          >
            <TextArea
              rows={12}
              placeholder="请输入推理模板内容"
              style={{ fontFamily: 'monospace' }}
            />
          </Form.Item>
        </Card>
      </Form>
    </div>
  )
}

export default ConfigPage
