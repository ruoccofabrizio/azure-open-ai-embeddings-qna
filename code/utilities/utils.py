import pandas as pd
import numpy as np
from openai.embeddings_utils import get_embedding, cosine_similarity
import openai
import os
from tenacity import retry, wait_random_exponential, stop_after_attempt
from transformers import GPT2Tokenizer
from utilities.redisembeddings import execute_query, get_documents

def initialize(engine='davinci'):
   
    openai.api_type = "azure"
    openai.api_base = os.getenv('OPENAI_API_BASE')
    openai.api_version = "2022-12-01"
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Read or compute embeddings with model
    return get_documents()

# Semantically search using the computed embeddings locally
def search_semantic(df, search_query, n=3, pprint=True, engine='davinci'):
    embedding = get_embedding(search_query, engine= os.getenv('OPENAI_EMBEDDINGS_ENGINE_QUERY', f'text-search-{engine}-query-001'))
    df['similarities'] = df[f'{engine}_search'].apply(lambda x: cosine_similarity(x, embedding))

    res = df.sort_values('similarities', ascending=False).head(n)
    if pprint:
        for r in res:
            print(r[:200])
            print()
    return res.reset_index()

# Semantically search using the computed embeddings on RediSearch
def search_semantic_redis(df, search_query, n=3, pprint=True, engine='davinci'):
    embedding = get_embedding(search_query, engine= os.getenv('OPENAI_EMBEDDINGS_ENGINE_QUERY', f'text-search-{engine}-query-001'))
    res = execute_query(np.array(embedding))

    if pprint:
        for r in res:
            print(r[:200])
            print()
    return res.reset_index()

# Return a semantically aware response using the Completion endpoint
def get_semantic_answer(df, question, max_tokens=400, explicit_prompt="", model="DaVinci-text", engine='babbage', limit_response=True):

    restart_sequence = "\n\n"
    question += "\n"

    if explicit_prompt == "":
        res = search_semantic_redis(df, question, n=3, pprint=False, engine=engine)
        if len(res) == 0:
            prompt = f"{question}"
        elif limit_response:
            prompt = f"{res['text'][0]}{restart_sequence}Please reply to the question using only the information present in this text or reply 'Not in the text': {question}"
        else:
            prompt = f"{res['text'][0]}{restart_sequence}{question}"
            
    else:
        prompt = f"{explicit_prompt}{restart_sequence}{question}"

    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        temperature=0,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )

    print(f"{response['choices'][0]['text'].encode().decode()}\n\n\n")

    return prompt,response#, res['page'][0]


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def get_embedding(text: str, engine="text-search-davinci-doc-001") -> list[float]:

    # replace newlines, which can negatively affect performance.
    text = text.replace("\n", " ")

    return openai.Embedding.create(input=[text], engine= os.getenv('OPENAI_EMBEDDINGS_ENGINE_DOC', 'text-search-davinci-doc-001'))["data"][0]["embedding"]


def chunk_and_embed(text: str, engine="text-search-davinci-doc-001"):
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

    full_data = {
        "text": text,
        "davinci_search": None
    }

    lenght = len(tokenizer(text)['input_ids'])
    while lenght > 2046:
        text = ".".join(text.split('.')[:-2])
        lenght = len(tokenizer(text)['input_ids'])

    full_data['davinci_search'] = get_embedding(text)

    return full_data


def get_completion(prompt="", max_tokens=400, model="text-davinci-002"):
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
