import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from judge import CustomerServiceJudge
import uvicorn

app = FastAPI(
    title="智能客服风险检测API",
    description="基于关键词匹配和情感分析的用户查询风险检测服务",
    version="1.0.0"
)

# 获取当前文件所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 加载关键词并初始化判断器
keyword_list = []
try:
    keyword_path = os.path.join(BASE_DIR, 'keywords.txt')
    with open(keyword_path, 'r', encoding='utf-8') as f:
        keyword_list = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print("警告：未找到keywords.txt文件，使用空关键词列表")

judge = CustomerServiceJudge(keyword_list)


class QueryRequest(BaseModel):
    """用户查询请求模型"""
    query: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "你们的产品质量太差了，我要投诉"
            }
        }


class RiskResponse(BaseModel):
    """风险检测响应模型"""
    is_risk: bool
    query: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_risk": True,
                "query": "你们的产品质量太差了，我要投诉"
            }
        }


@app.post(
    "/risk_detect",
    response_model=RiskResponse,
    summary="检测用户查询是否存在风险",
    description="接收用户查询，返回是否存在风险（购买意愿下降或投诉情绪）"
)
async def detect_risk(request: QueryRequest):
    """
    检测用户查询是否存在风险
    
    - **query**: 用户输入的查询文本
    
    返回:
    - **is_risk**: 是否存在风险 (true/false)
    - **query**: 原始用户查询
    """
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="查询内容不能为空")
    
    try:
        result = judge.judge_with_details(request.query)
        
        return RiskResponse(
            is_risk=result['final_result'],
            query=request.query
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")


@app.get(
    "/health",
    summary="健康检查",
    description="检查API服务是否正常运行"
)
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "risk-detection-api"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
