import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json

# ========== 配置 ==========
API_BASE_URL = "http://127.0.0.1:8080"
CHAT_AVATAR_USER = "🧑‍💼"
CHAT_AVATAR_AI = "🤖"

# ========== 页面配置 ==========
st.set_page_config(
    page_title="NL2SQL Tool",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== 样式CSS ==========
st.markdown("""
<style>
    /* 🚫 完全隐藏收起/展开按钮 */
    [data-testid="collapsedControl"], 
    [data-testid="collapsedControl"] * {
        display: none !important;
        visibility: hidden !important;
    }

    /* 🚫 禁止侧边栏折叠 */
    section[data-testid="stSidebar"][aria-expanded="false"] {
        transform: none !important;
        visibility: visible !important;
        width: 260px !important;
    }

    /* ✅ 确保侧边栏宽度固定 */
    [data-testid="stSidebar"] {
        display: block !important;
        width: 260px !important;
        min-width: 260px !important;
    }

    /* 页面顶部空白微调 */
    .main .block-container {
        padding-top: 1rem;
        max-width: 100%;
    }

    header[data-testid="stHeader"] {
        display: none;
    }

    /* --- 标题样式优化 --- */
    .custom-title {
        font-size: 1.5rem !important; /* 调小字体 */
        font-weight: 700;
        margin-bottom: 1rem !important;
        color: #1e3c72;
    }

    /* --- 侧边栏紧凑状态盒 --- */
    .sidebar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    .status-box {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 6px;
        padding: 0.4rem 0.6rem;
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
        font-size: 0.85rem;
        color: #166534;
    }

    .error-box {
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 6px;
        padding: 0.4rem 0.6rem;
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
        font-size: 0.85rem;
        color: #991b1b;
    }

    /* 聊天气泡 */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .sql-box {
        background: #f8f9fa;
        border-left: 5px solid #007bff;
        border-radius: 8px;
        padding: 1rem;
        font-family: 'Courier New', monospace;
        margin: 1rem 0;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

# ========== 辅助函数 ==========
@st.cache_data(ttl=10)
def fetch_tables():
    try:
        response = requests.get(f"{API_BASE_URL}/tables")
        return response.json() if response.status_code == 200 else None
    except: return None

@st.cache_data(ttl=10)
def fetch_models():
    try:
        response = requests.get(f"{API_BASE_URL}/models")
        return response.json() if response.status_code == 200 else None
    except: return None

def check_api_health():
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        return response.json() if response.status_code == 200 else None
    except: return None

def query_api(query, table_names=None, table_name=None, model_name=None):
    try:
        payload = {"query": query}
        if table_names: payload["table_names"] = table_names
        elif table_name: payload["table_name"] = table_name
        if model_name: payload["model_name"] = model_name
        return requests.post(f"{API_BASE_URL}/query", json=payload).json()
    except Exception as e: return {"success": False, "error": str(e)}

def execute_raw_sql(sql):
    try:
        return requests.post(f"{API_BASE_URL}/execute_raw_sql", json={"sql": sql}).json()
    except Exception as e: return {"success": False, "error": str(e)}

def fetch_table_preview(table_name):
    try:
        return requests.get(f"{API_BASE_URL}/table_preview/{table_name}").json()
    except Exception as e: return {"success": False, "error": str(e)}

def fetch_table_schema(table_name):
    try:
        return requests.get(f"{API_BASE_URL}/tables/{table_name}/schema").json()
    except: return None

# ========== 初始化状态 ==========
if "messages" not in st.session_state: st.session_state.messages = []
if "multi_table_mode" not in st.session_state: st.session_state.multi_table_mode = False

# ========== 侧边栏 ==========
with st.sidebar:
    st.markdown('<div class="sidebar-header"><h2>⚙️ 控制台</h2></div>', unsafe_allow_html=True)
    
    # 导航
    page = st.radio("功能模块:", ["💬 智能对话", "⌨️ SQL 运行器", "📂 数据库浏览"])
    
    # 紧凑状态栏 (去掉了多余分割线和边距)
    health = check_api_health()
    if health:
        st.markdown(f"""<div class="status-box"><strong>✅ 系统在线</strong><br>表: {health.get('tables_loaded', 0)} | 模型: {health.get('models_loaded', 0)}</div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="error-box"><strong>❌ API 离线</strong></div>', unsafe_allow_html=True)

    st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)

    if page == "💬 智能对话":
        st.markdown("### 📊 数据表")
        multi_mode = st.checkbox("多表模式", value=st.session_state.multi_table_mode)
        st.session_state.multi_table_mode = multi_mode
        
        tables_data = fetch_tables()
        if tables_data and tables_data.get("success"):
            table_options = tables_data["tables"]
            if multi_mode:
                st.session_state.selected_tables = st.multiselect("选择关联表:", table_options, key="multi_select")
            else:
                st.session_state.selected_table = st.selectbox("选择目标表:", table_options, key="single_select")
        
        st.markdown("### 🧠 AI 模型")
        models_data = fetch_models()
        if models_data and models_data.get("success"):
            st.session_state.selected_model = st.selectbox("选择模型:", list(models_data["models"].keys()))
        
        if st.button("🗑️ 清空历史", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

# ========== 主界面逻辑 ==========

if page == "💬 智能对话":
    st.markdown('<div class="custom-title">💬 自然语言 SQL 查询</div>', unsafe_allow_html=True)
    
    col_chat, col_status = st.columns([3, 1])
    
    with col_chat:
        # 显示历史 (最近一轮)
        for message in st.session_state.messages[-2:]:
            if message["role"] == "user":
                st.markdown(f'<div class="user-message"><strong>{CHAT_AVATAR_USER} 用户:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
            else:
                if "sql" in message:
                    st.markdown(f'<div class="sql-box"><strong>🔍 生成 SQL:</strong><br><code>{message["sql"]}</code></div>', unsafe_allow_html=True)
                if "data" in message and message["data"]:
                    st.dataframe(pd.DataFrame(message["data"]), use_container_width=True)
                if "error" in message:
                    st.error(message["error"])

        # 表单处理
        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_area("请输入问题:", placeholder="例如：查询最近三天的订单", height=100)
            c1, c2 = st.columns([1, 1])
            submit_clicked = c1.form_submit_button("🚀 提交查询", use_container_width=True)
            example_clicked = c2.form_submit_button("💡 示例查询", use_container_width=True)

        # 逻辑：如果点击“示例”，直接修改 user_input 并执行
        final_query = None
        if example_clicked:
            final_query = "查询表内的前5条数据"
        elif submit_clicked and user_input:
            final_query = user_input

        if final_query:
            # 校验选择
            if st.session_state.multi_table_mode and not st.session_state.get("selected_tables"):
                st.error("请选择至少一个数据表")
            elif not st.session_state.multi_table_mode and not st.session_state.get("selected_table"):
                st.error("请选择一个数据表")
            else:
                st.session_state.messages = [{"role": "user", "content": final_query}]
                with st.spinner("AI 正在思考..."):
                    if st.session_state.multi_table_mode:
                        res = query_api(final_query, table_names=st.session_state.selected_tables, model_name=st.session_state.get("selected_model"))
                    else:
                        res = query_api(final_query, table_name=st.session_state.selected_table, model_name=st.session_state.get("selected_model"))
                    
                    if res.get("success"):
                        st.session_state.messages.append({"role": "assistant", "sql": res.get("sql"), "data": res.get("data")})
                    else:
                        st.session_state.messages.append({"role": "assistant", "error": res.get("error")})
                st.rerun()

    with col_status:
        st.subheader("🛠️ 配置预览")
        if st.session_state.multi_table_mode:
            st.write(f"**关联表:** `{', '.join(st.session_state.get('selected_tables', []))}`")
        else:
            st.write(f"**当前表:** `{st.session_state.get('selected_table')}`")
        st.write(f"**当前模型:** `{st.session_state.get('selected_model')}`")

elif page == "⌨️ SQL 运行器":
    st.markdown('<div class="custom-title">⌨️ SQL Playground</div>', unsafe_allow_html=True)
    sql_text = st.text_area("输入原生 SQL:", placeholder="SELECT * FROM table LIMIT 10;", height=200)
    if st.button("▶️ 立即运行", type="primary"):
        if sql_text:
            with st.spinner("执行中..."):
                res = execute_raw_sql(sql_text)
                if res.get("success"):
                    st.success(f"执行成功 (行数: {res.get('total_rows')})")
                    if res.get("data"): st.dataframe(pd.DataFrame(res["data"]), use_container_width=True)
                else:
                    st.error(f"SQL 报错: {res.get('error')}")

elif page == "📂 数据库浏览":
    st.markdown('<div class="custom-title">📂 Database Explorer</div>', unsafe_allow_html=True)
    tables_res = fetch_tables()
    if tables_res and tables_res.get("success"):
        target = st.selectbox("选择表:", tables_res["tables"])
        if target:
            t1, t2 = st.tabs(["🏗️ 结构", "📊 预览"])
            with t1:
                schema = fetch_table_schema(target)
                if schema: st.code(schema.get("build_statement"), language="sql")
            with t2:
                preview = fetch_table_preview(target)
                if preview.get("success"): st.dataframe(pd.DataFrame(preview.get("data", [])), use_container_width=True)

st.markdown("<br><hr><div style='text-align: center; color: #999; font-size: 0.8rem;'>NL2SQL Management v1.2</div>", unsafe_allow_html=True)
# import streamlit as st
# import requests
# import pandas as pd
# from datetime import datetime
# import json

# # 可选的绘图库导入
# try:
#     import plotly.express as px
#     import plotly.graph_objects as go
#     PLOTLY_AVAILABLE = True
# except ImportError:
#     PLOTLY_AVAILABLE = False
#     st.warning("📊 Plotly not installed. Charts will be disabled. Install with: pip install plotly")

# # ========== 配置 ==========
# API_BASE_URL = "http://127.0.0.1:8080"
# CHAT_AVATAR_USER = "🧑‍💼"
# CHAT_AVATAR_AI = "🤖"

# # ========== 页面配置 ==========
# st.set_page_config(
#     page_title="NL2SQL",
#     page_icon="💬",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # ========== 样式CSS ==========
# st.markdown("""
# <style>
#     /* 🚫 完全隐藏收起/展开按钮，无论鼠标是否悬停 */
#     [data-testid="collapsedControl"], 
#     [data-testid="collapsedControl"] * {
#         display: none !important;
#         visibility: hidden !important;
#         opacity: 0 !important;
#         pointer-events: none !important;
#     }

#     /* 🚫 禁止侧边栏折叠，始终保持展开 */
#     section[data-testid="stSidebar"][aria-expanded="false"] {
#         transform: none !important;
#         visibility: visible !important;
#         opacity: 1 !important;
#         width: 260px !important;
#         min-width: 260px !important;
#     }

#     /* ✅ 确保侧边栏始终显示 */
#     [data-testid="stSidebar"] {
#         display: block !important;
#         visibility: visible !important;
#         opacity: 1 !important;
#         width: 260px !important;
#         min-width: 260px !important;
#         transform: none !important;
#         transition: none !important;
#         position: relative !important;
#         left: 0 !important;
#     }

#     /* 减少页面顶部空白 */
#     .main .block-container {
#         padding-top: 0.2rem;
#         max-width: 100%;
#     }

#     /* 隐藏Streamlit默认的header */
#     header[data-testid="stHeader"] {
#         height: 0px;
#         display: none;
#     }

#     /* 去除Streamlit默认的第一个元素上边距 */
#     .main .block-container > div:first-child {
#         margin-top: 0 !important;
#         padding-top: 0 !important;
#     }

#     /* 去除columns容器的上边距 */
#     .stColumns {
#         margin-top: 0 !important;
#     }

#     /* 减小标题间距 */
#     h3 {
#         margin-top: 0.3rem !important;
#         margin-bottom: 0.1rem !important;
#     }

#     /* 减小侧边栏组件间距 */
#     .stSelectbox {
#         margin-top: 0.1rem !important;
#     }

#     .stSelectbox > div > div {
#         margin-bottom: 0.2rem;
#     }

#     /* 完全隐藏selectbox的标签 */
#     .stSelectbox > label {
#         display: none !important;
#     }

#     /* 减小selectbox和后续元素间距 */
#     .stSelectbox + div {
#         margin-top: 0.1rem !important;
#     }

#     .main-header {
#         background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
#         padding: 1rem;
#         border-radius: 10px;
#         color: white;
#         text-align: center;
#         margin-bottom: 2rem;
#         box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
#     }

#     .chat-container {
#         background: #f8f9fa;
#         border-radius: 15px;
#         padding: 1rem;
#         margin: 1rem 0;
#         border-left: 4px solid #007bff;
#     }

#     .user-message {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         color: white;
#         padding: 1rem;
#         border-radius: 15px 15px 5px 15px;
#         margin: 0.5rem 0;
#         box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
#     }

#     .ai-message {
#         background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
#         color: white;
#         padding: 1rem;
#         border-radius: 15px 15px 15px 5px;
#         margin: 0.5rem 0;
#         box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
#     }

#     .sidebar-header {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         color: white;
#         padding: 0.5rem;
#         border-radius: 8px;
#         text-align: center;
#         margin-bottom: 0.5rem;
#     }

#     .status-box {
#         background: #e8f5e8;
#         border: 1px solid #28a745;
#         border-radius: 6px;
#         padding: 0.5rem;
#         margin: 0.3rem 0;
#         font-size: 0.9rem;
#     }

#     .error-box {
#         background: #f8d7da;
#         border: 1px solid #dc3545;
#         border-radius: 6px;
#         padding: 0.5rem;
#         margin: 0.3rem 0;
#         color: #721c24;
#         font-size: 0.9rem;
#     }

#     .sql-box {
#         background: #f8f9fa;
#         border: 1px solid #6c757d;
#         border-radius: 8px;
#         padding: 1rem;
#         font-family: 'Courier New', monospace;
#         margin: 1rem 0;
#     }

#     .metric-card {
#         background: white;
#         padding: 1rem;
#         border-radius: 10px;
#         box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
#         text-align: center;
#         margin: 0.5rem 0;
#     }
# </style>
# """, unsafe_allow_html=True)

# # ========== 辅助函数 ==========
# @st.cache_data(ttl=60)
# def fetch_tables():
#     try:
#         response = requests.get(f"{API_BASE_URL}/tables")
#         if response.status_code == 200:
#             return response.json()
#         return None
#     except:
#         return None

# @st.cache_data(ttl=60)
# def fetch_models():
#     try:
#         response = requests.get(f"{API_BASE_URL}/models")
#         if response.status_code == 200:
#             return response.json()
#         return None
#     except:
#         return None

# def query_api(query, table_names=None, table_name=None, model_name=None):
#     try:
#         payload = {
#             "query": query
#         }
#         # 支持多表模式和单表模式
#         if table_names:
#             payload["table_names"] = table_names
#         elif table_name:
#             payload["table_name"] = table_name

#         if model_name:
#             payload["model_name"] = model_name
#         response = requests.post(f"{API_BASE_URL}/query", json=payload)
#         return response.json()
#     except Exception as e:
#         return {"success": False, "error": str(e)}

# def check_api_health():
#     try:
#         response = requests.get(f"{API_BASE_URL}/health")
#         if response.status_code == 200:
#             return response.json()
#         return None
#     except:
#         return None

# # ========== 初始化会话状态 ==========
# if "messages" not in st.session_state:
#     st.session_state.messages = []
# if "selected_table" not in st.session_state:
#     st.session_state.selected_table = None
# if "selected_tables" not in st.session_state:
#     st.session_state.selected_tables = []
# if "selected_model" not in st.session_state:
#     st.session_state.selected_model = None
# if "multi_table_mode" not in st.session_state:
#     st.session_state.multi_table_mode = False

# # ========== 侧边栏 ==========
# with st.sidebar:
#     st.markdown("""
#     <div class="sidebar-header">
#         <h2>⚙️ Settings</h2>
#     </div>
#     """, unsafe_allow_html=True)
    
#     health = check_api_health()
#     if health:
#         st.markdown(f"""
#         <div class="status-box">
#             <strong>✅ API Status: Healthy</strong><br>
#             Tables: {health.get('tables_loaded', 0)}<br>
#             Models: {health.get('models_loaded', 0)}<br>
#             Default: {health.get('default_model', 'N/A')}
#         </div>
#         """, unsafe_allow_html=True)
#     else:
#         st.markdown("""
#         <div class="error-box">
#             <strong>❌ API Status: Offline</strong><br>
#             Please check your API server
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("<hr style='margin: 0.2rem 0; border: 0.5px solid #ddd;'>", unsafe_allow_html=True)

#     # 表选择模式切换
#     st.markdown("### 📊 Select Tables")
#     multi_table_mode = st.checkbox("启用多表查询模式", value=st.session_state.multi_table_mode)
#     st.session_state.multi_table_mode = multi_table_mode

#     tables_data = fetch_tables()
#     if tables_data and tables_data.get("success"):
#         table_options = tables_data["tables"]

#         if multi_table_mode:
#             # 多表选择模式
#             selected_tables = st.multiselect(
#                 "选择多个数据表",
#                 options=table_options,
#                 default=st.session_state.selected_tables if st.session_state.selected_tables else [],
#                 key="table_multiselect"
#             )
#             st.session_state.selected_tables = selected_tables
#             st.session_state.selected_table = None  # 清除单表选择
#             if selected_tables:
#                 st.success(f"📋 选择的表: {', '.join(selected_tables)}")
#         else:
#             # 单表选择模式
#             selected_table = st.selectbox(
#                 "选择数据表",
#                 options=table_options,
#                 index=0 if table_options else None,
#                 key="table_selector"
#             )
#             st.session_state.selected_table = selected_table
#             st.session_state.selected_tables = []  # 清除多表选择
#             if selected_table:
#                 st.success(f"📋 Active Table: **{selected_table}**")
#     else:
#         st.error("Failed to load tables")
    
#     st.markdown("<hr style='margin: 0.2rem 0; border: 0.5px solid #ddd;'>", unsafe_allow_html=True)
    
#     st.markdown("### 🧠 Select AI Model")
#     models_data = fetch_models()
#     if models_data and models_data.get("success"):
#         model_options = list(models_data["models"].keys())
#         default_model = models_data.get("default_model")
#         default_index = 0
#         if default_model and default_model in model_options:
#             default_index = model_options.index(default_model)
#         selected_model = st.selectbox(
#             "选择AI模型",
#             options=model_options,
#             index=default_index,
#             key="model_selector",
#             label_visibility="collapsed"
#         )
#         st.session_state.selected_model = selected_model
#         if selected_model:
#             st.success(f"🤖 {selected_model}")
#     else:
#         st.error("Failed to load models")
    
#     st.markdown("<hr style='margin: 0.2rem 0; border: 0.5px solid #ddd;'>", unsafe_allow_html=True)
    
#     if st.button("🗑️ Clear Chat", use_container_width=True):
#         st.session_state.messages = []
#         st.rerun()

# # ========== 主聊天区域 ==========
# col1, col2 = st.columns([3, 1])

# with col1:
#     st.markdown("<h1 style='margin-top: 0; margin-bottom: 0.5rem; padding: 0;'>NL2SQL</h1>", unsafe_allow_html=True)
    
#     if st.session_state.messages:
#         last_messages = st.session_state.messages[-2:] if len(st.session_state.messages) >= 2 else st.session_state.messages
#         for message in last_messages:
#             if message["role"] == "user":
#                 st.markdown(f"""
#                 <div class="user-message">
#                     <strong>{CHAT_AVATAR_USER} 查询:</strong><br>
#                     {message["content"]}
#                 </div>
#                 """, unsafe_allow_html=True)
#             else:
#                 if "sql" in message:
#                     st.markdown(f"""
#                     <div class="sql-box">
#                         <strong>🔍 生成的SQL:</strong><br>
#                         <code>{message["sql"]}</code>
#                     </div>
#                     """, unsafe_allow_html=True)
#                 if "data" in message and message["data"]:
#                     st.markdown("📈 **查询结果:**")
#                     df = pd.DataFrame(message["data"])
#                     st.dataframe(df, use_container_width=True)

#     with st.form(key="chat_form", clear_on_submit=True):
#         user_input = st.text_area(
#             "请输入您的查询问题:",
#             placeholder="例如: 显示前10条记录, 计算平均值等",
#             height=100
#         )
#         col_submit, col_example = st.columns([1, 1])
#         with col_submit:
#             submit_button = st.form_submit_button("🚀 发送查询", use_container_width=True)
#         with col_example:
#             if st.form_submit_button("💡 示例查询", use_container_width=True):
#                 user_input = "查询表内的前5条数据"
#                 submit_button = True

#     if submit_button and user_input:
#         # 验证表选择
#         if st.session_state.multi_table_mode:
#             if not st.session_state.selected_tables:
#                 st.error("请先选择至少一个数据表!")
#                 st.stop()
#         else:
#             if not st.session_state.selected_table:
#                 st.error("请先选择一个数据表!")
#                 st.stop()

#         st.session_state.messages = []
#         st.session_state.messages.append({
#             "role": "user",
#             "content": user_input
#         })
#         with st.spinner("🤔 AI正在思考..."):
#             if st.session_state.multi_table_mode:
#                 # 多表查询
#                 result = query_api(
#                     user_input,
#                     table_names=st.session_state.selected_tables,
#                     model_name=st.session_state.selected_model
#                 )
#             else:
#                 # 单表查询
#                 result = query_api(
#                     user_input,
#                     table_name=st.session_state.selected_table,
#                     model_name=st.session_state.selected_model
#                 )

#             if result.get("success"):
#                 ai_message = {
#                     "role": "assistant",
#                     "content": ""
#                 }
#                 if result.get("sql"):
#                     ai_message["sql"] = result["sql"]
#                 if result.get("data"):
#                     ai_message["data"] = result["data"]
#                 st.session_state.messages.append(ai_message)
#             else:
#                 error_msg = f"查询出错: {result.get('error', '未知错误')}"
#                 st.session_state.messages.append({
#                     "role": "assistant",
#                     "content": error_msg
#                 })
#         st.rerun()

# with col2:
#     st.subheader("⚙️ 当前配置")
#     if st.session_state.multi_table_mode and st.session_state.selected_tables:
#         st.markdown(f"**📊 数据表:** `{', '.join(st.session_state.selected_tables)}`")
#     elif not st.session_state.multi_table_mode and st.session_state.selected_table:
#         st.markdown(f"**📊 数据表:** `{st.session_state.selected_table}`")
#     if st.session_state.selected_model:
#         st.markdown(f"**🧠 模型:** `{st.session_state.selected_model}`")

# st.markdown("---")
# st.markdown("""
# <div style="text-align: center; color: #6c757d; padding: 1rem;">
#     Powered by Streamlit & FastAPI
# </div>
# """, unsafe_allow_html=True)
