# Ace Data Cloud model provider: your first Dify workflow

Connect a chat model to Dify and turn three expense amounts into a JSON summary. This example uses `gpt-4.1-mini` and has been run in Dify CE 1.17.1.

[Simplified Chinese](https://github.com/AceDataCloud/ModelProviderDify/blob/main/readme/README_zh_Hans.md) · [Install from Marketplace](https://marketplace.dify.ai/plugin/acedatacloud/acedatacloud)

## 1. Install the model provider

Open the Marketplace link above, check **Ace Data Cloud** by **acedatacloud**, click **Install**, and choose your workspace. In Dify, open **Integrations → Model Provider**. You should see **Ace Data Cloud**. This is a model provider; do not look for it under Tools.

## 2. Copy or create your API key

1. Sign in at [Ace Data Cloud → Applications](https://platform.acedata.cloud/console/applications) and open **General application**.
2. Click **1** in the screenshot to copy the selected API key. For a separate Dify key, use **2 → Manage Keys → Create**.

![Copy the selected key or open key management](https://raw.githubusercontent.com/AceDataCloud/ModelProviderDify/3f711095cb4dc317a32e3b6bc1e8659d6a112019/_assets/tutorial/get-api-key-en.png)

3. Name the new key, optionally set expiration and usage/API restrictions, then click **Create**. Return to the list or application card and copy it.

![Create an optional separate API key](https://raw.githubusercontent.com/AceDataCloud/ModelProviderDify/3f711095cb4dc317a32e3b6bc1e8659d6a112019/_assets/tutorial/create-api-key-en.png)

A general-application key can access multiple services your account is entitled to use; a service-specific key is limited to its service. Confirm `gpt-4.1-mini` access and balance before the first run. If you restrict Allowed APIs, permit the unified model listing `/v1/models` and Chat Completions `/v1/chat/completions`. Paste only the token string in Dify, without `Bearer ` or quotation marks. Do not use a platform management token.

## 3. Add the model in Dify

Open **Integrations → Model Provider → Ace Data Cloud → Add Model** and fill:

| Field | First-run value |
|---|---|
| Model ID | `gpt-4.1-mini` |
| Model Type | LLM |
| Authorization Name | `Ace Data Cloud` |
| API key | Your copied API token |
| Context token limit | `128000` |
| Maximum output tokens | `1024` |
| Tool calling | Disabled |
| Streaming tool calls | Disabled |
| Image input | Disabled |

Click **Add**. The API endpoint and Chat Completions mode are supplied by the plugin; you do not need to enter a Base URL. Saving checks the key and model ID without generating paid content.

![Actual Add Model dialog](https://raw.githubusercontent.com/AceDataCloud/ModelProviderDify/3f711095cb4dc317a32e3b6bc1e8659d6a112019/_assets/tutorial/02-authorize.png)

## 4. Create Start → LLM → Output

In **Studio**, click **Create → Create from Blank → Workflow**. Name it `Expense summary`. Add an **LLM** node and an **Output** node using **+**, and drag the connectors in this order:

**Start → LLM → Output**.

In **Start**, add a Paragraph input named `expenses` with label `Expenses JSON`, mark it required, and allow at least 2000 characters. In **LLM**, choose **Ace Data Cloud / gpt-4.1-mini**, Temperature `0`, Maximum tokens `400`. Keep failure retries off.

Use this system prompt:

```text
Return only a valid JSON object with keys currency, items, count and total.
Preserve each input name and numeric amount. Count the items and sum their amounts to two decimal places.
Do not add or omit any item. No markdown or extra text.
```

In the user prompt, type `Summarize these expenses:` and use the variable picker to insert **Start → expenses**. Do not paste the API key into a prompt.

![Select the model and input variable](https://raw.githubusercontent.com/AceDataCloud/ModelProviderDify/3f711095cb4dc317a32e3b6bc1e8659d6a112019/_assets/tutorial/03-configure.png)

In **Output**, add an output named `summary_json` and select **LLM → text** (String).

![Return the LLM text](https://raw.githubusercontent.com/AceDataCloud/ModelProviderDify/3f711095cb4dc317a32e3b6bc1e8659d6a112019/_assets/tutorial/05-output.png)

## 5. Run and compare the result

Click **Test Run**, paste this into **Expenses JSON**, then click **Start Run**:

```json
{"currency":"CNY","items":[{"name":"coffee","amount":12.5},{"name":"lunch","amount":28.75},{"name":"taxi","amount":8.75}]}
```

When the three nodes finish, `summary_json` should be valid JSON with the original items, `count: 3` and `total: 50.00`. This model node returns its completed text directly; do not add a media-task retrieval tool.

```json
{"currency":"CNY","items":[{"name":"coffee","amount":12.5},{"name":"lunch","amount":28.75},{"name":"taxi","amount":8.75}],"count":3,"total":50.00}
```

![Actual successful expense-summary run](https://raw.githubusercontent.com/AceDataCloud/ModelProviderDify/3f711095cb4dc317a32e3b6bc1e8659d6a112019/_assets/tutorial/06-result.png)

[Download the importable workflow](https://github.com/AceDataCloud/ModelProviderDify/raw/refs/heads/main/docs/quickstart.dify.yml). Import it in Studio and configure your own key; it contains no credentials.

## Troubleshooting and cost

| Problem | Check |
|---|---|
| Model cannot be saved | Exact model ID, generation API token, expiration, service access and Allowed APIs. |
| Model missing in the LLM selector | Add the custom model under Ace Data Cloud, then select that provider/model in the node. |
| 401/403 | Key, permissions, content policy and balance; never send your key in a support message. |
| 429 | Wait and reduce concurrency. |
| Timeout/5xx | Check request history before resubmitting; the plugin does not retry paid calls automatically. |
| Text contains markdown or the wrong total | Keep the JSON instruction and validate the answer; LLM arithmetic should be checked before business use. |

The plugin is free; model calls use current Ace Data Cloud service pricing. Dify can display zero estimated price because no static price is supplied; the account usage ledger is authoritative. Requests go to `api.acedata.cloud`. See [Privacy](https://github.com/AceDataCloud/ModelProviderDify/blob/main/PRIVACY.md).

This provider supports Chat Completions. Responses-only/other protocols, image generation, embeddings and audio/video endpoints are not selectable chat models here. Enable optional vision/tool features only for models that support them.

[Source](https://github.com/AceDataCloud/ModelProviderDify) · [Issues](https://github.com/AceDataCloud/ModelProviderDify/issues) · dev@acedata.cloud
