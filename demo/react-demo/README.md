# TableQA React Demo

精致简洁的自然语言数据库查询演示界面

## 特性

- 🎨 现代化UI设计，使用Ant Design组件库
- 🚀 基于Vite构建，开发体验流畅
- 💡 支持多表查询和模型选择
- 📊 实时展示SQL和查询结果
- 🎯 响应式布局，支持移动端

## 快速开始

### 1. 安装依赖

```bash
cd demo/react-demo
npm install
```

### 2. 启动后端服务

确保后端API服务已启动（默认端口8080）:

```bash
# 在项目根目录
python run_server.py
```

### 3. 启动前端开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

## 使用说明

1. **输入查询问题**: 在文本框中输入自然语言问题
2. **选择数据表**: 从下拉列表中选择一个或多个相关表
3. **选择模型**: 选择用于生成SQL的模型
4. **执行查询**: 点击按钮或按 Ctrl/Cmd + Enter 执行查询
5. **查看结果**: 查看生成的SQL和查询结果表格

## 构建生产版本

```bash
npm run build
```

构建产物将生成在 `dist` 目录。

## 技术栈

- React 18
- Vite 5
- Ant Design 5
- Axios
- CSS3 (渐变背景、毛玻璃效果)

## 项目结构

```
react-demo/
├── index.html          # HTML入口
├── package.json        # 依赖配置
├── vite.config.js      # Vite配置
└── src/
    ├── main.jsx        # 应用入口
    ├── App.jsx         # 主组件
    ├── App.css         # 样式文件
    ├── index.css       # 全局样式
    └── api.js          # API封装
```

## API代理配置

开发环境下，所有 `/api/*` 请求会被代理到 `http://localhost:8080`。

如需修改后端地址，编辑 `vite.config.js` 中的 proxy 配置。
