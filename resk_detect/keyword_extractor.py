import jieba
from typing import List, Set

class KeywordExtractor:
    def __init__(self, keyword_list: List[str]):
        self.keyword_set = set(keyword_list)
        
    def extract_keywords(self, text: str) -> List[str]:
        words = jieba.lcut(text)
        return [word for word in words if word.strip()]
    
    def get_matched_keywords(self, text: str) -> List[str]:
        extracted_keywords = self.extract_keywords(text)
        matched = [kw for kw in extracted_keywords if kw in self.keyword_set]
        return matched
