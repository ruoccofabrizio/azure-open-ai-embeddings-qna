# Azure OpenAI Embeddings QnA

Simple web application for creating Azure OpenAI embeddings vectors, retrieve the most relevant document, and apply QnA on it.

## Application Settings

| App Setting | Value | Note |
| --- | --- | ------------- |
|embeddings_path | embeddings_text.csv | Filename to locally store computed embeddings |
|engines| davinci-002,text-curie-001,text-babbage-001,text-ada-001 | Engines deployed in your Azure OpenAI Resource |
|embeddings_engines | text-search-davinci-doc-001  | Embeddings engines deployed in your Azure OpenAI Resource |
|api_base | https://YOUR_AZURE_OPENAI_RESOURCE.openai.azure.com/ | Your Azure OpenAI Resource name. Get it in the [Azure Portal](https://portal.azure.com) |
|api_key| 'YOUR_AZURE_OPENAI_API_KEY' | Your Azure OpenAI Api Key. Get it in the [Azure Portal](https://portal.azure.com)|
