import os
import base64
from typing import Optional

import requests

# 读取全局环境变量
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OWNER = os.getenv("GITHUB_OWNER")
REPO = os.getenv("GITHUB_REPO")
BRANCH = os.getenv("GITHUB_BRANCH", "main")

API_BASE = f"https://api.github.com/repos/{OWNER}/{REPO}"


def get_file_sha(file_path: str) -> Optional[str]:
    """
    获取仓库文件SHA标识
    :param file_path: 仓库内文件路径
    :return: 文件sha，文件不存在返回None
    """
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = f"{API_BASE}/contents/{file_path}"
    params = {"ref": BRANCH}
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code == 200:
        return resp.json()["sha"]
    return None


def update_file(file_path: str, content: str, commit_msg: str) -> tuple[dict, int]:
    """
    更新/新建GitHub仓库文件
    :param file_path: 文件路径
    :param content: 文件文本内容
    :param commit_msg: 提交说明
    :return: 响应数据, 状态码
    """
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    sha = get_file_sha(file_path)
    # 内容Base64编码
    b64_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    payload = {
        "message": commit_msg,
        "content": b64_content,
        "branch": BRANCH
    }
    if sha:
        payload["sha"] = sha

    url = f"{API_BASE}/contents/{file_path}"
    resp = requests.put(url, json=payload, headers=headers)
    return resp.json(), resp.status_code