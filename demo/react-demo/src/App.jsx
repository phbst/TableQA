import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import { Layout, Menu } from 'antd'
import {
  MessageOutlined,
  CodeOutlined,
  DatabaseOutlined,
  UploadOutlined,
  SettingOutlined
} from '@ant-design/icons'
import NL2SQLPage from './pages/NL2SQLPage'
import SQLDebugPage from './pages/SQLDebugPage'
import DBManagePage from './pages/DBManagePage'
import ExcelImportPage from './pages/ExcelImportPage'
import ConfigPage from './pages/ConfigPage'
import './App.css'

const { Header, Content } = Layout

function AppContent() {
  const location = useLocation()

  const menuItems = [
    {
      key: '/',
      icon: <MessageOutlined />,
      label: <Link to="/">NL2SQL + 对话</Link>,
    },
    {
      key: '/sql-debug',
      icon: <CodeOutlined />,
      label: <Link to="/sql-debug">SQL 调试</Link>,
    },
    {
      key: '/db-manage',
      icon: <DatabaseOutlined />,
      label: <Link to="/db-manage">数据库管理</Link>,
    },
    {
      key: '/excel-import',
      icon: <UploadOutlined />,
      label: <Link to="/excel-import">导入表格</Link>,
    },
    {
      key: '/config',
      icon: <SettingOutlined />,
      label: <Link to="/config">系统配置</Link>,
    },
  ]

  return (
    <Layout className="app-layout">
      <Header className="app-header">
        <div className="logo">
          <DatabaseOutlined className="logo-icon" />
          <span className="logo-text">TableQA</span>
        </div>
        <Menu
          theme="light"
          mode="horizontal"
          selectedKeys={[location.pathname]}
          items={menuItems}
          className="nav-menu"
        />
      </Header>

      <Content className="app-content">
        <Routes>
          <Route path="/" element={<NL2SQLPage />} />
          <Route path="/sql-debug" element={<SQLDebugPage />} />
          <Route path="/db-manage" element={<DBManagePage />} />
          <Route path="/excel-import" element={<ExcelImportPage />} />
          <Route path="/config" element={<ConfigPage />} />
        </Routes>
      </Content>
    </Layout>
  )
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  )
}

export default App
