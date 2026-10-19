# Ace Data Cloud 模型供应商：手把手跑通第一个 Dify 工作流

安装 **Ace Data Cloud 模型供应商**，保存 API Key，再选择 **GPT-4.1 mini**。预设已提供接口地址和保守参数，不用手填 Base URL、模型 ID 或能力开关。先完成下方不运行模型的接入步骤；金额汇总工作流是可选的历史示例。

**2026年10月20日真实接入验收：**Dify CE1.17.1正常签名安装 Marketplace **0.0.4** 后，原生凭据保存与实际模型选择通过，没有运行模型。下方公开三张原图和[脱敏验收摘要](https://github.com/AceDataCloud/ModelProviderDify/blob/88bf2f25e5c50a0194aadb9e12ed21aea1d3ea89/_assets/tutorial/native-20261020/acceptance.json)。Applications操作示意图为北京时间10月9日旧图（UTC时间为10月8日），工作流/结果图为10月9日历史实拍。

[English](https://github.com/AceDataCloud/ModelProviderDify/blob/main/README.md) · [官方市场安装入口](https://marketplace.dify.ai/plugin/acedatacloud/acedatacloud)

## 1. 安装模型插件

打开上方市场入口，确认 **Ace Data Cloud**、发布者 **Ace Data Cloud（acedatacloud）**，点 **Install** 并选择工作区。回到 Dify 的 **Integrations（集成）→ Model Provider（模型供应商）**，应能看到 **Ace Data Cloud**。这是模型插件，不在 Tools 工具列表中。

## 2. 在 Applications 创建独立的 Dify 用途 Key

首次使用请先注册并登录；如果应用页还没有通用应用，点击 **初始化通用应用（Initialize General Application）**，再按下面步骤管理密钥。

1. 登录 [Ace Data Cloud → 我的应用](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=modelproviderdify_readme_api_key)，找到 **通用应用**。
2. 建议为这个 Dify 工作区创建独立 Key：点 **②管理密钥 → 创建**，名称可填 `Dify workspace`。如果已有获授权的 consumer Key，可用图中 **①** 复制所选 Key。

![复制Key与管理密钥入口](https://raw.githubusercontent.com/AceDataCloud/ModelProviderDify/3f711095cb4dc317a32e3b6bc1e8659d6a112019/_assets/tutorial/get-api-key-en.png)

3. 设置合适的过期、用量和 API 限制，点 **创建**，再回密钥列表或应用页复制 Token。独立 Key 便于只撤销这一个集成，而不用轮换其他集成的 Key。

![创建独立的Dify Key](https://raw.githubusercontent.com/AceDataCloud/ModelProviderDify/3f711095cb4dc317a32e3b6bc1e8659d6a112019/_assets/tutorial/create-api-key-en.png)

Applications旧图展示已有密钥管理流程，图中的创建窗口当时已取消。这是操作指南，不是新建 Key 的验收证明。10月20日接入验收使用的是既有获授权 consumer API credential，没有新建专用 Applications Token。

通用应用 Key 可用于账号有权使用的多个服务；专用 Key 仅限对应服务。首次运行前确认 `gpt-4.1-mini` 权限和余额。启用 Allowed APIs 时，要允许统一模型列表 `/v1/models` 及聊天接口 `/v1/chat/completions`。Dify 只贴 Token 字符串，不加 `Bearer `、引号，也不要用平台管理 Token。

## 3. 在 Dify 添加模型

### 0.0.4：保存供应商 Key，再选择预设模型

1. 打开 **Integrations → Model Provider → Ace Data Cloud → Configure**。在凭据窗口中按提示填写易识别的名称，把自己的 **Ace Data Cloud API key** 粘贴到保密 API-key 字段。只粘贴 Token，不用管理凭据，也不加 `Bearer ` 前缀。
2. 点一次 **Save**。保存通过只读 `/v1/models` 检查访问权限，不生成模型内容。如果保存超时，先检查现有命名凭据，再决定是否重试。

![2026年10月20日Ace Data Cloud0.0.4原生凭据保存后的真实已配置状态](https://raw.githubusercontent.com/AceDataCloud/ModelProviderDify/44238d0b83a89583ba95beded66a620a39632e0f/_assets/tutorial/native-20261020/01-native-provider-configured.png)

这张原图展示保存后的已配置结果，不展示输入 Key 的动作，也没有 Key 值。

3. 如需先检查原生选择器而不运行工作流，打开 **Default Models**，展开 **System Reasoning Model**，选择 **Ace Data Cloud → GPT-4.1 mini**。下面实拍的是原生设置选择器，不是 LLM 节点运行截图。

![原生模型选择器：保留半透明popover过渡的真实原图](https://raw.githubusercontent.com/AceDataCloud/ModelProviderDify/44238d0b83a89583ba95beded66a620a39632e0f/_assets/tutorial/native-20261020/02-native-model-picker.png)

popover处于真实半透明过渡帧，不能当作稳定截图；[验收摘要](https://github.com/AceDataCloud/ModelProviderDify/blob/88bf2f25e5c50a0194aadb9e12ed21aea1d3ea89/_assets/tutorial/native-20261020/acceptance.json)另行记录了实际 provider/model 元数据与真实点击选择结果。

![GPT-4.1 mini在未保存设置草稿中选中：真实过渡帧](https://raw.githubusercontent.com/AceDataCloud/ModelProviderDify/44238d0b83a89583ba95beded66a620a39632e0f/_assets/tutorial/native-20261020/03-native-model-draft-selected.png)

后一张选择器原图也保留过渡半透明。点 **Cancel** 可退出这次检查而不保存工作区默认模型；本次验收停在未保存、未运行的选择草稿。之后在自己的工作流 LLM 节点中选择同一 **Ace Data Cloud → GPT-4.1 mini** 预设，再决定是否运行。

预设采用128,000 Token上下文和1,024 Token最大输出，默认关闭图片与工具调用；仍需对应模型权限和余额。若账号无法使用该模型，可通过自定义方式添加目录中确实可用的模型，插件不会自动换模型。

这是 Dify 命名模型供应商使用的标准插件机制。市场安装不表示 Dify Cloud 或新建自部署工作区会默认安装 Ace；本次更新不改生产默认配置。

### 可选自定义模型及较旧的已安装版本

已安装版本早于 0.0.4，或需要其他自定义模型时，使用下面已有路径；升级后仍然支持。

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

![历史自定义模型窗口：Dify CE 1.17.1，2026年10月9日](https://raw.githubusercontent.com/AceDataCloud/ModelProviderDify/3f711095cb4dc317a32e3b6bc1e8659d6a112019/_assets/tutorial/02-authorize.png)

## 4. 连接 Start → LLM → Output

以下金额汇总工作流及结果图是2026年10月9日历史示例，没有在10月20日接入验收中重跑。执行第5步模型请求时，会按账号当前服务价格计费。

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

## 10月20日实际验证了什么

| 验收项 | 记录结果 |
|---|---|
| 安装 | Provider0.0.4普通签名 Marketplace安装；exact package identifier与verified状态读回。 |
| 原生凭据 | 唯一一次Save返回201；独立只读DB检查命名记录为1且active指向匹配，没有选择凭据值。 |
| 模型选择 | 原生元数据包含Ace / `gpt-4.1-mini`，真实点击选择器并在未保存设置草稿中显示选中。 |
| 边界 | 没有模型/生成请求、响应mock、复用用户profile/cookie或提交工作区默认模型；临时fixture已正常清理。 |

[公开脱敏记录与原图哈希](https://github.com/AceDataCloud/ModelProviderDify/blob/88bf2f25e5c50a0194aadb9e12ed21aea1d3ea89/_assets/tutorial/native-20261020/acceptance.json)证明正常安装和原生接入，不代表默认预装、Dify Cloud、收费推理、唯一账单或渠道归因通过。本次没有新建专用Applications Token。02/03原图如实保留过渡半透明，没有为美观再开环境或重跑已成功的Save。

本源码仓指南可能新于已发布的不可变0.0.4市场包内README。本次只更新文档，不重包或替换已有0.0.4。

## 常见问题与费用

| 现象 | 检查方法 |
|---|---|
| 保存模型失败 | 核对精确模型 ID、生成 API Token、过期时间、服务权限、Allowed APIs。 |
| LLM 下拉框没有模型 | 0.0.4 保存供应商 Key 后检查预设模型权限；0.0.3 先添加自定义模型。 |
| 401/403 | 检查 Key、权限、内容限制及余额；反馈时不要发送 Key。 |
| 429 | 稍后再试并降低并发。 |
| 超时/5xx | 重提前先看请求历史；插件不自动重试付费调用。 |
| 出现 Markdown 或总额错误 | 保留 JSON 提示并核对结果；用于业务计算前需要独立校验模型答案。 |

插件免费，API 按当前服务价格计费。Dify 因未配置固定价格可能显示估价为零，真实扣费以 Ace Data Cloud 用量页为准。请求发往 `api.acedata.cloud`，详见[隐私说明](https://github.com/AceDataCloud/ModelProviderDify/blob/main/PRIVACY.md)。

本插件支持 Chat Completions；Responses-only 等其他协议、图片生成、向量及音视频接口不是此处的聊天模型。只有模型确实支持时，再开启图片或工具调用。

[源码](https://github.com/AceDataCloud/ModelProviderDify) · [问题反馈](https://github.com/AceDataCloud/ModelProviderDify/issues) · dev@acedata.cloud
