# Privacy policy — Ace Data Cloud Dify model provider

Effective date: 2026-10-06. Maintainer: Ace Data Cloud (dev@acedata.cloud).

## Data sent and purpose

The plugin transmits your API key to `api.acedata.cloud` in an HTTPS Authorization
header. Credential validation reads the available model IDs. Model invocations
send your selected model, conversation messages, system instructions, enabled
image inputs, tool definitions, tool results and generation parameters to the same
API to produce the requested answer. Prompts and tool results may contain personal
data if you include it. The service also receives ordinary request metadata,
including the calling server's IP address and token usage needed to operate and
bill the API.

## Storage, logging and recipients

The plugin adds no database, filesystem storage, analytics or telemetry. It does
not intentionally log prompts, API keys or raw API errors. It holds request data
in memory during a call and returns results and token usage to Dify. Dify manages
saved credentials, conversations and its own logging according to your deployment.
The plugin does not forward Dify's optional end-user identifier.

The plugin's only direct external API recipient is Ace Data Cloud. API-side
processing, service providers, retention and user rights are governed by the
[Ace Data Cloud privacy policy](https://platform.acedata.cloud/privacy).
This plugin makes no additional promise of zero retention by the API service.
Image URLs or image data, if enabled, are sent as model input; the plugin does not
fetch arbitrary URLs itself.

## Your choices and requests

Only send content you are authorized to process. Disable image input or tool
calling when unnecessary. Remove the saved model credential in Dify to stop use;
revoke the API key in Ace Data Cloud to invalidate it. Contact dev@acedata.cloud
for questions or requests concerning API-side personal data, and your Dify
administrator for data retained by your Dify deployment.
