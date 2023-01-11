# Azure OpenAI Embeddings QnA

Simple web application for creating Azure OpenAI embeddings vectors, retrieve the most relevant document, and apply QnA on it.

## Application Settings

| App Setting | Value | Note |
| --- | --- | ------------- |
|engines| davinci-002,text-curie-001,text-babbage-001,text-ada-001 | Engines deployed in your Azure OpenAI Resource |
|embeddings_engines | text-search-davinci-doc-001  | Embeddings engines deployed in your Azure OpenAI Resource |
|redis_address| api | URL for Redis Stack: "api" for docker composer |
|redis_password| redis-stack-password | OPTIONAL - Password for your Redis Stack |
|REDIS_ARGS | --requirepass redis-stack-password | OPTIONAL - Password for your Redis Stack |
|api_base | https://YOUR_AZURE_OPENAI_RESOURCE.openai.azure.com/ | Your Azure OpenAI Resource name. Get it in the [Azure Portal](https://portal.azure.com) |
|api_key| 'YOUR_AZURE_OPENAI_API_KEY' | Your Azure OpenAI Api Key. Get it in the [Azure Portal](https://portal.azure.com)|
|Blob_Account_Name| 'YOUR_AZURE_BLOB_STORAGE_ACCOUNT_NAME'| Get it in the [Azure Portal](https://portal.azure.com)|
|Blob_Account_Key| 'YOUR_AZURE_BLOB_STORAGE_ACCOUNT_KEY'| Get it in the [Azure Portal](https://portal.azure.com)|
|Blob_Container_Name| 'YOUR_AZURE_BLOB_STORAGE_CONTAINER_NAME'| Get it in the [Azure Portal](https://portal.azure.com)|
|Form_Recognizer_Endpoint| 'YOUR_AZURE_FORM_RECOGNIZER_ENDPOINT'| Get it in the [Azure Portal](https://portal.azure.com)|
|Form_Recognizer_Key| 'YOUR_AZURE_FORM_RECOGNIZER_KEY'| Get it in the [Azure Portal](https://portal.azure.com)|

## How to execute the WebApp and a Redis Stack with docker
- Clone the repo
- In the main folder execute docker compose
```
    docker compose up
```
It will spin 2 docker containers:
-   WebApp
-   Redis Stack for embeddings storing

## How to execute the WebApp locally (with an available Redis Stack)
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

## Hot to execute the WebApp with Docker (with an available Redis Stack)
OPTION 1:
- Run a prebuilt docker image
```
    docker run -e .env -p 80:80 fruocco/oai-embeddings:latest
```

OPTION 2:
- Build a docker image
```
    docker build . -t your_docker_registry/your_docker_image:your_tag
```
- Run the image
```
    docker run -e .env -p 80:80 your_docker_registry/your_docker_image:your_tag
```