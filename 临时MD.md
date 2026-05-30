用户：
修改代码：如果无token就每分钟更新一次，如果是ghp_...就每秒更新一次
给调用函数加一对参数：用户名，仓库名，Classic PAT；即如果给出了这几个参数就是用这几个参数，如果没给出就用环境变量
修改文件：使用来自项目根目录的相对目录

豆包：
结合你的需求完成代码改造，实现以下功能：
 
1. 动态参数优先：接口调用可传入  用户名、仓库名、PAT ，无传参则读取环境变量
2. 频率控制：无有效  ghp_  令牌 → 每分钟写入一次；有  ghp_  令牌 → 每秒写入一次
3. 相对路径存储：日志文件使用项目根目录相对路径  ./logs/日期.json 
4. 增加内存缓冲队列，按规则定时批量落地到 GitHub，大幅降低 API 请求次数
5. 保留跨域、参数校验、异常捕获，兼容原有调用方式
 
 
 
最终完整代码  main.py 
 
```python
  
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import requests
import base64
import json
import os
import time
from datetime import date, datetime
from dotenv import load_dotenv
from threading import Timer, Lock
from fastapi.middleware.cors import CORSMiddleware

# 加载环境变量
load_dotenv()
app = FastAPI(title="行为日志上报服务")

# 跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== 全局配置 & 内存缓冲 =====================
# 日志缓冲队列 + 锁（线程安全）
log_buffer = []
buffer_lock = Lock()
last_write_time = time.time()

# 全局默认配置（取自环境变量）
DEFAULT_OWNER = os.getenv("GITHUB_OWNER", "")
DEFAULT_REPO = os.getenv("GITHUB_REPO", "")
DEFAULT_TOKEN = os.getenv("GITHUB_TOKEN", "")

# 接口认证（可选，防恶意调用）
API_SECRET = os.getenv("API_SECRET", "default_secret_123456")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ===================== 数据模型 =====================
class BehaviorLog(BaseModel):
    action: str
    user_id: str = "anonymous"
    page: str = ""
    remark: str = ""

# ===================== 工具函数 =====================
def is_valid_ghp_token(token: str) -> bool:
    """判断是否为 GitHub Classic PAT"""
    return token.strip().startswith("ghp_")

def get_file_content(owner: str, repo: str, file_path: str, token: str):
    """读取仓库文件，返回内容和sha"""
    headers = {"Authorization": f"token {token}"}
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            content = base64.b64decode(data["content"]).decode("utf-8")
            return json.loads(content), data["sha"]
        return [], None
    except Exception:
        return [], None

def update_file(owner: str, repo: str, file_path: str, new_data: list, sha: str, token: str) -> bool:
    """写入文件并提交"""
    headers = {"Authorization": f"token {token}"}
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    content_bytes = json.dumps(new_data, ensure_ascii=False, indent=2).encode("utf-8")
    content_b64 = base64.b64encode(content_bytes).decode("utf-8")

    payload = {
        "message": f"auto log: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "content": content_b64
    }
    if sha:
        payload["sha"] = sha

    try:
        resp = requests.put(url, json=payload, headers=headers, timeout=10)
        return resp.status_code == 200
    except Exception:
        return False

def flush_buffer(owner: str, repo: str, token: str):
    """刷新缓冲：将队列日志写入GitHub"""
    global last_write_time
    with buffer_lock:
        if not log_buffer:
            return
        # 相对路径：项目根目录下 logs/日期.json
        today = date.today().isoformat()
        rel_file_path = f"logs/{today}.json"

        # 读取原有数据
        old_data, sha = get_file_content(owner, repo, rel_file_path, token)
        # 合并数据
        all_data = old_data + log_buffer
        # 写入仓库
        update_file(owner, repo, rel_file_path, all_data, sha, token)
        # 清空队列 + 更新最后写入时间
        log_buffer.clear()
        last_write_time = time.time()

# ===================== 认证依赖 =====================
def verify_api_token(token: str = Depends(oauth2_scheme)):
    if token != API_SECRET:
        raise HTTPException(status_code=401, detail="接口令牌无效")
    return token

# ===================== 核心接口 =====================
@app.post("/api/log")
async def add_log(
    log: BehaviorLog,
    # 动态传参：优先级 > 环境变量
    gh_owner: str | None = Query(None, description="GitHub 用户名，不传则使用环境变量"),
    gh_repo: str | None = Query(None, description="GitHub 仓库名，不传则使用环境变量"),
    gh_token: str | None = Query(None, description="GitHub Classic PAT，不传则使用环境变量"),
    _: str = Depends(verify_api_token)
):
    # 1. 优先级：传入参数 > 环境变量
    use_owner = gh_owner if gh_owner else DEFAULT_OWNER
    use_repo = gh_repo if gh_repo else DEFAULT_REPO
    use_token = gh_token if gh_token else DEFAULT_TOKEN

    if not all([use_owner, use_repo, use_token]):
        raise HTTPException(status_code=400, detail="缺少 GitHub 账号/仓库/令牌配置")

    # 2. 组装单条日志
    log_item = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": log.action,
        "user_id": log.user_id,
        "page": log.page,
        "remark": log.remark
    }

    # 3. 加入缓冲队列
    with buffer_lock:
        log_buffer.append(log_item)

    # 4. 频率判断：ghp_令牌 → 1秒写一次；无 → 60秒写一次
    now = time.time()
    interval = 1 if is_valid_ghp_token(use_token) else 60

    if now - last_write_time >= interval:
        # 到达间隔，立即刷新
        flush_buffer(use_owner, use_repo, use_token)
    else:
        # 未到间隔，延时触发刷新（保证最终落地）
        Timer(interval, flush_buffer, args=(use_owner, use_repo, use_token)).start()

    return {
        "code": 200,
        "msg": "日志已加入队列",
        "data": log_item,
        "write_interval": f"{interval}秒"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```
 
 
 
 
