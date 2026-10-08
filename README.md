# Ace Data Cloud model provider for Dify

Use an Ace Data Cloud API key to access Chat Completions models from Dify Chatflow,
Workflow and Agent applications. This is one model provider with a fixed HTTPS
endpoint, `https://api.acedata.cloud/v1/chat/completions`.

[Simplified Chinese](readme/README_zh_Hans.md)

## Setup

1. Register or sign in at [Ace Data Cloud](https://platform.acedata.cloud).
2. Open the desired chat service, activate access, and check its current price and
   balance. Create an API key in the console. A service key is limited to that
   service; use a global key for models from multiple services.
3. Install **Ace Data Cloud** from [Dify Marketplace](https://marketplace.dify.ai/plugin/acedatacloud/acedatacloud), or install
   the `.difypkg` from **Plugins → Install plugin → Local package file** in a
   Dify instance that permits local plugins. Submission is not Marketplace approval.
4. Go to **Integrations → Model Provider → Ace Data Cloud → Add Model**
   (older versions: **Settings → Model Providers**). Enter an
   exact Chat Completions model ID, for example `gpt-4.1-mini`, and your API key.
   The endpoint and Chat Completions mode are set by the plugin.
5. Leave the conservative context/output limits or change them within the selected
   model's documented limits. Enable tool calling, streaming tool calls and image
   input only when that model supports them. They are disabled by default.
6. Save and select the model in an LLM node. Connect **Start → LLM → Output**,
   pass a text input to the LLM, and map `LLM.text` into the Output node. Test with
   `Reply only DIFY_OK`. Chatflows use an **Answer** node. For Agent nodes, enable
   tool calling on a supported model first.

The plugin needs outbound HTTPS to `api.acedata.cloud` and Python 3.12 with
`dify-plugin==0.9.1`. It requires a Dify version supporting that SDK.

## Model selection and limits

Use the [current catalog](https://platform.acedata.cloud/models) and the model's
API documentation to choose a model. The authenticated `/v1/models` list confirms
IDs, but it includes models for other API protocols as well. This plugin supports
**Chat Completions only**. Do not add image-generation or embedding models, or
Messages-only models such as `claude-opus-5-5` and `claude-sonnet-5-5`.
Responses, Messages, speech, video and music APIs are outside this provider.

Streaming text, tool messages, streaming tool calls and image input use Dify's SDK
message adapters. User images are passed to the API; the plugin does not download
user URLs. It does not execute model-generated tools: Dify controls tool execution.
The optional Dify user identifier is not forwarded to the API.

Saving a model validates the key and ID using a read-only `/v1/models` request.
It does not prove paid model entitlement, balance or all features. The first real
call checks those. Requests have a 10-second connection timeout and a 120-second
read timeout (30 seconds for validation). Redirects are disabled and there is no
automatic model substitution or retry of billable requests.

## Billing and errors

The plugin is free to install. Ace Data Cloud API usage is charged to the user's
account. Check [live prices](https://platform.acedata.cloud/models) and billing in
the console. Charges are in Credits; their USD value depends on the user's package.
The plugin reports API token usage, but does not publish a fixed USD estimate.
Dify may display zero estimated cost when pricing is absent; this does **not** mean
that API calls are free. In [Usage](https://platform.acedata.cloud/console/usages),
filter by the test key and time window to match the request and deduction.
Ace Data Cloud's billing records are authoritative.

For authentication or access errors, check the API key scope, selected model,
service activation and available balance. HTTP 429 is a rate limit; try later.
HTTP 403 can indicate access or content-policy restrictions. Error messages omit
raw API bodies and credentials. Check the service console for request diagnostics.

## Development and support

- Source repository: https://github.com/AceDataCloud/ModelProviderDify
- Contact: dev@acedata.cloud
- Issues: https://github.com/AceDataCloud/ModelProviderDify/issues
- Privacy: [PRIVACY.md](PRIVACY.md)
- License: MIT

```sh
uv venv --python 3.12
uv pip install -r requirements.txt pytest ruff
.venv/bin/python -m pytest tests -q
.venv/bin/ruff check .
.venv/bin/ruff format --check .
dify plugin package .
```

`tests/live_smoke.py` is an opt-in, billable integration check. It reads
`ACEDATACLOUD_API_TOKEN` from the environment, performs three small requests and
prints only non-secret results. It is never run by unit tests.

## Official Marketplace verification

[Install from Dify Marketplace](https://marketplace.dify.ai/plugin/acedatacloud/acedatacloud). Version 0.0.1 was downloaded and installed through the official Marketplace flow on October 8, 2026, with signature verification enabled and no remote-debug process. The installed plugin then completed the recorded real Dify workflow. [Verification data](tests/marketplace-acceptance.json) and [original Dify screenshot](tests/evidence/marketplace-20261008.png) document the exact scope. This proves optional Marketplace availability, not default installation or featured placement.
