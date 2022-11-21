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

## How to execute the WebApp locally
- Create a python env
```
    python -m venv .venv
```

- Activate python env
```
    .venv\Scripts\activate
```
- Install PIP Requirements
```
    pip install -r code\requirements.txt
```
- Set env variable as described in the section above
- Change CWD
```
    cd code
```
- Run Streamlit
```
    streamlit run OpenAI-Queries.py
```

## Hot to execute the WebApp with Docker
- Build a docker image
```
    docker build . -t your_docker_registry/your_docker_image:your_tag
```
- Run the image
```
    docker run -e .env -p 80:80 your_docker_registry/your_docker_image:your_tag
```