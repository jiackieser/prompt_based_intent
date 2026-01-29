import csv
import os
import unicodedata
import dotenv

from openai import OpenAI
from prompt_templates import SYSTEM_PROMPT, build_user_prompt

dotenv.load_dotenv()


# 使用本地部署的 Qwen 模型
# 注意：OpenAI SDK 的 base_url 需要指向 API 根路径（通常以 /v1 结尾），
# SDK 会自动拼接 /chat/completions；如果把 /chat/completions 写进 base_url 会导致 404。
BASE_URL = "https://vllm-qwen3.vertu.cn/v1"
MODEL_NAME = "/root/autodl-tmp/Qwen3-30B-A3B-Instruct-2507-Int4-W4A16"  

# 本地模型不需要 API Key，使用占位符
# client = OpenAI(api_key="EMPTY", base_url=BASE_URL)

# 从环境变量读取配置
# API_KEY = os.getenv("QWEN_API_KEY")
# BASE_URL = os.getenv("QWEN_BASE_URL")
# MODEL_NAME = os.getenv("QWEN_MODEL_NAME")

# 初始化客户端
client = OpenAI(api_key="EMPTY", base_url=BASE_URL)

def call_qianwen(history_qas, question):
    """·
    将 history_qas（历史对话列表）和 question 拼接后作为千问大模型的输入，
    返回模型生成的结果。
    
    Args:
        history_qas: list，每个元素需有 question 和 answer 属性
        question: str，当前查询
    """
    prompt = build_user_prompt(history_qas, question)
    
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
    )

    return completion.choices[0].message.content

def normalize_text(text):
    """
    去掉空白字符和所有 Unicode 标点符号。
    """
    cleaned = []
    for ch in text:
        if ch.isspace():
            continue
        if unicodedata.category(ch).startswith("P"):
            continue
        cleaned.append(ch)
    return "".join(cleaned)

def compute_accuracy(model_outputs, golden_rewrites):
    """
    计算准确率：去掉空格和标点后，若与模型输出完全一致则计为正确。
    """
    if not golden_rewrites:
        return 0.0

    correct = 0
    for model_output, rewrite in zip(model_outputs, golden_rewrites):
        normalized_rewrite = normalize_text(rewrite)
        normalized_model_output = normalize_text(model_output)
        if normalized_model_output == normalized_rewrite:
            correct += 1

    return correct / len(golden_rewrites)

def main():
    # 假设 CSV 文件名为 data/sampled_data_1.csv，编码为 UTF-8
    csv_file = os.path.join("data", "sampled_data_only_pos.csv")
    output_file = os.path.join("data", "sample_records_only_pos_qwen_30b.csv")
    
    # 存放模型输出的列表
    model_outputs = []
    # 存放原始 rewrite 列的列表
    golden_rewrites = []
    # 存放用于展示的样本记录
    sample_records = []
    
    # 读取 CSV，有表头：history1,history2,question,rewrite
    with open(csv_file, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for idx, row in enumerate(rows, start=1):
        # if idx > 500:
        #     break
        history1 = row["history1"]
        history2 = row["history2"]
        question = row["question"]
        rewrite = row["rewrite"]

        # 构造历史对话列表，使用简单的对象来存储
        class HistoryItem:
            def __init__(self, question, answer):
                self.question = question
                self.answer = answer
        
        history_qas = [HistoryItem(history1, history2)]
        
        # 调用模型获取输出
        model_reply = call_qianwen(history_qas, question)

        model_outputs.append(model_reply)
        golden_rewrites.append(rewrite)

        sample_records.append(
            {
                "history1": history1,
                "history2": history2,
                "question": question,
                "model_output": model_reply,
                "rewrite": rewrite,
            }
        )
        
    
    print("===== 完整历史 + 模型输出 + 原始 rewrite（前5条）=====")
    for i, record in enumerate(sample_records[:5], start=1):
        print(f"样本 {i} -> 历史对话1：{record['history1']}")
        print(f"样本 {i} -> 历史对话2：{record['history2']}")
        print(f"样本 {i} -> Question：{record['question']}")
        print(f"样本 {i} -> 模型改写后的查询：{record['model_output']}")
        print(f"样本 {i} -> 原始 rewrite：{record['rewrite']}\n")

    accuracy = compute_accuracy(model_outputs, golden_rewrites)
    print(f"\n===== 准确率 =====\n{accuracy:.4f}")

    fieldnames = ["history1", "history2", "question", "rewrite", "model_output", "accuracy"]
    for record in sample_records:
        record["accuracy"] = ""
    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sample_records)
        writer.writerow(
            {
                "history1": "",
                "history2": "",
                "question": "",
                "rewrite": "",
                "model_output": "",
                "accuracy": accuracy,
            }
        )

    print(f"\n===== 写入结果 =====\n已写入 {output_file}")


if __name__ == "__main__":
    main()