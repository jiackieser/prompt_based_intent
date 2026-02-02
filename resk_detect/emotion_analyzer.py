import requests
import json
from typing import Dict, Any
from config import Config

class EmotionAnalyzer:
    def __init__(self):
        Config.validate()
        self.api_key = Config.QWEN_API_KEY
        self.api_url = Config.QWEN_API_URL
        self.model = Config.QWEN_MODEL
        self.c_tolerance = 2
    
    def _call_qwen_api(self, prompt: str) -> Dict[str, Any]:
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.model,
            'input': {
                'messages': [
                    {
                        'role': 'system',
                        'content': Config.EMOTION_ANALYZER_SYSTEM_PROMPT
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            },
            'parameters': {
                'result_format': 'message'
            }
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API调用失败: {str(e)}")  
    
    def analyze_emotion_with_details(self, query: str, context: list = None) -> Dict[str, Any]:
        if self.c_tolerance == 0:
            self.c_tolerance = 2
            return {
                'is_complaint': True,
                'raw_response': 'true',
                'full_result': None,
                'is_total_limit_reached': True
            }
        
        # 构建提示词，包含上下文信息（如果有的话）
        if context and isinstance(context, list):
            # 如果context是对话列表，格式化为对话历史
            context_str = ""
            for i, turn in enumerate(context):
                if isinstance(turn, dict):
                    role = turn.get('role', 'unknown')
                    content = turn.get('content', '')
                    context_str += f"{role}: {content}\n"
            
            prompt = f"对话历史：\n{context_str}\n用户最新消息：{query}\n"

        else:
            # 无上下文的情况
            prompt = f"用户消息：{query}\n"
        
        try:
            result = self._call_qwen_api(prompt)
            
            if 'output' in result and 'choices' in result['output']:
                content = result['output']['choices'][0]['message']['content'].strip().lower()
                is_complaint = content == 'true'
                if is_complaint:
                    self.c_tolerance -= 1
                
                return {
                    'is_complaint': is_complaint,
                    'raw_response': content,
                    'full_result': result,
                    'is_total_limit_reached': False
                }

            else:
                raise Exception("API返回格式异常")
        except Exception as e:
            raise Exception(f"情感分析失败: {str(e)}")
