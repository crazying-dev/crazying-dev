from http.server import BaseHTTPRequestHandler
import json
# 导入自定义修改模块
from github_file import update_file
# 读取环境变量校验
import os
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OWNER = os.getenv("GITHUB_OWNER")
REPO = os.getenv("GITHUB_REPO")


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 环境校验
        if not all([GITHUB_TOKEN, OWNER, REPO]):
            self._send_json(500, {"error": "环境变量缺失"})
            return

        # 解析请求体
        try:
            content_len = int(self.headers.get("content-length", 0))
            post_body = self.rfile.read(content_len)
            body = json.loads(post_body)
        except Exception as e:
            self._send_json(400, {"error": "请求格式错误", "reason": str(e)})
            return

        # 提取参数
        file_path = body.get("filePath")
        file_content = body.get("content")
        commit_msg = body.get("commitMsg", "update file by module import")

        if not file_path or file_content is None:
            self._send_json(400, {"error": "缺少文件路径或内容参数"})
            return

        # 导入模块后调用修改方法
        res_data, status_code = update_file(file_path, file_content, commit_msg)
        self._send_json(status_code, res_data)

    def _send_json(self, code: int, data: dict):
        """统一返回JSON响应"""
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))