# Ace Data Cloud model provider: your first Dify workflow

Install **Ace Data Cloud** as a Dify model provider, save an API key, and select **GPT-4.1 mini**. The preset supplies the endpoint and conservative limits, so you do not have to type a Base URL, model ID or capability settings. Start with the no-inference setup below; the optional expense-workflow example is historical.

**Verified setup, October 20, 2026 (UTC+8):** Dify CE 1.17.1 with the ordinary signed Marketplace **0.0.4** package passed native credential saving and real model-picker selection without running a model. Three original captures and a [sanitized acceptance record](https://github.com/AceDataCloud/ModelProviderDify/blob/44238d0b83a89583ba95beded66a620a39632e0f/_assets/tutorial/native-20261020/acceptance.json) are public below. The Applications illustrations are dated October 8; the older workflow/result images are dated October 9.

[Simplified Chinese](https://github.com/AceDataCloud/ModelProviderDify/blob/main/readme/README_zh_Hans.md) · [Install from Marketplace](https://marketplace.dify.ai/plugin/acedatacloud/acedatacloud)

## 1. Install the model provider

Open the Marketplace link above, check **Ace Data Cloud**, published by **Ace Data Cloud (`acedatacloud`)**, click **Install**, and choose your workspace. In Dify, open **Integrations → Model Provider**. You should see **Ace Data Cloud**. This is a model provider; do not look for it under Tools.

## 2. Create a dedicated Dify key in Applications

New account? Register and sign in first. If the Applications page has no General application yet, choose **Initialize General Application**, then continue with the key steps below.

1. Sign in at [Ace Data Cloud → Applications](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=modelproviderdify_readme_api_key) and open **General application**.
2. For a key dedicated to this Dify workspace, choose **2 → Manage Keys → Create**. Give it a recognizable name such as `Dify workspace`. If you already have an authorized consumer key, **1** copies that selected key instead.

![Copy the selected key or open key management](https://raw.githubusercontent.com/AceDataCloud/ModelProviderDify/3f711095cb4dc317a32e3b6bc1e8659d6a112019/_assets/tutorial/get-api-key-en.png)

3. Set an appropriate expiration and usage/API restrictions, then click **Create**. Return to the key list or application card and copy the token. A separate key lets you revoke this integration without rotating other integrations.

![Applications guide: create a separate Dify-purpose API key](https://raw.githubusercontent.com/AceDataCloud/ModelProviderDify/3f711095cb4dc317a32e3b6bc1e8659d6a112019/_assets/tutorial/create-api-key-en.png)

The Applications illustrations show the existing key-management flow; the pictured Create dialog was cancelled. They are instructions, not evidence that a new key was created. The October 20 acceptance used a previously authorized consumer API credential.

A general-application key can access multiple services your account is entitled to use; a service-specific key is limited to its service. Confirm `gpt-4.1-mini` access and balance before the first run. If you restrict Allowed APIs, permit the unified model listing `/v1/models` and Chat Completions `/v1/chat/completions`. Paste only the token string in Dify, without `Bearer ` or quotation marks. Do not use a platform management token.

## 3. Add the model in Dify

### Version 0.0.4: one provider key, then select the preset

1. Open **Integrations → Model Provider → Ace Data Cloud → Configure**. In the credential dialog, enter a recognizable name if requested and paste your **Ace Data Cloud API key** into the secret API-key field. Use the token only, not a management credential or `Bearer ` prefix.
2. Click **Save** once. Saving checks access through read-only `/v1/models`; it does not generate a model response. If saving times out, check the existing credential before trying again.

![Actual Ace Data Cloud 0.0.4 configured state, October 20 2026](https://raw.githubusercontent.com/AceDataCloud/ModelProviderDify/44238d0b83a89583ba95beded66a620a39632e0f/_assets/tutorial/native-20261020/01-native-provider-configured.png)

This original capture shows the configured result after saving, not the secret-entry action. No key value is shown.

3. To inspect the native picker without running a workflow, open **Default Models**, expand **System Reasoning Model**, and select **Ace Data Cloud → GPT-4.1 mini**. The following captures show that native settings picker; they are not LLM-node execution screenshots.

![Native model picker: original semi-transparent transition frame](https://raw.githubusercontent.com/AceDataCloud/ModelProviderDify/44238d0b83a89583ba95beded66a620a39632e0f/_assets/tutorial/native-20261020/02-native-model-picker.png)

The popover was captured during its real semi-transparent transition. This is not a stable-frame capture; the [acceptance record](https://github.com/AceDataCloud/ModelProviderDify/blob/44238d0b83a89583ba95beded66a620a39632e0f/_assets/tutorial/native-20261020/acceptance.json) separately records the observed provider/model metadata and actual selection.

![GPT-4.1 mini selected in an unsaved settings draft: original transition frame](https://raw.githubusercontent.com/AceDataCloud/ModelProviderDify/44238d0b83a89583ba95beded66a620a39632e0f/_assets/tutorial/native-20261020/03-native-model-draft-selected.png)

The second picker capture also retains its transition transparency. **Cancel** closes this inspection without saving workspace defaults; the recorded acceptance stopped with the model selected in an unsaved, unrun draft. For a workflow, choose the same **Ace Data Cloud → GPT-4.1 mini** preset in its LLM node before running it.

The preset uses a conservative 128,000-token context and a 1,024-token maximum output, with optional vision and tool calling disabled. Service access and balance still apply. If the model is unavailable for your account, choose an exact available model through the custom-model form; no substitute is chosen automatically.

This is the standard Dify model-provider plugin mechanism used for named providers. Marketplace installation does not mean Dify Cloud or a new self-hosted workspace installs Ace by default. No production setting is changed by this release.

### Optional custom models and older installed versions

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

The expense-workflow example and its result images below are from October 9,2026. They were not rerun for the October 20 setup acceptance. Running the model in step5 uses your account’s current service pricing.

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

## What the October 20 acceptance proved

| Check | Recorded result |
|---|---|
| Installation | Ordinary signed Marketplace Provider 0.0.4, exact package identifier and verified status read back. |
| Native credentials | One Save returned 201; a separate read-only database check found one matching named credential and the active selection matched it. No credential values were selected. |
| Model selection | Native metadata contained Ace / `gpt-4.1-mini`; the picker was clicked and showed it selected in an unsaved settings draft. |
| Boundaries | No model/generation request, response mock, existing user profile/cookie reuse or workspace-default Save. Temporary fixture normally cleaned. |

See the [public sanitized record and original-image hashes](https://github.com/AceDataCloud/ModelProviderDify/blob/44238d0b83a89583ba95beded66a620a39632e0f/_assets/tutorial/native-20261020/acceptance.json). This proves normal installation and native setup, not default preinstallation, Dify Cloud acceptance, paid inference, unique billing or attribution. No new dedicated Applications key was created for this acceptance. Images 02/03 honestly retain transition transparency; no environment or successful Save was rerun for cosmetic screenshots.

This repository guide can be newer than the README bundled in the immutable 0.0.4 Marketplace package. This documentation update does not rebuild or replace that package.

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
