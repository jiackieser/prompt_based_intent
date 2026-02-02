#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：prompt_based_intent
@File    ：test_sub_questions.py
@IDE     ：PyCharm
@Author  ：wgl
@Date    ：2026/1/30 14:38
'''
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from intent_recognization.control import sub_qustions_main
from intent_recognization.prompt_template import SUB_QUESTIONS_SYSTEM_CONTENT

def get_sub_question_result():
    test_file = "test_cases.csv"
    df = pd.read_csv(test_file)
    queries = df['question'].tolist()
    # 新建测试csv
    df_result = pd.DataFrame(columns=['question', 'is_complexity', 'varify_complexity'])
    df_result['question'] = queries
    df_result['is_complexity'] = df['is_complexity']
    for q in queries:
        sub_questions = sub_qustions_main(q, SUB_QUESTIONS_SYSTEM_CONTENT)
        if len(sub_questions) == 1:
            print(f"问题: {q} 是简单问题，无需拆解")
            # 写入df_result
            df_result.loc[df_result['question'] == q, 'varify_complexity'] = 0
        else:
            print(f"问题: {q} 是复杂问题，拆解为子任务:")
            for task in sub_questions:
                print(f"- {task}")
            # 写入df_result
            df_result.loc[df_result['question'] == q, 'varify_complexity'] = 1
    df_result.to_csv("test_sub_questions_result.csv", index=False)

def process_question(q):
    sub_questions = sub_qustions_main(q, SUB_QUESTIONS_SYSTEM_CONTENT)
    if len(sub_questions) == 1:
        print(f"问题: {q} 是简单问题，无需拆解")
        return 0
    else:
        print(f"问题: {q} 是复杂问题，拆解为子任务:")
        for task in sub_questions:
            print(f"- {task}")
        return 1

def batch_get_sub_question_result(file_path,target_file_path):
    df = pd.read_csv(file_path)
    queries = df['question'].tolist()
    df_result = pd.DataFrame(columns=['question', 'is_complexity', 'varify_complexity'])
    df_result['question'] = queries
    df_result['is_complexity'] = df['is_complexity']
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(process_question, queries))
    df_result['varify_complexity'] = results
    # 计算并打印准确率varify_complexity = is_complexity的准确率
    accuracy = (df_result['is_complexity'] == df_result['varify_complexity']).mean()
    print(f"复杂度识别准确率: {accuracy * 100:.2f}%")
    df_result.to_csv(target_file_path, index=False)
    # df_result.to_csv("test_sub_questions_result.csv", index=False)


if __name__ == '__main__':
    # test_file = "test_cases.csv"
    test_file = "test_cases_100.csv"
    target_file_path = test_file.replace(".csv", "_result.csv")
    batch_get_sub_question_result(test_file, target_file_path)
