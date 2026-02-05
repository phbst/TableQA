import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

export const queryAPI = {
  getTables: () => api.get('/tables'),

  getModels: () => api.get('/models'),

  getTableSchema: (tableName) => api.get(`/tables/${tableName}/schema`),

  executeQuery: (data) => api.post('/query', data),

  chat: (data) => api.post('/chat', data),

  previewTable: (tableName, limit = 50) =>
    api.get(`/table_preview/${tableName}`, { params: { limit } }),

  deleteTable: (tableName) =>
    api.delete(`/tables/${tableName}`),

  executeRawSQL: (data) => api.post('/execute_raw_sql', data),

  // Excel 导入相关
  uploadExcel: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/excel/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  getExcelSheets: (data) => api.post('/excel/sheets', data),

  importExcel: (data) => api.post('/excel/import', data),

  updateConfig: (data) => api.post('/excel/update_config', data),

  healthCheck: () => api.get('/health'),

  // 配置管理相关
  getModelConfig: () => api.get('/config/model'),

  saveModelConfig: (data) => api.post('/config/model', data),

  getTemplate: (templateType) => api.get(`/config/template/${templateType}`),

  saveTemplate: (templateType, data) => api.post(`/config/template/${templateType}`, data),
}

export default api
