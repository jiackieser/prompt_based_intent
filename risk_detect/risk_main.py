import csv
from judge import CustomerServiceJudge

def load_keywords(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        keywords = [line.strip() for line in f if line.strip()]
    return keywords

def load_test_cases(file_path):
    test_cases = []
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            test_cases.append({
                'query': row['用户请求'],
                'expected': row['预期情况']
            })
    return test_cases

def main():
    print("=== 智能客服问答系统测试 ===\n")
    
    keyword_list = load_keywords('keywords.txt')
    print(f"已加载 {len(keyword_list)} 个关键词")
    
    judge = CustomerServiceJudge(keyword_list)
    
    # 测试用例 - 从test_sample.csv文件读取
    test_cases = load_test_cases('data/test_sample_10.csv')
    
    print(f"\n=== 测试用例（从test_sample.csv读取，共{len(test_cases)}条） ===\n")
    
    # 存储测试结果
    results = []
    
    for i, case in enumerate(test_cases, 1):
        print(f"测试用例 {i}:")
        print(f"用户请求: {case['query']}")
        print(f"预期情况: {case['expected']}")
        print("-" * 50)
        
        try:
            # 只传递query，不传递context
            result = judge.judge_with_details(case['query'])
            
            final_result = result['final_result']
            print(f"最终结果: {final_result}")
            print(f"关键词匹配: {result['keyword_match']}")
            print(f"匹配的关键词: {result['matched_keywords']}")
            print(f"情感匹配: {result['emotion_match']}")
            
            # 保存结果
            results.append({
                '用户请求': case['query'],
                '预期情况': case['expected'],
                '最终结果': final_result,
                '情感匹配': result['emotion_match']
            })
            
        except Exception as e:
            print(f"处理失败: {str(e)}")
            # 保存失败结果
            results.append({
                '用户请求': case['query'],
                '预期情况': case['expected'],
                '最终结果': 'error'
            })
        
        print()
    
    # 将结果写入新的CSV文件
    output_file = 'data/test_sample_results_10.csv'
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ['用户请求', '预期情况', '最终结果', '情感匹配']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n=== 测试完成，结果已保存至 {output_file} ===")

if __name__ == "__main__":
    main()