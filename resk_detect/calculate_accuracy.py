import csv

def load_results(file_path):
    """加载测试结果文件"""
    results = []
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)
    return results

def calculate_accuracy(results):
    """计算准确率"""
    total = len(results)
    correct = 0
    
    for result in results:
        expected = result['预期情况'].lower().strip()
        actual = result['最终结果'].lower().strip()
        
        if expected == actual:
            correct += 1
    
    accuracy = correct / total if total > 0 else 0
    return total, correct, accuracy

def display_results(total, correct, accuracy):
    """显示统计结果"""
    print("=" * 60)
    print("测试结果统计")
    print("=" * 60)
    print(f"总测试用例数: {total}")
    print(f"符合预期的数量: {correct}")
    print(f"不符合预期的数量: {total - correct}")
    print(f"准确率: {accuracy:.4f}")
    print("=" * 60)
    

def main():
    input_file = 'data/test_sample_results_100.csv'
    
    print(f"正在分析 {input_file}...\n")
    
    # 加载测试结果
    results = load_results(input_file)
    
    # 计算准确率
    total, correct, accuracy = calculate_accuracy(results)
    
    # 显示统计结果
    display_results(total, correct, accuracy)
    

if __name__ == "__main__":
    main()
