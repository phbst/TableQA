# 项目重构说明

## 重构概述

原始的 `server_es.py` 文件已被重构为模块化的项目结构，提高了代码的可维护性和可扩展性。

## 新的目录结构

```
src/
├── __init__.py                 # 包初始化文件
├── app.py                      # FastAPI 应用主入口
├── server_es.py               # 原始文件（保留作为参考）
│
├── config/                     # 配置管理模块
│   ├── __init__.py
│   ├── settings.py            # 应用配置常量
│   └── config_loader.py       # 配置加载器
│
├── models/                     # Pydantic 数据模型
│   ├── __init__.py
│   ├── schema_models.py       # Schema Linker 相关模型
│   └── query_models.py        # SQL 查询相关模型
│
├── utils/                      # 工具函数
│   ├── __init__.py
│   ├── sql_validator.py       # SQL 安全验证
│   ├── sql_parser.py          # SQL 解析工具
│   └── logger.py              # 日志记录工具
│
├── services/                   # 业务逻辑服务层
│   ├── __init__.py
│   ├── schema_linker_service.py   # Schema Linker 服务
│   ├── sql_service.py             # SQL 相关服务
│   └── database_service.py        # 数据库服务
│
└── api/                        # API 路由层
    ├── __init__.py
    ├── health_routes.py       # 健康检查路由
    ├── query_routes.py        # 查询相关路由
    └── schema_routes.py       # Schema 链接路由
```

## 模块说明

### 1. config/ - 配置管理
- **settings.py**: 存储所有配置常量（数据库路径、API配置、超时设置等）
- **config_loader.py**: 负责加载和管理数据库配置和模型配置

### 2. models/ - 数据模型
- **schema_models.py**: Schema Linker 的请求/响应模型
- **query_models.py**: SQL 查询的请求/响应模型

### 3. utils/ - 工具函数
- **sql_validator.py**: SQL 安全验证，确保只执行只读查询
- **sql_parser.py**: 从模型响应中提取 SQL 语句
- **logger.py**: 查询日志记录功能

### 4. services/ - 业务逻辑层
- **schema_linker_service.py**:
  - 百度 API 授权和向量化
  - Elasticsearch 搜索
  - Schema 链接核心逻辑
  - Jieba 分词初始化

- **sql_service.py**:
  - 调用大模型 API 生成 SQL
  - 执行 SQL 查询

- **database_service.py**:
  - 数据库表管理
  - 表结构查询

### 5. api/ - API 路由层
- **health_routes.py**: 健康检查和系统信息接口
- **query_routes.py**: SQL 查询相关的所有接口
- **schema_routes.py**: Schema 链接接口

### 6. app.py - 应用主入口
- 创建 FastAPI 应用实例
- 注册所有路由
- 应用启动时的初始化逻辑

## 启动方式

### 方式 1: 使用启动脚本
```bash
python run_server.py
```

### 方式 2: 直接运行 app.py
```bash
python -m src.app
```

### 方式 3: 使用 uvicorn
```bash
uvicorn src.app:app --host 0.0.0.0 --port 8080
```

## 配置文件要求

确保以下配置文件存在于项目根目录：
- `config.json` - 数据库配置
- `model_config.json` - 模型配置
- `infer.template` - Prompt 模板
- `funds_v3.db` - SQLite 数据库文件

## API 端点

### 健康检查
- `GET /` - 根路径
- `GET /health` - 健康检查

### 查询相关
- `GET /tables` - 获取所有表列表
- `GET /tables/{table_name}/schema` - 获取表结构
- `GET /models` - 获取可用模型列表
- `POST /query` - 执行自然语言查询
- `POST /execute_raw_sql` - 直接执行 SQL
- `GET /table_preview/{table_name}` - 预览表数据

### Schema 链接
- `POST /schema_link` - Schema 链接服务

## 重构优势

1. **模块化**: 代码按功能分离，易于维护和测试
2. **可扩展性**: 新功能可以轻松添加到相应模块
3. **可读性**: 清晰的目录结构和命名规范
4. **可测试性**: 每个模块可以独立测试
5. **配置管理**: 集中管理所有配置项
6. **关注点分离**: API 路由、业务逻辑、数据模型完全分离

## 注意事项

1. 原始的 `server_es.py` 文件已保留，可以作为参考或回退方案
2. 所有功能保持不变，只是代码组织方式改变
3. 确保所有依赖包已安装（fastapi, uvicorn, elasticsearch, httpx, jieba, qianfan 等）
