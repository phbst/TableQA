#!/usr/bin/env python3
"""
Streamlit Chat Demo 启动脚本
开放端口供外部访问
"""

import subprocess
import sys
import os

def main():
    """启动Streamlit应用"""
    print("🚀 Starting SQL Chat Assistant...")
    print("🌐 Opening port for external access...")
    
    # Streamlit配置参数
    config_args = [
        "streamlit", "run", "streamlit_chat.py",
        "--server.port=8501",           # 端口
        "--server.address=0.0.0.0",     # 允许外部访问
        "--server.headless=true",       # 无头模式
        "--browser.gatherUsageStats=false",  # 禁用统计
        "--theme.base=light",           # 浅色主题
    ]
    
    try:
        # 检查streamlit_chat.py是否存在
        if not os.path.exists("streamlit_chat.py"):
            print("❌ Error: streamlit_chat.py not found!")
            print("Please make sure you're in the correct directory.")
            return 1
        
        print(f"📡 Server will be accessible at: http://0.0.0.0:8501")
        print(f"🌍 External access: http://<your-ip>:8501")
        print("🛑 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # 启动Streamlit
        result = subprocess.run(config_args, check=True)
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Streamlit: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())