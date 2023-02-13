import pandas as pd
import numpy as np
from openai.embeddings_utils import get_embedding, cosine_similarity
import openai
import os
from tenacity import retry, wait_random_exponential, stop_after_attempt
from transformers import GPT2Tokenizer
from utilities.redisembeddings import execute_query, get_documents
import tiktoken

def initialize(engine='davinci'):
    openai.api_type = "azure"
    openai.api_base = os.getenv('OPENAI_API_BASE')
    openai.api_version = "2022-12-01"
    openai.api_key = os.getenv("OPENAI_API_KEY")


# Semantically search using the computed embeddings locally
def search_semantic(df, search_query, n=3, pprint=True, engine='davinci'):
    embedding = get_embedding(search_query, engine= get_embeddings_model()['query'])
    df['similarities'] = df[f'{engine}_search'].apply(lambda x: cosine_similarity(x, embedding))

    res = df.sort_values('similarities', ascending=False).head(n)
    if pprint:
        for r in res:
            print(r[:200])
            print()
    return res.reset_index()

# Semantically search using the computed embeddings on RediSearch
def search_semantic_redis(df, search_query, n=3, pprint=True, engine='davinci'):
    embedding = get_embedding(search_query, engine= get_embeddings_model()['query'])
    res = execute_query(np.array(embedding))

    if pprint:
        for r in res:
            print(r[:200])
            print()
    return res.reset_index()

# Return a semantically aware response using the Completion endpoint
def get_semantic_answer(df, question, explicit_prompt="", model="DaVinci-text", engine='babbage', limit_response=True, tokens_response=100, temperature=0.0):

    restart_sequence = "\n\n"
    question += "\n"

    res = search_semantic_redis(df, question, n=3, pprint=False, engine=engine)

    if len(res) == 0:
        prompt = f"{question}"
    elif limit_response:
        res_text = "\n".join(res['text'][0:int(os.getenv("NUMBER_OF_EMBEDDINGS_FOR_QNA",1))])
        question_prompt = explicit_prompt.replace(r'\n', '\n')
        question_prompt = question_prompt.replace("_QUESTION_", question)
        prompt = f"{res_text}{restart_sequence}{question_prompt}"
    else:
        prompt = f"{res_text}{restart_sequence}{question}"
            

    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        temperature=temperature,
        max_tokens=tokens_response,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )

    print(f"{response['choices'][0]['text'].encode().decode()}\n\n\n")

    return prompt,response#, res['page'][0]


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def get_embedding(text: str, engine="text-embedding-ada-002") -> list[float]:
    # replace newlines, which can negatively affect performance.
    text = text.replace("\n", " ")
    EMBEDDING_ENCODING = 'cl100k_base' if engine == 'text-embedding-ada-002' else 'gpt2'
    encoding = tiktoken.get_encoding(EMBEDDING_ENCODING)
    return openai.Embedding.create(input=encoding.encode(text), engine=engine)["data"][0]["embedding"]


def chunk_and_embed(text: str, filename="", engine="text-embedding-ada-002"):
    EMBEDDING_ENCODING = 'cl100k_base' if engine == 'text-embedding-ada-002' else 'gpt2'
    encoding = tiktoken.get_encoding(EMBEDDING_ENCODING)

    full_data = {
        "text": text,
        "filename": filename,
        "search_embeddings": None
    }

    lenght = len(encoding.encode(text))
    if engine == 'text-embedding-ada-002' and lenght > 2000:
        return None
    elif lenght > 3000:
        return None

    full_data['search_embeddings'] = get_embedding(text, engine)

    return full_data


def get_completion(prompt="", max_tokens=400, model="text-davinci-003"):
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        temperature=1,
        max_tokens=max_tokens,
        top_p=0.5,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )

    print(f"{response['choices'][0]['text'].encode().decode()}\n\n\n")

    return prompt,response#, res['page'][0]


def get_token_count(text: str):
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    return len(tokenizer(text)['input_ids'])


def get_embeddings_model():
    OPENAI_EMBEDDINGS_ENGINE_DOC = os.getenv('OPENAI_EMEBDDINGS_ENGINE', os.getenv('OPENAI_EMBEDDINGS_ENGINE_DOC', 'text-embedding-ada-002'))  
    OPENAI_EMBEDDINGS_ENGINE_QUERY = os.getenv('OPENAI_EMEBDDINGS_ENGINE', os.getenv('OPENAI_EMBEDDINGS_ENGINE_QUERY', 'text-embedding-ada-002'))
    return {
        "doc": OPENAI_EMBEDDINGS_ENGINE_DOC,
        "query": OPENAI_EMBEDDINGS_ENGINE_QUERY
    }