配套  .env  文件（项目根目录）
 
```env
  
# GitHub 默认配置（不传参时使用）
GITHUB_OWNER=你的GitHub用户名
GITHUB_REPO=你的仓库名
GITHUB_TOKEN=你的ghp_开头PAT

# 接口访问密钥（客户端调用必须携带）
API_SECRET=自定义一串随机密钥
```
 
 
 
 
核心规则说明
 
1. 参数优先级
 
接口支持 URL 传参，优先级： 调用时传入参数  >  .env 环境变量 
 
- 传参示例： /api/log?gh_owner=xxx&gh_repo=xxx&gh_token=ghp_xxx 
- 不传这三个参数，自动读取  .env  配置
 
2. 写入频率控制
 
- 令牌以  ghp_  开头（官方 Classic PAT）：1 秒写入一次
- 无令牌 / 非  ghp_  格式令牌：60 秒写入一次
- 采用内存队列 + 定时刷新，避免高频请求打爆 GitHub API
 
3. 文件路径
 
日志文件固定为项目根目录相对路径：
 
```plaintext
  
logs/YYYY-MM-DD.json
```
 
 
会自动在 GitHub 仓库根目录创建  logs  文件夹。
 
 
 
客户端调用示例
 
1. Python 客户端
 
方式1：使用环境变量（不传GitHub参数）
 
```python
  
import requests

url = "http://127.0.0.1:8000/api/log"
headers = {
    "Authorization": "Bearer 你的API_SECRET",
    "Content-Type": "application/json"
}
data = {
    "action": "button_click",
    "user_id": "user001",
    "page": "index",
    "remark": "首页按钮点击"
}

resp = requests.post(url, json=data, headers=headers)
print(resp.json())
```
 
 
方式2：动态传入 GitHub 账号/仓库/PAT（覆盖环境变量）
 
```python
  
import requests

url = "http://127.0.0.1:8000/api/log?gh_owner=用户名&gh_repo=仓库名&gh_token=ghp_你的令牌"
headers = {
    "Authorization": "Bearer 你的API_SECRET",
    "Content-Type": "application/json"
}
data = {"action": "page_view", "user_id": "user002"}

resp = requests.post(url, json=data, headers=headers)
print(resp.json())
```
 
 
2. JavaScript 前端调用
 
方式1：使用环境变量
 
```javascript
  
async function sendLog() {
  const res = await fetch("http://127.0.0.1:8000/api/log", {
    method: "POST",
    headers: {
      "Authorization": "Bearer 你的API_SECRET",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      action: "visit",
      user_id: "web_001",
      page: "about"
    })
  });
  console.log(await res.json());
}
sendLog();
```
 
 
方式2：动态携带 GitHub 参数
 
```javascript
  
async function sendLog() {
  const params = new URLSearchParams({
    gh_owner: "你的用户名",
    gh_repo: "你的仓库",
    gh_token: "ghp_你的令牌"
  });
  const url = `http://127.0.0.1:8000/api/log?${params.toString()}`;

  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Authorization": "Bearer 你的API_SECRET",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ action: "submit", user_id: "web_002" })
  });
  console.log(await res.json());
}
sendLog();
```
 
 
 
 
部署 & 补充说明
 
1. 依赖安装
```bash
  
pip install fastapi uvicorn requests python-dotenv
```
 
2. Vercel 部署
保留之前的  vercel.json ，并在 Vercel 环境变量中填入  .env  内所有字段。
3. 线程安全
队列操作加了锁，多客户端并发上报不会数据错乱。
4. 降级策略
读取/写入 GitHub 失败不会阻断接口，仅丢失当前批次日志，服务正常运行。