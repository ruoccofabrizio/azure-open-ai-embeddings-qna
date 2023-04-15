# Azure OpenAI Embeddings QnA

A simple web application for a OpenAI-enabled document search. This repo uses Azure OpenAI Service for creating embeddings vectors from documents. For answering the question of a user, it retrieves the most relevant document and then uses GPT-3 to extract the matching answer for the question.

![Architecture](docs/architecture.png)

# IMPORTANT NOTE (OpenAI generated)
We have made some changes to the data format in the latest update of this repo. 
<br>The new format is more efficient and compatible with the latest standards and libraries. However, we understand that some of you may have existing applications that rely on the previous format and may not be able to migrate to the new one immediately.

Therefore, we have provided a way for you to continue using the previous format in a running application. All you need to do is to set your web application tag to fruocco/oai-embeddings:2023-03-27_25. This will ensure that your application will use the data format that was available on March 27, 2023. We strongly recommend that you update your applications to use the new format as soon as possible.

If you want to move to the new format, please go to:
-   "Add Document" -> "Add documents in Batch" and click on "Convert all files and add embeddings" to reprocess your documents. 
          
# Use the Repo with Chat based deployment (gpt-35-turbo or gpt-4-32k or gpt-4)
By default, the repo uses an Instruction based model (like text-davinci-003) for QnA and Chat experience.  
If you want to use a Chat based deployment (gpt-35-turbo or gpt-4-32k or gpt-4), please change the environment variables as described [here](#environment-variables)

# Running this repo
You have multiple options to run the code:
-   [Deploy on Azure (WebApp + Azure Cache for Redis + Batch Processing)](#deploy-on-azure-webapp--azure-cache-for-redis-enterprise--batch-processing)
-   [Deploy on Azure (WebApp + Redis Stack + Batch Processing)](#deploy-on-azure-webapp--redis-stack--batch-processing)
-   [Run everything locally in Docker (WebApp + Redis Stack + Batch Processing)](#run-everything-locally-in-docker-webapp--redis-stack--batch-processing)
-   [Run everything locally in Python with Conda (WebApp only)](#run-everything-locally-in-python-with-conda-webapp-only)
-   [Run everything locally in Python with venv](#run-everything-locally-in-python-with-venv)
-   [Run WebApp locally in Docker against an existing Redis deployment](#run-webapp-locally-in-docker-against-an-existing-redis-deployment)

## Deploy on Azure (WebApp + Azure Cache for Redis Enterprise + Batch Processing)
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fruoccofabrizio%2Fazure-open-ai-embeddings-qna%2Fmain%2Finfrastructure%2FdeploymentACRE.json)

Click on the Deploy to Azure button to automatically deploy a template on Azure by with the resources needed to run this example. This option will provision an instance of [Azure Cache for Redis](https://learn.microsoft.com/azure/azure-cache-for-redis/cache-overview) with [RediSearch](https://learn.microsoft.com/azure/azure-cache-for-redis/cache-redis-modules#redisearch) installed to store vectors and perform the similiarity search. 

Please be aware that you still need:
-   an existing Azure OpenAI resource with models deployments (instruction models e.g. `text-davinci-003`, and embeddings models e.g. `text-embedding-ada-002`) 
-   an existing Form Recognizer Resource 
-   an existing Translator Resource
-   Azure marketplace access. (Azure Cache for Redis Enterprise uses the marketplace for IP billing)

You will add the endpoint and access key information for these resources when deploying the template. 

## Deploy on Azure (WebApp + Redis Stack + Batch Processing)
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fruoccofabrizio%2Fazure-open-ai-embeddings-qna%2Fmain%2Finfrastructure%2Fdeployment.json)

Click on the Deploy to Azure button and configure your settings in the Azure Portal as described in the [Environment variables](#environment-variables) section.

Please be aware that you need:
-   an existing Azure OpenAI resource with models deployments (instruction models e.g. `text-davinci-003`, and embeddings models e.g. `text-embedding-ada-002`) 
-   an existing Form Recognizer Resource (OPTIONAL - if you want to extract text out of documents)
-   an existing Translator Resource (OPTIONAL - if you want to translate documents)

## Run everything locally in Docker (WebApp + Redis Stack + Batch Processing)

First, clone the repo:

```console
git clone https://github.com/ruoccofabrizio/azure-open-ai-embeddings-qna
cd azure-open-ai-embeddings-qna
```

Next, configure your `.env` as described in [Environment variables](#environment-variables):


```console
cp .env.template .env
vi .env # or use whatever you feel comfortable with
```

Finally run the application:

```console
docker compose up
```

Open your browser at [http://localhost:8080](http://localhost:8080)

This will spin up three Docker containers:
-   The WebApp itself
-   Redis Stack for storing the embeddings
-   Batch Processing Azure Function

NOTE: Please note that the Batch Processing Azure Function uses an Azure Storage Account for queuing the documents to process. Please create a Queue named "doc-processing" in the account used for the "AzureWebJobsStorage" env setting.

## Run everything locally in Python with Conda (WebApp only)

This requires Redis running somewhere and expects that you've setup `.env` as described above. In this case, point `REDIS_ADDRESS` to your Redis deployment. 

You can run a local Redis instance via:
```console
 docker run -p 6379:6379 redis/redis-stack-server:latest
```

You can run a local Batch Processing Azure Function:
```console
 docker run -p 7071:80 fruocco/oai-batch:latest
```

Create `conda` environment for Python:

```console
conda env create -f code/environment.yml
conda activate openai-qna-env
```

Configure your `.env` as described in as described in [Environment variables](#environment-variables)

Run WebApp:
```console
cd code
streamlit run OpenAI_Queries.py
```

## Run everything locally in Python with venv
This requires Redis running somewhere and expects that you've setup `.env` as described above. In this case, point `REDIS_ADDRESS` to your Redis deployment. 

You can run a local Redis instance via:
```console
 docker run -p 6379:6379 redis/redis-stack-server:latest
```

You can run a local Batch Processing Azure Function:
```console
 docker run -p 7071:80 fruocco/oai-batch:latest
```

Please ensure you have Python 3.9+ installed.

Create `venv` environment for Python:

```console
python -m venv .venv
.venv\Scripts\activate
```

Install `PIP` Requirements
```console
pip install -r code\requirements.txt
```

Configure your `.env` as described in as described in [Environment variables](#environment-variables)

Run the WebApp
```console
cd code
streamlit run OpenAI_Queries.py
```

## Run WebApp locally in Docker against an existing Redis deployment

### Option 1 - Run the prebuilt Docker image

Configure your `.env` as described in as described in [Environment variables](#environment-variables)

Then run:

```console
docker run --env-file .env -p 8080:80 fruocco/oai-embeddings:latest
```

### Option 2 - Build the Docker image yourself

Configure your `.env` as described in as described in [Environment variables](#environment-variables)

```console
docker build . -f Dockerfile -t your_docker_registry/your_docker_image:your_tag
docker run --env-file .env -p 8080:80 your_docker_registry/your_docker_image:your_tag
```

Note: You can use 
-   WebApp.Dockerfile to build the Web Application
-   BatchProcess.Dockerfile to build the Azure Function for Batch Processing

## Environment variables

Here is the explanation of the parameters:

| App Setting | Value | Note |
| --- | --- | ------------- |
|OPENAI_ENGINE|text-davinci-003|Engine deployed in your Azure OpenAI resource. E.g. Instruction based model: text-davinci-003 or Chat based model: gpt-35-turbo or gpt-4-32k or gpt-4. Please use the deployment name and not the model name.|
|OPENAI_DEPLOYMENT_TYPE | Text | Text for Instruction engines (text-davinci-003), <br> Chat for Chat based deployment (gpt-35-turbo or gpt-4-32k or gpt-4) |
|OPENAI_EMBEDDINGS_ENGINE_DOC | text-embedding-ada-002  | Embedding engine for documents deployed in your Azure OpenAI resource|
|OPENAI_EMBEDDINGS_ENGINE_QUERY | text-embedding-ada-002  | Embedding engine for query deployed in your Azure OpenAI resource|
|OPENAI_API_BASE | https://YOUR_AZURE_OPENAI_RESOURCE.openai.azure.com/ | Your Azure OpenAI Resource name. Get it in the [Azure Portal](https://portal.azure.com)|
|OPENAI_API_KEY| YOUR_AZURE_OPENAI_KEY | Your Azure OpenAI API Key. Get it in the [Azure Portal](https://portal.azure.com)|
|REDIS_ADDRESS| api | URL for Redis Stack: "api" for docker compose|
|REDIS_PORT | 6379 | Port for Redis |
|REDIS_PASSWORD| redis-stack-password | OPTIONAL - Password for your Redis Stack|
|REDIS_ARGS | --requirepass redis-stack-password | OPTIONAL - Password for your Redis Stack|
|REDIS_PROTOCOL| redis:// | |
|CHUNK_SIZE | 500 | OPTIONAL: Chunk size for splitting long documents in multiple subdocs. Default value: 500 |
|CHUNK_OVERLAP |100 | OPTIONAL: Overlap between chunks for document splitting. Default: 100 |
|CONVERT_ADD_EMBEDDINGS_URL| http://batch/api/BatchStartProcessing | URL for Batch processing Function: "http://batch/api/BatchStartProcessing" for docker compose |
|AzureWebJobsStorage | AZURE_BLOB_STORAGE_CONNECTION_STRING FOR_AZURE_FUNCTION_EXECUTION | Azure Blob Storage Connection string for Azure Function - Batch Processing |



Optional parameters for additional features (e.g. document text extraction with OCR):

| App Setting | Value | Note |
| --- | --- | ------------- |
|BLOB_ACCOUNT_NAME| YOUR_AZURE_BLOB_STORAGE_ACCOUNT_NAME| OPTIONAL - Get it in the [Azure Portal](https://portal.azure.com) if you want to use the document extraction feature |
|BLOB_ACCOUNT_KEY| YOUR_AZURE_BLOB_STORAGE_ACCOUNT_KEY| OPTIONAL - Get it in the [Azure Portal](https://portal.azure.com)if you want to use document extraction feature|
|BLOB_CONTAINER_NAME| YOUR_AZURE_BLOB_STORAGE_CONTAINER_NAME| OPTIONAL - Get it in the [Azure Portal](https://portal.azure.com) if you want to use document extraction feature|
|FORM_RECOGNIZER_ENDPOINT| YOUR_AZURE_FORM_RECOGNIZER_ENDPOINT| OPTIONAL - Get it in the [Azure Portal](https://portal.azure.com) if you want to use document extraction feature|
|FORM_RECOGNIZER_KEY| YOUR_AZURE_FORM_RECOGNIZER_KEY| OPTIONAL - Get it in the [Azure Portal](https://portal.azure.com) if you want to use document extraction feature|
|PAGES_PER_EMBEDDINGS| Number of pages for embeddings creation. Keep in mind you should have less than 3K token for each embedding.| Default: A new embedding is created every 2 pages.|
|TRANSLATE_ENDPOINT| YOUR_AZURE_TRANSLATE_ENDPOINT| OPTIONAL - Get it in the [Azure Portal](https://portal.azure.com) if you want to use translation feature|
|TRANSLATE_KEY| YOUR_TRANSLATE_KEY| OPTIONAL - Get it in the [Azure Portal](https://portal.azure.com) if you want to use translation feature|
|TRANSLATE_REGION| YOUR_TRANSLATE_REGION| OPTIONAL - Get it in the [Azure Portal](https://portal.azure.com) if you want to use translation feature|


# DISCLAIMER
This presentation, demonstration, and demonstration model are for informational purposes only and (1) are not subject to SOC 1 and SOC 2 compliance audits, and (2) are not designed, intended or made available as a medical device(s) or as a substitute for professional medical advice, diagnosis, treatment or judgment. Microsoft makes no warranties, express or implied, in this presentation, demonstration, and demonstration model. Nothing in this presentation, demonstration, or demonstration model modifies any of the terms and conditions of Microsoft’s written and signed agreements. This is not an offer and applicable terms and the information provided are subject to revision and may be changed at any time by Microsoft.

This presentation, demonstration, and demonstration model do not give you or your organization any license to any patents, trademarks, copyrights, or other intellectual property covering the subject matter in this presentation, demonstration, and demonstration model.

The information contained in this presentation, demonstration and demonstration model represents the current view of Microsoft on the issues discussed as of the date of presentation and/or demonstration, for the duration of your access to the demonstration model. Because Microsoft must respond to changing market conditions, it should not be interpreted to be a commitment on the part of Microsoft, and Microsoft cannot guarantee the accuracy of any information presented after the date of presentation and/or demonstration and for the duration of your access to the demonstration model.

No Microsoft technology, nor any of its component technologies, including the demonstration model, is intended or made available as a substitute for the professional advice, opinion, or judgment of (1) a certified financial services professional, or (2) a certified medical professional. Partners or customers are responsible for ensuring the regulatory compliance of any solution they build using Microsoft technologies.
