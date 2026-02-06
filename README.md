# TableQA - 自然语言数据库问答系统

一个基于大语言模型的自然语言转 SQL 查询系统，支持通过自然语言提问来查询数据库，并提供 AI 智能分析结果。

## 功能特性

- **自然语言查询 (NL2SQL)**: 使用自然语言提问，自动生成并执行 SQL 查询，AI 分析结果
- **SQL 调试工具**: 直接编写和执行 SQL 语句，支持历史记录
- **Excel 数据导入**: 快速导入 Excel 文件到数据库
- **数据库管理**: 查看和管理数据库表结构
- **多模型支持**: 支持配置多个 LLM 模型（Claude、GPT 等）
- **对话式交互**: 完整的对话历史记录和流程追踪

## 技术栈

### 后端
- **FastAPI**: 高性能 Web 框架
- **SQLite**: 轻量级数据库
- **Python 3.x**: 核心开发语言

### 前端
- **React 18**: UI 框架
- **Ant Design 5**: UI 组件库
- **Vite**: 构建工具
- **React Router**: 路由管理

## 项目结构

```
TableQA/
├── config/                 # 配置文件目录
│   ├── config.json        # 数据库配置
│   ├── model_config.json  # 模型配置
│   └── infer.template     # 推理模板
├── data/                  # 数据目录
│   └── sqlite3.db        # SQLite 数据库文件
├── demo/                  # 前端应用
│   └── react-demo/       # React 前端项目
│       ├── src/          # 源代码
│       └── package.json  # 依赖配置
├── src/                   # 后端源代码
│   ├── api/              # API 路由
│   ├── config/           # 配置加载
│   ├── models/           # 数据模型
│   ├── services/         # 业务逻辑
│   ├── utils/            # 工具函数
│   └── app.py            # FastAPI 应用入口
├── uploads/               # 文件上传目录
├── requirements.txt       # Python 依赖
└── run_server.py         # 服务启动脚本
```

## 快速开始

### 前置要求

- **Python**: 3.8 或更高版本
- **Node.js**: 16.x 或更高版本
- **npm**: 8.x 或更高版本

### 1. 安装依赖

#### 后端依赖
```bash
# 在项目根目录下
pip install -r requirements.txt
```

#### 前端依赖
```bash
# 进入前端目录
cd demo/react-demo

# 安装依赖
npm install
```

### 2. 配置

#### 配置模型 API
编辑 `config/model_config.json`：

```json
{
  "models": {
    "claude-sonnet-4-20250514": {
      "type": "online",
      "url": "https://api.anthropic.com/v1/messages",
      "model": "claude-sonnet-4-20250514",
      "api_key": "Bearer sk-ant-xxx",
      "description": "Claude Sonnet 4"
    },
    "gpt-4": {
      "type": "online",
      "url": "https://api.openai.com/v1/chat/completions",
      "model": "gpt-4",
      "api_key": "Bearer sk-xxx",
      "description": "GPT-4"
    }
  },
  "default_model": "claude-sonnet-4-20250514"
}
```

#### 配置数据库（可选）
编辑 `config/config.json`，默认使用 SQLite：

```json
{
  "database": {
    "type": "sqlite",
    "path": "data/sqlite3.db"
  }
}
```

### 3. 启动服务

#### 启动后端服务
```bash
# 在项目根目录下
python run_server.py
```

后端服务将在 `http://localhost:8080` 启动

#### 启动前端服务
```bash
# 在 demo/react-demo 目录下
npm run dev
```

前端服务将在 `http://localhost:5173` 启动（默认端口）

### 4. 访问应用

打开浏览器访问：`http://localhost:5173`

## 使用指南

### NL2SQL 对话

1. 在左侧面板输入自然语言问题，例如：
   - "查询所有用户的信息"
   - "统计每个部门的员工数量"
   - "找出销售额最高的前10个产品"

2. 选择要查询的数据表

3. 选择使用的 LLM 模型

4. 点击"开始查询"，系统会：
   - 自动生成 SQL 语句
   - 执行查询
   - AI 分析结果并给出解释

### SQL 调试

1. 切换到"SQL 调试"页面

2. 在编辑器中输入 SQL 语句

3. 点击"执行查询"查看结果

4. 支持查看历史执行记录

### Excel 导入

1. 切换到"Excel 导入"页面

2. 上传 Excel 文件

3. 配置导入选项（表名、是否覆盖等）

4. 点击导入，数据将自动导入数据库

### 数据库管理

1. 切换到"数据库管理"页面

2. 查看所有数据表

3. 查看表结构和数据预览

## API 文档

启动后端服务后，访问以下地址查看完整 API 文档：

- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

### 主要 API 端点

- `GET /health` - 健康检查
- `GET /tables` - 获取所有数据表
- `POST /query` - 执行 NL2SQL 查询
- `POST /chat` - AI 对话分析
- `POST /execute_sql` - 执行原始 SQL
- `POST /excel/upload` - 上传 Excel 文件
- `GET /models` - 获取可用模型列表

## 开发

### 后端开发

```bash
# 开发模式启动（自动重载）
uvicorn src.app:app --reload --host 0.0.0.0 --port 8080
```

### 前端开发

```bash
cd demo/react-demo
npm run dev
```

### 构建生产版本

```bash
# 前端构建
cd demo/react-demo
npm run build

# 构建产物在 demo/react-demo/dist 目录
```

## 常见问题

### 1. 后端启动失败

**问题**: `ModuleNotFoundError: No module named 'xxx'`

**解决**: 确保已安装所有依赖
```bash
pip install -r requirements.txt
```

### 2. 前端无法连接后端

**问题**: API 请求失败，CORS 错误

**解决**:
- 确保后端服务已启动在 `http://localhost:8080`
- 检查前端 API 配置文件 `demo/react-demo/src/api/index.js`

### 3. 模型 API 调用失败

**问题**: 401 Unauthorized 或 API Key 错误

**解决**:
- 检查 `config/model_config.json` 中的 API Key 是否正确
- 确保 API Key 格式为 `Bearer sk-xxx`
- 验证 API 端点 URL 是否正确

### 4. Excel 导入失败

**问题**: 文件上传或解析错误

**解决**:
- 确保 Excel 文件格式正确（.xlsx 或 .xls）
- 检查文件大小是否超过限制
- 确保 `uploads/` 目录存在且有写入权限

### 5. 数据库连接失败

**问题**: 无法连接到数据库

**解决**:
- 确保 `data/sqlite3.db` 文件存在
- 检查文件权限
- 如果文件不存在，系统会自动创建

## 许可证

本项目仅供学习和研究使用。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请通过 Issue 反馈。
