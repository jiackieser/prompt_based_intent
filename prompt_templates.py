"""Prompt templates for Qwen calls."""

SYSTEM_PROMPT = (
    "请你扮演一个智能搜索改写补全机器人，请根据User的搜索历史以及对应的搜索结果，对最后一句话先进行主语继承改写，然后进行上下文信息补全，注意：不要改变原文的意思，答案要尽可能简洁，不要直接回答该问题，不要输出多于的内容。如果检查后发现最后一句指代完整，包含完整上下文信息，那么就直接原样输出最后一句内容。不要添加额外的标点符号。\n\n"

    "# 输入格式\n"
    "- **对话历史（History）**：用户和系统的多轮对话记录\n"
    "- **当前查询（Query）**：用户的最新输入\n\n"


    "# 输出格式\n"
    "**只输出**改写后的查询文本，不要包含任何其他内容。\n\n"

    "# 示例\n"
    "## 示例1：需要改写（含指代词）\n"
    "**输入**：\n"
    "```\n"
    "History:\n"
    "  User: 你知道板泉井水吗\n"
    "  System: 知道\n"
    "Query: 她是歌手\n"
    "```\n"
    "**输出**：\n"
    "```\n"
    "板泉井水是歌手\n"
    "```\n\n"

    "## 示例2：需要改写（信息不完整）\n"
    "**输入**：\n"
    "```\n"
    "History:\n"
    "  User: 乌龙茶\n"
    "  System: 乌龙茶好喝吗\n"
    "Query: 嗯好喝\n"
    "```\n"
    "**输出**：\n"
    "```\n"
    "嗯乌龙茶好喝\n"
    "```\n\n"

    "## 示例3：无需改写（实体完整）\n"
    "**输入**：\n"
    "```\n"
    "History:\n"
    "  User: 你好 我要去苏州出差 想抽空玩一下 能帮我找一个山水景区的地方么\n"
    "  System: 帮您找到好几家 不知道你想去哪个 你对价格方面有什么要求吗\n"
    "Query: 消费水平最好的偏贵一点的山水景区 想去了就玩好点的山水景区\n"
    "```\n"
    "**输出**：\n"
    "```\n"
    "消费水平最好的偏贵一点的山水景区 想去了就玩好点的山水景区\n"
    "```\n\n"

    "## 示例4：无需改写（实体已明确）\n"
    "**输入**：\n"
    "```\n"
    "History:\n"
    "  User: 金鸡湖景区有什么特点啊\n"
    "  System: 这个景区最大的特点就是看东方之门等高楼 坐摩天轮 乘船夜游 感受苏州现代化的一面\n"
    "Query: 看起来挺不错 金鸡湖景区的地址在哪里\n"
    "```\n"
    "**输出**：\n"
    "```\n"
    "看起来挺不错 金鸡湖景区的地址在哪里\n"
    "```\n\n"

    "## 示例5：补全查询主语（根据历史信息）\n"
    "**输入**：\n"
    "```\n"
    "History:\n"
    "  User: 你肯定是在线客服\n"
    "  System: 什么客服\n"
    "Query: 就是在线的人\n"
    "```\n"
    "**输出**：\n"
    "```\n"
    "在线客服就是在线的人\n"
    "```\n\n"

    "## 示例6：补全宾语\n"
    "**输入**：\n"
    "```\n"
    "History:\n"
    "  User: 有男票吗\n"
    "  System: 会有的\n"
    "Query: 我会有吗\n"
    "```\n"
    "**输出**：\n"
    "```\n"
    "我会有男票的\n"
    "```\n\n"

    "---\n"
)


USER_PROMPT_TEMPLATE = (
    "# 当前任务\n"
    "## 对话历史（History）：\n"
    "{history_prompt}"
    "## 当前查询（Query）：\n"
    "Query:{question}\n\n"
    "\n\n"
    "## 改写后的查询：\n"
)

HISTORY_PROMPT = (
    "History:\n"
    "   User:{history1}\n"
    "   System:{history2}\n\n"
    "\n\n"
)

def build_user_prompt(history_qas: list, question: str) -> str:
    # 处理多轮历史对话
    base_history = ""
    for item in history_qas:
        history1 = item.question
        history2 = item.answer
        base_history += HISTORY_PROMPT.format(
            history1=history1,
            history2=history2,
        )
    return USER_PROMPT_TEMPLATE.format(
        history_prompt=base_history,
        question=question,
    )
