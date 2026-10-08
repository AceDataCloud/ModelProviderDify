# Ace Data Cloud 模型供应商：手把手跑通第一个 Dify 工作流

把聊天模型接入 Dify，将三项金额汇总为 JSON。本例使用 `gpt-4.1-mini`，已在真实 Dify CE 1.17.1 中运行。

[English](https://github.com/AceDataCloud/ModelProviderDify/blob/main/README.md) · [官方市场安装入口](https://marketplace.dify.ai/plugin/acedatacloud/acedatacloud)

## 1. 安装模型插件

打开上方市场入口，确认 **Ace Data Cloud**、作者 **acedatacloud**，点 **Install** 并选择工作区。回到 Dify 的 **Integrations（集成）→ Model Provider（模型供应商）**，应能看到 **Ace Data Cloud**。这是模型插件，不在 Tools 工具列表中。

## 2. 复制或创建 API Key

1. 登录 [Ace Data Cloud → 我的应用](https://platform.acedata.cloud/console/applications)，找到 **通用应用**。
2. 点击图中 **①** 复制当前 Key。要单独给 Dify 创建 Key，则点 **②管理密钥 → 创建**。

![复制Key与管理密钥入口](https://raw.githubusercontent.com/AceDataCloud/ModelProviderDify/3f711095cb4dc317a32e3b6bc1e8659d6a112019/_assets/tutorial/get-api-key-en.png)

3. 填名称，按需设置过期、用量和 API 限制，点 **创建**，再回列表或应用页复制。

![创建独立的Dify Key](https://raw.githubusercontent.com/AceDataCloud/ModelProviderDify/3f711095cb4dc317a32e3b6bc1e8659d6a112019/_assets/tutorial/create-api-key-en.png)

通用应用 Key 可用于账号有权使用的多个服务；专用 Key 仅限对应服务。首次运行前确认 `gpt-4.1-mini` 权限和余额。启用 Allowed APIs 时，要允许统一模型列表 `/v1/models` 及聊天接口 `/v1/chat/completions`。Dify 只贴 Token 字符串，不加 `Bearer `、引号，也不要用平台管理 Token。

## 3. 在 Dify 添加模型

进入 **Integrations → Model Provider → Ace Data Cloud → Add Model**：

| 字段 | 首跑填写 |
|---|---|
| Model ID（模型 ID） | `gpt-4.1-mini` |
| Model Type（模型类型） | LLM |
| Authorization Name（授权名称） | `Ace Data Cloud` |
| API key | 自己复制的 API Token |
| Context token limit（上下文限制） | `128000` |
| Maximum output tokens（最大输出） | `1024` |
| Tool calling（工具调用） | Disabled（禁用） |
| Streaming tool calls（流式工具调用） | Disabled |
| Image input（图片输入） | Disabled |

点 **Add（添加）**。插件已经配置接口地址和 Chat Completions 模式，不用再填 Base URL。保存只查询模型列表，不生成付费内容。

![真实添加模型窗口](https://raw.githubusercontent.com/AceDataCloud/ModelProviderDify/3f711095cb4dc317a32e3b6bc1e8659d6a112019/_assets/tutorial/02-authorize.png)

## 4. 连接 Start → LLM → Output

进入 **Studio → Create → Create from Blank → Workflow**，命名为 `Expense summary`。用 **+** 添加 LLM 和 Output 节点，将右侧连接点依次连为 **Start → LLM → Output**。

Start 新增 Paragraph（多行文本）输入，变量名 `expenses`，标签 `Expenses JSON`，设为必填，最大长度至少 2000。LLM 节点选择 **Ace Data Cloud / gpt-4.1-mini**，Temperature 填 `0`，Maximum tokens 填 `400`，失败重试关闭。

系统提示词填写：

```text
Return only a valid JSON object with keys currency, items, count and total.
Preserve each input name and numeric amount. Count the items and sum their amounts to two decimal places.
Do not add or omit any item. No markdown or extra text.
```

用户提示词填写 `Summarize these expenses:`，再从变量选择器插入 **Start → expenses**。不要把 API Key 放进提示词。

![选择模型与输入变量](https://raw.githubusercontent.com/AceDataCloud/ModelProviderDify/3f711095cb4dc317a32e3b6bc1e8659d6a112019/_assets/tutorial/03-configure.png)

Output 新增 `summary_json`，变量选择 **LLM → text**，类型为 String。

![输出模型文本](https://raw.githubusercontent.com/AceDataCloud/ModelProviderDify/3f711095cb4dc317a32e3b6bc1e8659d6a112019/_assets/tutorial/05-output.png)

## 5. 实际运行并核对结果

点 **Test Run**，在 **Expenses JSON** 中粘贴：

```json
{"currency":"CNY","items":[{"name":"coffee","amount":12.5},{"name":"lunch","amount":28.75},{"name":"taxi","amount":8.75}]}
```

点 **Start Run**。三个节点完成后，`summary_json` 应是合法 JSON，保留三项输入，`count` 为 3，`total` 为 50.00。聊天模型直接返回完成后的文本，不需要媒体任务查询节点。

```json
{"currency":"CNY","items":[{"name":"coffee","amount":12.5},{"name":"lunch","amount":28.75},{"name":"taxi","amount":8.75}],"count":3,"total":50.00}
```

![真实成功的金额汇总结果](https://raw.githubusercontent.com/AceDataCloud/ModelProviderDify/3f711095cb4dc317a32e3b6bc1e8659d6a112019/_assets/tutorial/06-result.png)

[下载可导入工作流](https://github.com/AceDataCloud/ModelProviderDify/raw/refs/heads/main/docs/quickstart.dify.yml)。在 Studio 导入后配置自己的 Key，文件不含凭据。

## 常见问题与费用

| 现象 | 检查方法 |
|---|---|
| 保存模型失败 | 核对精确模型 ID、生成 API Token、过期时间、服务权限、Allowed APIs。 |
| LLM 下拉框没有模型 | 先在 Ace Data Cloud 下添加自定义模型，再回节点选择对应供应商和模型。 |
| 401/403 | 检查 Key、权限、内容限制及余额；反馈时不要发送 Key。 |
| 429 | 稍后再试并降低并发。 |
| 超时/5xx | 重提前先看请求历史；插件不自动重试付费调用。 |
| 出现 Markdown 或总额错误 | 保留 JSON 提示并核对结果；用于业务计算前需要独立校验模型答案。 |

插件免费，API 按当前服务价格计费。Dify 因未配置固定价格可能显示估价为零，真实扣费以 Ace Data Cloud 用量页为准。请求发往 `api.acedata.cloud`，详见[隐私说明](https://github.com/AceDataCloud/ModelProviderDify/blob/main/PRIVACY.md)。

本插件支持 Chat Completions；Responses-only 等其他协议、图片生成、向量及音视频接口不是此处的聊天模型。只有模型确实支持时，再开启图片或工具调用。

[源码](https://github.com/AceDataCloud/ModelProviderDify) · [问题反馈](https://github.com/AceDataCloud/ModelProviderDify/issues) · dev@acedata.cloud
