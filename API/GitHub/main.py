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