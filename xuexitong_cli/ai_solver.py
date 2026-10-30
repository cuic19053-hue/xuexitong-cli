import json
import os
import requests

class AISolver:
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")
        self.base_url = (base_url or os.environ.get("DEEPSEEK_BASE_URL") or "https://api.deepseek.com/chat/completions").rstrip('/')
        if not self.base_url.endswith("/chat/completions"):
            self.base_url += "/chat/completions"
        self.model = model or os.environ.get("DEEPSEEK_MODEL") or "deepseek-flash"

    def solve_quiz(self, questions: list) -> list:
        """
        输入题目列表，调用 LLM 进行批处理推理答题。
        questions 格式：
        [
            {
                "id": 1,
                "type": "单选题",
                "question": "马克思主义的根本特征是...",
                "options": [{"letter": "A", "text": "..."}, {"letter": "B", "text": "..."}]
            }
        ]
        输出格式：
        [
            {"id": 1, "letters": ["A"]},
            {"id": 2, "letters": ["B", "D"]}
        ]
        """
        if not self.api_key:
            raise ValueError("未配置 API Key，请设置环境变量 DEEPSEEK_API_KEY 或在参数中指定")

        prompt = (
            "按题意回答全部题目。注意：题干或选项可能经过网页防复制处理，出现个别汉字被替换或乱码。"
            "先结合上下文在内部推断原意作答。每题都必须给非空答案，只用该题提供的选项字母且不可重复。"
            "单选和判断选一个，多选列出所有正确项。不确定时选最可能的答案。"
            '严格输出标准 JSON 格式：{"answers":[{"id":1,"letters":["A"]}]}，禁止输出多余解释或 Markdown 标签。'
        )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
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

        resp = requests.post(self.base_url, headers=headers, json=body, timeout=60)
        if not resp.ok:
            raise RuntimeError(f"大模型接口请求失败: HTTP {resp.status_code} - {resp.text}")

        res_data = resp.json()
        content = res_data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        
        parsed = json.loads(content)
        answers = parsed.get("answers", [])
        if not isinstance(answers, list) or len(answers) != len(questions):
            raise ValueError(f"大模型返回答案格式异常或数量不匹配: {content}")
        return answers
