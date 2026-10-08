# Ace Data Cloud 模型供应商

使用 Ace Data Cloud API Key，在 Dify 的 LLM 节点、Chatflow 和 Agent 中调用聊天模型。
插件固定使用 `https://api.acedata.cloud/v1/chat/completions`。

## 安装与配置

1. 登录 [Ace Data Cloud](https://platform.acedata.cloud/console/applications)，开通需要的聊天服务，检查余额与[当前模型价格](https://platform.acedata.cloud/models)。
2. 在凭据中创建 API Key。服务 Key 仅适用于对应服务；全局 Key 可跨服务使用，但账户仍需有相应模型权限。
3. 本插件目前已提交官方 Marketplace 审核，尚未确认上架。发布后在市场中安装 **Ace Data Cloud**。如需审核本候选包，可在允许本地插件的 Dify 环境中通过 **Plugins → Install plugin → Local package file** 安装 `.difypkg`；本地安装不代表官方收录。
4. 打开 **Integrations → Model Provider → Ace Data Cloud → Add Model**；旧版入口为**设置 → 模型供应商**。填写准确的聊天模型 ID，例如 `gpt-4.1-mini`，以及 API Key。无需填写接口地址。
5. 首次文本测试可使用上下文 `4096`、最大输出 `1024`。这些是保守测试设置，不代表模型最大容量。工具调用、流式工具调用和图片输入默认关闭，仅在所选模型支持时启用。
6. 保存模型，在 LLM 节点中选择它。创建**开始 → LLM → 输出**工作流，将用户输入传入 LLM，再将 `LLM.text` 映射到输出。输入 `Reply only DIFY_OK`，确认成功返回。Chatflow 使用**回答**节点输出结果。

保存模型通过只读 `/v1/models` 验证 Key 和模型 ID，不生成付费回答；模型权限、余额和可选能力仍需通过真实调用确认。
仅使用 Chat Completions 模型。不要添加生图、Embedding 或 Messages-only 模型，例如 `claude-opus-5-5`、`claude-sonnet-5-5`。

## 用量与排错

插件免费安装，模型 API 使用 Ace Data Cloud 余额。到[用量页](https://platform.acedata.cloud/console/usages)按 Key 和时间筛选请求，核对状态及实际扣减。
扣费单位为 Credits，USD 换算取决于当前套餐。Dify 的零预估费用不代表 API 免费；以平台用量记录为准。重试和 Agent 多轮调用可能增加请求数。

认证错误时检查 Key、服务权限和模型 ID；403 可能表示访问或内容限制；429 时降低并发并等待；超时或 5xx 时检查[服务状态](https://status.acedata.cloud)。
工具未执行时，检查模型能力及 Agent 的工具配置；工作流成功却无回答时，检查输出节点映射。

插件需要 Python 3.12、`dify-plugin==0.9.1`，并允许访问 `api.acedata.cloud:443`。连接超时 10 秒，生成读取超时 120 秒。
已完成插件包、SDK 与真实 API 验证；完整 Community Edition/Cloud 界面安装仍待验证。

## 隐私与支持

API Key、提示词、启用的图片输入、工具定义和工具结果通过 HTTPS 发送到 Ace Data Cloud。Key 只存放在 Dify 凭据设置中，不写入提示词或导出文件。
插件不下载任意用户 URL、不执行生成的工具，也不额外持久化或记录这些内容；工具执行由 Dify 管理。详见 [PRIVACY.md](../PRIVACY.md)。

源码：https://github.com/AceDataCloud/ModelProviderDify
支持：https://github.com/AceDataCloud/ModelProviderDify/issues
联系：dev@acedata.cloud

## 官方市场安装验收

2026-10-08 已从[官方市场](https://marketplace.dify.ai/plugin/acedatacloud/acedatacloud)安装签名包，并完成记录中的真实 Dify 工作流。未使用 remote-debug。[验收数据](../tests/marketplace-acceptance.json)与[原始截图](../tests/evidence/marketplace-20261008.png)记录了准确范围；此前主流程和高级功能证据继续保留。
