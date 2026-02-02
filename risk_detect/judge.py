from typing import Dict, Any
import os
from risk_detect.keyword_extractor import KeywordExtractor
from risk_detect.emotion_analyzer import EmotionAnalyzer

class CustomerServiceJudge:
    def __init__(self, keyword_list):
        self.keyword_extractor = KeywordExtractor(keyword_list)
        self.emotion_analyzer = EmotionAnalyzer()
        self.manual_service_keywords = self._load_manual_service_keywords()
    
    def _load_manual_service_keywords(self):
        """从文件加载人工服务关键词"""
        keywords = []
        try:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            keyword_path = os.path.join(BASE_DIR, 'manual_service_keywords.txt')
            with open(keyword_path, 'r', encoding='utf-8') as f:
                keywords = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print("警告：未找到manual_service_keywords.txt文件，使用默认关键词")
        return keywords
    
    def _has_manual_service_request(self, user_query: str) -> bool:
        """检测用户是否主动要求转接人工服务"""
        user_query_lower = user_query.lower()
        for keyword in self.manual_service_keywords:
            if keyword in user_query_lower:
                return True
        return False
    
    def judge_with_details(self, user_query: str, context: list = None) -> Dict[str, Any]:
        # 首先检查用户是否要求转接人工服务
        manual_service_requested = self._has_manual_service_request(user_query)
        
        if manual_service_requested:
            # 如果用户要求转接人工服务，直接返回True
            return {
                'final_result': True,
                'keyword_match': True,
                'matched_keywords': ['人工服务请求'],
                'emotion_match': True,
                'manual_service_requested': True,
            }
        
        matched_keywords = self.keyword_extractor.get_matched_keywords(user_query)
        keyword_match = len(matched_keywords) > 0
        
        emotion_result = self.emotion_analyzer.analyze_emotion_with_details(user_query, context)
        emotion_match = emotion_result['is_complaint']

        final_result = keyword_match and emotion_match
        
        # 检查是否达到累计调用次数限制
        # is_total_limit_reached = emotion_result.get('is_total_limit_reached', False)
        
        # if is_total_limit_reached:
        #     # 如果达到累计调用次数限制，最终结果直接为True
        #     final_result = True
        # else:
        #     # 否则按照原有逻辑
        #     final_result = keyword_match and emotion_match
        
        # 如果最终结果为true，重置c_tolerance为2
        # if final_result:
        #     self.emotion_analyzer.c_tolerance = 2
        
        return {
            'final_result': final_result,
            'keyword_match': keyword_match,
            'matched_keywords': matched_keywords,
            'emotion_match': emotion_match,
            'manual_service_requested': False,
        }
