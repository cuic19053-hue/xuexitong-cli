import json
import os
import requests

class AISolver:
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        # 严格过滤 Key，剥离可能由于终端粘贴误带入的中文全角字符、不可见零宽字符与首尾空格
        raw_key = api_key or os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY") or ""
        self.api_key = raw_key.encode('ascii', 'ignore').decode('ascii').strip()
        
        raw_url = (base_url or os.environ.get("DEEPSEEK_BASE_URL") or "https://api.deepseek.com/chat/completions").rstrip('/')
        if not raw_url.endswith("/chat/completions"):
            raw_url += "/chat/completions"
        self.base_url = raw_url
        self.model = model or os.environ.get("DEEPSEEK_MODEL") or "deepseek-chat"

    def solve_quiz(self, questions: list) -> list:
        """
        输入题目列表，调用 LLM 进行批处理推理答题。
        自动处理 UTF-8 编码，彻底规避 requests 底层 http.client 的 latin-1 字符异常。
        """
        if not self.api_key:
            raise ValueError("未配置有效 API Key，请设置环境变量 DEEPSEEK_API_KEY 或在参数中指定")

        prompt = (
            "按题意回答全部题目。注意：题干或选项可能经过网页防复制处理，出现个别汉字被替换或乱码。"
            "先结合上下文在内部推断原意作答。每题都必须给非空答案，只用该题提供的选项字母且不可重复。"
            "单选和判断选一个，多选列出所有正确项。不确定时选最可能的答案。"
            '严格输出标准 JSON 格式：{"answers":[{"id":1,"letters":["A"]}]}，禁止输出多余解释或 Markdown 标签。'
        )

        # 确保 headers 中的所有键值均为纯正 ASCII 编码，防止中文标点污染 Header
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {self.api_key.strip()}"
        }
        
        body = {
            "model": self.model,
            "stream": False,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": json.dumps(questions, ensure_ascii=False)}
            ]
        }

        # 显式使用 UTF-8 字节流发送，彻底杜绝 latin-1 编码报错
        payload_bytes = json.dumps(body, ensure_ascii=False).encode('utf-8')

        resp = requests.post(self.base_url, headers=headers, data=payload_bytes, timeout=60)
        if not resp.ok:
            raise RuntimeError(f"大模型接口请求失败: HTTP {resp.status_code} - {resp.text}")

        res_data = resp.json()
        content = res_data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        
        parsed = json.loads(content)
        answers = parsed.get("answers", [])
        if not isinstance(answers, list) or len(answers) != len(questions):
            raise ValueError(f"大模型返回答案格式异常或数量不匹配: {content}")
        return answers
