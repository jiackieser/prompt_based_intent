import csv
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 使用本地部署的 Qwen 模型
BASE_URL = "https://vllm-qwen3-lite.vertu.cn/v1"
MODEL_NAME = "/root/.cache/modelscope/hub/models/okwinds/Qwen3-30B-A3B-Instruct-2507-Int4-W4A16"

# 本地模型不需要 API Key，使用占位符
client = OpenAI(api_key="EMPTY", base_url=BASE_URL)

# 系统提示词
SYSTEM_PROMPT = (
    "你是一个专业的语义相关性判定专家。\n\n"

    "# 任务说明\n"
    "判断以下两段文本是否具有语义相关性。\n\n"

    "# 判断标准\n"
    "- **输出 1**：两段文本表达的核心语义相同或高度相关\n"
    "  - 即使措辞不同，但传达的意思一致\n"
    "  - 关键实体和关系保持一致\n\n"
    "- **输出 0**：两段文本语义不相关或相关性较弱\n"
    "  - 添加额外的文本标点符号\n"
    "  - 表达的主题或意图完全不同\n"
    "  - 关键实体或关系发生改变\n\n"

    "# 输出格式\n"
    "**严格要求**：只输出数字 0 或 1，不要包含任何其他内容。\n"
)

# 用户提示词模板
USER_PROMPT_TEMPLATE = """
# 待判断文本
## 参考文本（rewrite）：
{rewrite}

## 待比较文本（model_output）：
{model_output}


# 判断结果
"""


def semantic_judge(rewrite: str, model_output: str) -> str:
    """
    判断两段文本的语义相关性
    
    Args:
        rewrite: 参考文本
        model_output: 待比较文本
    
    Returns:
        "0" 或 "1"
    """
    prompt = USER_PROMPT_TEMPLATE.format(
        rewrite=rewrite,
        model_output=model_output
    )
    
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    
    text = resp.choices[0].message.content.strip()
    # 提取第一个数字字符
    for char in text:
        if char in ('0', '1'):
            return char
    return "0"  # 默认返回0


def main(): 
    input_file = r"data\sample_records_1.csv"
    output_file = r"data\sample_records_1.csv"

    with open(input_file, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    if "rewrite" not in fieldnames or "model_output" not in fieldnames:
        raise ValueError("CSV缺少rewrite或model_output列")

    result_col = "semantic_related"
    if result_col not in fieldnames:
        fieldnames.append(result_col)

    related_count = 0
    total_count = 0

    for row in rows:
        rewrite = row.get("rewrite", "")
        model_output = row.get("model_output", "")
        if not rewrite and not model_output:
            row[result_col] = ""
            continue

        label = semantic_judge(rewrite, model_output)
        row[result_col] = label

        total_count += 1
        if label == "1":
            related_count += 1

    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    ratio = (related_count / total_count) if total_count else 0.0
    print(f"语义相关占比: {ratio:.4f} ({related_count}/{total_count})")


if __name__ == "__main__":
    main()
