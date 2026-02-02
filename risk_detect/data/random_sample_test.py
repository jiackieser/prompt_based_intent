import csv
import random

def load_test_cases(file_path):
    """加载CSV文件中的所有测试用例"""
    test_cases = []
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            test_cases.append(row)
    return test_cases

def random_sample(test_cases, sample_size=10):
    """随机抽取指定数量的测试用例"""
    if len(test_cases) <= sample_size:
        return test_cases
    return random.sample(test_cases, sample_size)

def save_sample(sample_cases, output_file):
    """保存抽取的样本到CSV文件"""
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ['用户请求', '预期情况']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sample_cases)

def main():
    input_file = 'data/test_sample.csv'
    output_file = 'data/test_sample_100.csv'
    sample_size = 100
    
    print(f"正在从 {input_file} 中随机抽取 {sample_size} 条测试用例...")
    
    # 加载所有测试用例
    all_test_cases = load_test_cases(input_file)
    print(f"总共加载了 {len(all_test_cases)} 条测试用例")
    
    # 随机抽取500条
    sample_cases = random_sample(all_test_cases, sample_size)
    
    # 保存到新文件
    save_sample(sample_cases, output_file)
    
    print(f"\n已随机抽取 {len(sample_cases)} 条测试用例")
    print(f"结果已保存至 {output_file}")
    
    # 显示抽取的样本
    print("\n=== 抽取的测试用例 ===")
    for i, case in enumerate(sample_cases, 1):
        print(f"\n{i}. 用户请求: {case['用户请求']}")
        print(f"   预期情况: {case['预期情况']}")

if __name__ == "__main__":
    main()
