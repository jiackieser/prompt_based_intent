from typing import Dict, Any
import os
from risk_detect.keyword_extractor import KeywordExtractor
from risk_detect.emotion_analyzer import EmotionAnalyzer

class CustomerServiceJudge:
    def __init__(self, keyword_list):
        self.keyword_extractor = KeywordExtractor(keyword_list)
        self.emotion_analyzer = EmotionAnalyzer()
        self.price_keywords, self.manual_service_keywords = self._load_keywords()
    
    def _load_keywords(self):
        """从文件加载价格和人工服务关键词"""
        keywords_manual = []
        keywords_price = []
        try:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            keyword_path_manual = os.path.join(BASE_DIR, 'manual_service_keywords.txt')
            with open(keyword_path_manual, 'r', encoding='utf-8') as f:
                keywords_manual = [line.strip() for line in f if line.strip()]
            keyword_path_price = os.path.join(BASE_DIR, 'price_keywords.txt')
            with open(keyword_path_price, 'r', encoding='utf-8') as f:
                keywords_price = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print("警告：未找到keywords文件，使用默认关键词")
        return keywords_price, keywords_manual
    
    def _has_manual_service_request(self, user_query: str) -> bool:
        """检测用户是否主动要求转接人工服务"""
        user_query_lower = user_query.lower()
        for keyword in self.manual_service_keywords:
            if keyword in user_query_lower:
                return True
        return False
    
    def _has_price_related_query(self, user_query: str) -> bool:
        """检测用户是否询问价格或优惠相关内容"""
        user_query_lower = user_query.lower()
        for keyword in self.price_keywords:
            if keyword in user_query_lower:
                return True
        return False
    
    def judge_with_details(self, user_query: str, context: list = None) -> Dict[str, Any]:
        # 首先检查用户是否要求转接人工服务
        manual_service_requested = self._has_manual_service_request(user_query)
        
        # 检查用户是否询问价格或优惠相关内容
        price_related_query = self._has_price_related_query(user_query)
        
        if manual_service_requested or price_related_query:
            # 如果用户要求转接人工服务或询问价格，直接返回True
            request_type = '人工服务请求' if manual_service_requested else '价格优惠询问'
            return {
                'final_result': True,
                'keyword_match': True,
                'matched_keywords': [request_type],
                'emotion_match': True,
                'manual_service_requested': manual_service_requested,
                'price_related_query': price_related_query,
            }
        
        matched_keywords = self.keyword_extractor.get_matched_keywords(user_query)
        keyword_match = len(matched_keywords) > 0
        
        emotion_result = self.emotion_analyzer.analyze_emotion_with_details(user_query, context)
        emotion_match = emotion_result['is_complaint']

        """综合判断最终结果，只有当关键词匹配且情感分析结果为投诉时才为True"""
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
            'price_related_query': False,
        }
