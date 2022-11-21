import pandas as pd
import numpy as np
from openai.embeddings_utils import get_embedding, cosine_similarity
import openai
import os
from tenacity import retry, wait_random_exponential, stop_after_attempt
from transformers import GPT2Tokenizer

def initialize(embeddings_path=r'embeddings_text.csv', engine='babbage'):
   
    openai.api_type = "azure"
    openai.api_base = os.getenv('api_base')
    openai.api_version = "2022-06-01-preview"
    openai.api_key = os.getenv("api_key")

    # Read or compute embeddings with model
    df = pd.read_csv(embeddings_path)
    if f'{engine}_search' in df:
        # Reading embedding
        df[f'{engine}_search'] = df[f'{engine}_search'].apply(eval).apply(np.array)
    return df

# Semantically search using the computed embeddings
def search_semantic(df, search_query, n=3, pprint=True, engine='babbage'):
    embedding = get_embedding(search_query, engine=f'text-search-{engine}-query-001')
    df['similarities'] = df[f'{engine}_search'].apply(lambda x: cosine_similarity(x, embedding))

    res = df.sort_values('similarities', ascending=False).head(n)
    if pprint:
        for r in res:
            print(r[:200])
            print()
    return res.reset_index()

# Return a semantically aware response using the Completion endpoint
def get_semantic_answer(df, question, max_tokens=400, explicit_prompt="", model="text-davinci-002", engine='babbage'):

    start_sequence = "\nA:"
    restart_sequence = "\n\nQ: "

    if explicit_prompt == "":
        res = search_semantic(df, question, n=3, pprint=False, engine=engine)
        prompt = f"{res['text'][0][:-1]}{restart_sequence}{question}"

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
        stop=["\\n"]
    )

    print(f"{response['choices'][0]['text'].encode().decode()}\n\n\n")

    return prompt,response#, res['page'][0]


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def get_embedding(text: str, engine="text-search-davinci-doc-001") -> list[float]:

    # replace newlines, which can negatively affect performance.
    text = text.replace("\n", " ")

    return openai.Embedding.create(input=[text], engine=engine)["data"][0]["embedding"]


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