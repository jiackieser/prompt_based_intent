# intent

基于本地部署的 Qwen 模型实现“对话查询改写”与评测的示例项目。包含：

- 查询改写 FastAPI 服务
- 采样脚本与准确率评估脚本
- 语义相关性评测脚本

## 功能概览

- 将多轮对话中的指代消解并补全为“可独立搜索”的查询
- 输出改写结果并计算准确率
- 支持批量评测语义相关性

## 目录结构

- api.py：FastAPI 接口服务（查询改写）
- main.py：离线批量改写 + 计算准确率
- prompt_templates.py：系统提示词与用户提示词拼装
- sample_data.py：正负样本抽样并生成 sampled_data_1.csv
- semantic_based_accuracy.py：语义相关性评估
- data/：样本与输出 CSV

## 环境依赖

建议使用 Python 3.10+。

主要依赖：

- openai
- python-dotenv
- fastapi
- uvicorn
- scipy
- jieba

如需使用 requirements.txt，可自行创建并安装上述依赖。

## 配置说明

脚本会自动读取项目根目录下的 .env 文件（可选）。
本项目配置为本地部署的 Qwen 模型（vLLM）：

- api.py 使用 BASE_URL = https://vllm-qwen3.vertu.cn/v1
- main.py 使用 BASE_URL = https://vllm-qwen3.vertu.cn/v1
- semantic_based_accuracy.py 使用 BASE_URL = https://vllm-qwen3-lite.vertu.cn/v1

如需切换模型或地址，请直接修改对应文件中的 BASE_URL 与 MODEL_NAME。

## 使用方式

### 1) 启动 API 服务

运行 api.py 后访问 http://localhost:8000/docs 查看接口文档。

接口：

- GET /：服务信息
- GET /health：健康检查
- POST /api/rewrite：单条改写
- POST /api/batch-rewrite：批量改写

请求示例（简化）：

- param_pairs：历史对话（question/answer 列表）
- context.window_size：对话窗口大小（默认 1）

### 2) 生成采样数据

sample_data.py 会从 data/negative_data.csv 与 data/positive_data.csv 抽样并生成 data/sampled_data_1.csv。

### 3) 批量改写 + 准确率统计

main.py 读取 data/sampled_data_1.csv，调用模型生成改写并输出到 data/sample_records_10.csv，同时输出准确率。

### 4) 语义相关性评测

semantic_based_accuracy.py 基于 data/sample_records_10.csv 计算语义准确率并写回新增列 semantic_related。

## 数据文件说明

- data/positive_data.csv：正样本
- data/negativve_data.csv：负样本（文件名为 negativve_data.csv）
- data/sampled_data_1.csv：抽样后的混合数据
- data/sample_records_10.csv：模型输出与评测结果

## 常见问题

- 如果出现 404，请检查 BASE_URL 是否包含 /v1。
- 如果输出为空或报错，请确认模型服务可访问且 MODEL_NAME 正确。

## License

未指定。
