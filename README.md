# Ace Data Cloud model provider: your first Dify workflow

Install **Ace Data Cloud** as a Dify model provider, save one API key, and select **GPT-4.1 mini** in an LLM node. The preset supplies the endpoint and conservative limits; you do not have to type a Base URL, model ID or capability settings. This example turns three expense amounts into JSON and previously ran in Dify CE 1.17.1.

**Version 0.0.4 guide:** provider-wide credentials and the preset model are available when this plugin version is installed. Check the version in your Dify workspace and the [Marketplace entry](https://marketplace.dify.ai/plugin/acedatacloud/acedatacloud); an older installed or public version may still use the custom-model form below. The screenshots are real historical Dify CE 1.17.1 captures from October 9, 2026; they do not show the new provider-key form or prove 0.0.4 installation.

[Simplified Chinese](https://github.com/AceDataCloud/ModelProviderDify/blob/main/readme/README_zh_Hans.md) · [Install from Marketplace](https://marketplace.dify.ai/plugin/acedatacloud/acedatacloud)

## 1. Install the model provider

Open the Marketplace link above, check **Ace Data Cloud** by **acedatacloud**, click **Install**, and choose your workspace. In Dify, open **Integrations → Model Provider**. You should see **Ace Data Cloud**. This is a model provider; do not look for it under Tools.

## 2. Copy or create your API key

New account? Register and sign in first. If the Applications page has no General application yet, choose **Initialize General Application**, then continue with the key steps below.

1. Sign in at [Ace Data Cloud → Applications](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=modelproviderdify_readme_api_key) and open **General application**.
2. Click **1** in the screenshot to copy the selected API key. For a separate Dify key, use **2 → Manage Keys → Create**.

![Copy the selected key or open key management](https://raw.githubusercontent.com/AceDataCloud/ModelProviderDify/3f711095cb4dc317a32e3b6bc1e8659d6a112019/_assets/tutorial/get-api-key-en.png)

3. Name the new key, optionally set expiration and usage/API restrictions, then click **Create**. Return to the list or application card and copy it.

![Create an optional separate API key](https://raw.githubusercontent.com/AceDataCloud/ModelProviderDify/3f711095cb4dc317a32e3b6bc1e8659d6a112019/_assets/tutorial/create-api-key-en.png)

A general-application key can access multiple services your account is entitled to use; a service-specific key is limited to its service. Confirm `gpt-4.1-mini` access and balance before the first run. If you restrict Allowed APIs, permit the unified model listing `/v1/models` and Chat Completions `/v1/chat/completions`. Paste only the token string in Dify, without `Bearer ` or quotation marks. Do not use a platform management token.

## 3. Add the model in Dify

### Version 0.0.4: one provider key, then select the preset

In **Integrations → Model Provider → Ace Data Cloud**, configure the provider credential and paste your **Ace Data Cloud API key**. Saving makes only a read-only `/v1/models` request; it does not generate a response. In an LLM node, choose **Ace Data Cloud → GPT-4.1 mini**. The preset uses a conservative 128,000-token context and a 1,024-token maximum output, with optional vision and tool calling disabled. Service access and balance still apply. If the model is unavailable for your account, choose an exact available model through the custom-model form; no substitute is chosen automatically.

This is the standard Dify model-provider plugin mechanism used for named providers. Marketplace installation does not mean Dify Cloud or a new self-hosted workspace installs Ace by default. No production setting is changed by this release.

### Published 0.0.3 and optional custom models

Use this existing path for a custom model or an installed version earlier than 0.0.4. It remains supported after upgrading.

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

![Historical custom-model dialog, Dify CE 1.17.1, October 9 2026](https://raw.githubusercontent.com/AceDataCloud/ModelProviderDify/3f711095cb4dc317a32e3b6bc1e8659d6a112019/_assets/tutorial/02-authorize.png)

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
| Model missing in the LLM selector | In 0.0.4, save the provider API key and check preset model access. In 0.0.3, add the custom model first. |
| 401/403 | Key, permissions, content policy and balance; never send your key in a support message. |
| 429 | Wait and reduce concurrency. |
| Timeout/5xx | Check request history before resubmitting; the plugin does not retry paid calls automatically. |
| Text contains markdown or the wrong total | Keep the JSON instruction and validate the answer; LLM arithmetic should be checked before business use. |

The plugin is free; model calls use current Ace Data Cloud service pricing. Dify can display zero estimated price because no static price is supplied; the account usage ledger is authoritative. Requests go to `api.acedata.cloud`. See [Privacy](https://github.com/AceDataCloud/ModelProviderDify/blob/main/PRIVACY.md).

This provider supports Chat Completions. Responses-only/other protocols, image generation, embeddings and audio/video endpoints are not selectable chat models here. Enable optional vision/tool features only for models that support them.

[Source](https://github.com/AceDataCloud/ModelProviderDify) · [Issues](https://github.com/AceDataCloud/ModelProviderDify/issues) · dev@acedata.cloud
