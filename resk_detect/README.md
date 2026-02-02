# 智能客服问答前置风险分析

基于关键词匹配和情感分析的智能客服转接判断系统，用于自动识别用户是否需要转接人工客服。

## 功能特点

- **关键词匹配**：使用 jieba 分词提取用户输入中的关键词
- **情感分析**：集成通义千问API，识别用户的购买意愿下降或投诉情绪
- **人工服务请求检测**：自动识别用户主动要求转接人工服务的意图
- **双重判断机制**：结合关键词匹配和情感分析，提高判断准确性
- **准确率统计**：提供测试结果分析和准确率计算功能

## 项目结构

```
emotion_keywords_judge/
├── config.py                      # 配置管理
├── emotion_analyzer.py            # 情感分析模块（基于通义千问API）
├── keyword_extractor.py           # 关键词提取模块（基于jieba）
├── judge.py                       # 综合判断逻辑
├── calculate_accuracy.py          # 准确率计算
├── test.py                        # 测试脚本
├── requirements.txt               # 依赖包列表
├── .env.example                   # 环境变量示例
├── keywords.txt                   # 投诉相关关键词列表
├── manual_service_keywords.txt    # 人工服务请求关键词列表
└── data/                          # 测试数据目录
    ├── test_sample_10.csv         # 测试用例（10条）
    ├── test_sample_100.csv        # 测试用例（100条）
    ├── test_sample_500.csv        # 测试用例（500条）
    └── test_sample_results_*.csv  # 测试结果文件
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

1. 复制环境变量示例文件：

```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的通义千问API密钥：

```
QWEN_API_KEY=your_qwen_api_key_here
QWEN_API_URL=https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation
QWEN_MODEL=qwen3-max-thinking
```

## 使用方法

### 运行测试

```bash
python test.py
```

测试脚本会：
- 从 `data/test_sample_10.csv` 读取测试用例
- 对每个用例进行判断分析
- 将结果保存到 `data/test_sample_results_10.csv`

### 计算准确率

```bash
python calculate_accuracy.py
```

准确率计算脚本会：
- 读取测试结果文件
- 对比预期情况和实际结果
- 输出统计信息（总数、正确数、准确率）

### 在代码中使用

```python
from judge import CustomerServiceJudge

# 加载关键词列表
keyword_list = load_keywords('keywords.txt')

# 初始化判断器
judge = CustomerServiceJudge(keyword_list)

# 判断用户查询
result = judge.judge_with_details("这个产品质量太差了，我要投诉")

# 查看结果
print(result['final_result'])           # 最终判断结果（True/False）
print(result['keyword_match'])          # 是否匹配到关键词
print(result['matched_keywords'])       # 匹配到的关键词列表
print(result['emotion_match'])          # 情感分析结果
print(result['manual_service_requested']) # 是否主动要求人工服务
```

## 判断逻辑

系统采用以下判断逻辑：

1. **人工服务请求优先**：如果用户明确要求转接人工服务，直接返回 `True`
2. **关键词匹配**：检查用户输入是否包含投诉相关关键词
3. **情感分析**：使用通义千问API分析用户情感，识别购买意愿下降或投诉情绪
4. **综合判断**：只有同时满足关键词匹配和情感匹配，才判定为需要转接人工服务

## 关键词配置

### 投诉相关关键词 (keywords.txt)

包含退款、退货、投诉、质量问题、服务态度等负面情绪相关词汇。

### 人工服务请求关键词 (manual_service_keywords.txt)

包含"人工"、"转人工"、"人工客服"等表示用户希望转接人工服务的词汇。

## 情感分析标准

系统识别以下情况为需要转接人工服务：

- 明确拒绝（如"不需要了"、"不买了"）
- 价格异议（如"太贵"、"价格高"）
- 竞品倾向
- 消极情绪（如"失望"、"不满"）
- 退出行为（如"怎么退款"、"如何取消"）
- 决策拖延（如"下次再说"、"再看看"）
- 投诉情绪（如"投诉"、"非常不满意"）

## 注意事项

- 需要有效的通义千问API密钥才能使用情感分析功能
- API调用有超时限制（30秒）
- 建议根据实际业务场景调整关键词列表
- 情感分析结果受AI模型性能影响，可能存在误判

## 许可证

No License
