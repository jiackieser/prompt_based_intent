"""
FastAPI 接口服务
提供查询改写功能
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn

from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware

from prompt_templates import SYSTEM_PROMPT, build_user_prompt
from risk_detect.api import RiskResponse, QueryRequest, judge, send_wechat_group_notification

# 初始化 FastAPI 应用
app = FastAPI(
    title="查询改写 API",
    description="提供基于 Qwen 模型的对话查询改写服务",
    version="1.0.0"
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# 配置本地模型
BASE_URL = "https://vllm-qwen3.vertu.cn/v1"
MODEL_NAME = "vemory_1_2w_pt"
client = OpenAI(api_key="EMPTY", base_url=BASE_URL)


# ========== 数据模型定义 ==========

class ParamPair(BaseModel):
    """对话对"""
    question: str = Field(..., description="用户问题")
    answer: str = Field(..., description="系统回答")

class ContextInfo(BaseModel):
    """上下文信息"""
    window_size: int = Field(1, description="对话窗口大小")
    timestamp: Optional[str] = Field(None, description="时间戳")


class QueryRewriteRequest(BaseModel):
    """查询改写请求"""
    param_pairs: list[ParamPair] = Field(..., description="对话历史")
    query: str = Field(..., description="用户当前查询")
    context: Optional[ContextInfo] = Field(None, description="上下文信息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "param_pairs": [
                    {
                        "question": "给我介绍一下SIGNATURE眼镜蛇手机",
                        "answer": "SIGNATURE眼镜蛇手机是VERTU与宝诗龙联合推出的豪华收藏品"
                    }
                ],
                "query": "这个手机多少钱",
                "context": {
                    "window_size": 1,
                    "timestamp": "2026-01-22T15:35:20.123456"
                }
            }
        }


class QueryRewriteResponse(BaseModel):
    """查询改写响应"""
    original_query: str = Field(..., description="原始查询")
    rewritten_query: str = Field(..., description="改写后的查询")
    success: bool = Field(True, description="是否成功")
    timestamp: Optional[str] = Field(None, description="处理时间戳")


# ========== API 接口 ==========

@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "message": "查询改写 API 服务",
        "version": "1.0.0",
        "endpoints": {
            "查询改写": "/api/rewrite",
            "批量改写": "/api/batch-rewrite",
            "健康检查": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "model": MODEL_NAME}


@app.post("/api/rewrite", response_model=QueryRewriteResponse)
async def rewrite_query(request: QueryRewriteRequest):
    """
    查询改写接口
    
    根据对话历史，将用户的当前查询改写为独立、完整的搜索查询
    """
    try:
        # param_pairs 可以为空，表示没有历史对话
        
        # 获取窗口大小，默认为1
        window_size = 1
        if request.context and request.context.window_size:
            window_size = request.context.window_size
        
        # 根据窗口大小获取历史对话
        recent_pairs = request.param_pairs
        
        # 当前查询从 request.query 获取
        current_question = request.query

        # 获取历史对话（param_pairs 全部是历史对话）
        if len(recent_pairs) >= 1:
            # 取最近 window_size 轮历史
            history_qas = recent_pairs[-window_size:]
        else:
            # 没有历史
            history_qas = []
        # 构建提示词
        prompt = build_user_prompt(history_qas, current_question)
        
        # 调用模型
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        
        rewritten_query = completion.choices[0].message.content.strip()
        
        return QueryRewriteResponse(
            original_query=current_question,
            rewritten_query=rewritten_query,
            success=True,
            timestamp=request.context.timestamp if request.context else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模型调用失败: {str(e)}")


@app.post("/api/batch-rewrite")
async def batch_rewrite(requests: list[QueryRewriteRequest]):
    """
    批量查询改写接口
    
    一次处理多个查询改写请求
    """
    results = []
    for req in requests:
        try:
            if not req.param_pairs:
                results.append({
                    "original_query": "",
                    "rewritten_query": "",
                    "success": False,
                    "error": "param_pairs 不能为空"
                })
                continue
            
            # 获取窗口大小
            window_size = 1
            if req.context and req.context.window_size:
                window_size = req.context.window_size
            
            # 获取所有对话对
            recent_pairs = req.param_pairs
            
            # 提取历史信息和当前问题
            if len(recent_pairs) == 0:
                results.append({
                    "original_query": "",
                    "rewritten_query": "",
                    "success": False,
                    "error": "至少需要一轮对话"
                })
                continue
            
            # 最后一轮是当前问题
            current_question = recent_pairs[-1].question
            
            # 获取历史对话（排除最后一轮当前查询）
            if len(recent_pairs) > 1:
                # 取最近 window_size 轮历史
                history_qas = recent_pairs[:-1][-window_size:]
            else:
                # 只有一轮对话，没有历史
                history_qas = []
            
            prompt = build_user_prompt(history_qas, current_question)
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
            )
            
            results.append({
                "original_query": current_question,
                "rewritten_query": completion.choices[0].message.content.strip(),
                "success": True
            })
        except Exception as e:
            results.append({
                "original_query": req.param_pairs[-1].question if req.param_pairs else "",
                "rewritten_query": "",
                "success": False,
                "error": str(e)
            })
    
    return {"results": results, "total": len(results)}


@app.get("/api/risk_detect")
async def risk_detect():
    """风险预测接口"""

    return {"status": "healthy", "model": MODEL_NAME}


@app.post(
    "/api/risk_detect",
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

        if result['final_result']:
            notification_content = f"检测到需要转人工服务：\n用户问题：{request.query}"
            if result['manual_service_requested']:
                notification_content = f"用户主动要求转人工：\n用户问题：{request.query}"
            elif result['price_related_query']:
                notification_content = f"用户询问价格优惠：\n用户问题：{request.query}"
            elif result['matched_keywords']:
                notification_content = f"检测到投诉风险：\n用户问题：{request.query}\n匹配关键词：{result['matched_keywords']}"
            
            await send_wechat_group_notification(notification_content)

        return RiskResponse(
            is_risk=result['final_result'],
            query=request.query
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")

# ========== 启动服务 ==========

if __name__ == "__main__":
    # 启动服务器
    # 访问 http://localhost:8000/docs 查看自动生成的API文档
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式，代码修改后自动重启
        log_level="info"
    )
