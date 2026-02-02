#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：prompt_based_intent
@File    ：control.py
@IDE     ：PyCharm
@Author  ：wgl
@Date    ：2026/1/29 17:38
'''
import json

from intent_recognization.prompt_template import SUB_QUESTIONS_SYSTEM_CONTENT
from main import intent_recognize


def sub_qustions_main(query, system_content) -> list:
    """根据用户的查询和系统内容，识别用户的意图。
    1, 判断问题复杂度
      - 简单问题, 直接返回
      - 复杂问题, 问题分解
    2, 返回当前query 拆解的子任务列表
    """
    model_output = intent_recognize(query, system_content)
    tasks = sub_qustions_post_handle(model_output, query)

    return tasks

def sub_qustions_post_handle(model_output: str, query: str) -> list:
    """对模型输出进行后处理，提取子任务列表
    Args:
        model_output: str，模型输出内容
        ```json
{
  "complexity": "简单",
  "original_intent": "查询今天天气信息",
  "solution_type": "直接回答",
  "subtasks": [],
  "explanation": "这是一个简单的信息查询问题，不需要分解"
}
```
```json
{
  "complexity": "复杂",
  "original_intent": "分析苹果收购小米对市场的影响",
  "solution_type": "任务分解",
  "subtasks": [
    {
      "id": "task_1",
      "description": "核实苹果是否真的收购了小米",
      "purpose": "确认问题前提的真实性，避免基于错误假设进行分析"
    },
    {
      "id": "task_2",
      "description": "如果收购属实，分析苹果的并购战略目标",
      "purpose": "理解收购背后的商业动机，如技术获取、市场扩张或供应链整合"
    },
    {
      "id": "task_3",
      "description": "评估小米在智能手机、IoT、电动汽车等领域的核心资产",
      "purpose": "识别被收购企业对苹果可能带来的价值点"
    },
    {
      "id": "task_4",
      "description": "分析对全球智能手机市场竞争格局的影响",
      "purpose": "判断收购是否会导致市场集中度提升或引发新竞争"
    },
    {
      "id": "task_5",
      "description": "评估对消费者、供应链及产业链上下游的影响",
      "purpose": "理解收购对产品价格、创新速度和供应链稳定性的潜在影响"
    },
    {
      "id": "task_6",
      "description": "探讨可能的监管与反垄断风险",
      "purpose": "识别该交易在中美及其他主要市场中是否可能被阻止"
    }
  ],
  "explanation": "该问题涉及多个层面的分析：事实真实性、商业战略、市场结构、技术整合与政策风险。由于苹果与小米均为全球科技巨头，此类收购若属实将引发广泛影响，需系统性拆解才能准确评估。因此采用苏格拉底式任务分解以引导深度思考。"
}
```
    Returns:
        list，子任务列表

    """
    if model_output.startswith("```"):
        model_output = model_output.strip("```json").strip("```").strip()
    try:
        output_json = json.loads(model_output)
        complexity = 1 if output_json.get("complexity", "") == "复杂" else 0
        if not complexity:
            return [query]
        subtasks = output_json.get("subtasks", [])
        return [i.get("description", "") for i in subtasks]
    except json.JSONDecodeError:
        print("模型输出不是有效的JSON格式")
        return []

if __name__ == '__main__':
    q_list = ["how's it going?", "what's the weather today?", "LIFE 与 AGENT Q价格差异","what's difference between LIFE and AGENT Q?","苹果收购小米对市场的影响？"]
    for q in q_list:
        print(sub_qustions_main(q, SUB_QUESTIONS_SYSTEM_CONTENT))

