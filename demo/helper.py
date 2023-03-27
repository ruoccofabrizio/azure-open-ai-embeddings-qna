import os
import openai
from dotenv import load_dotenv
from openai.embeddings_utils import get_embedding
from tenacity import retry, wait_random_exponential, stop_after_attempt
import pandas as pd
import numpy as np
from redis.commands.search.query import Query
from redis import Redis

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base =  os.getenv("OPENAI_API_BASE")
openai.api_type = 'azure'
openai.api_version = '2022-12-01'
completion_model = os.getenv("OPENAI_ENGINES").split(',')[0]
embedding_model = os.getenv("OPENAI_EMBEDDINGS_ENGINE_DOC")
question_prompt = os.getenv("QUESTION_PROMPT").replace(r'\n', '\n')
number_of_embeddings_for_qna = int(os.getenv("NUMBER_OF_EMBEDDINGS_FOR_QNA", 1))

redis_conn = Redis(host=os.getenv('REDIS_ADDRESS'), port=int(os.environ.get('REDIS_PORT','6379')), password=os.getenv('REDIS_PASSWORD'))
index_name = "embeddings-index"
prompt_index_name = "prompt-index"


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def get_embedding(text) -> list[float]:
    text = text.replace("\n", " ")
    return openai.Embedding.create(input=text, engine=embedding_model)["data"][0]["embedding"]


def find_matching_vectors_in_redis(np_vector:np.array, return_fields: list=[], search_type: str="KNN", number_of_results: int=20, vector_field_name: str="embeddings"):
    base_query = f'*=>[{search_type} {number_of_results} @{vector_field_name} $vec_param AS vector_score]'
    query = Query(base_query)\
        .sort_by("vector_score")\
        .paging(0, number_of_results)\
        .return_fields(*return_fields)\
        .dialect(2)
    params_dict = {"vec_param": np_vector.astype(dtype=np.float32).tobytes()}
    results = redis_conn.ft(index_name).search(query, params_dict)
    return pd.DataFrame(list(map(lambda x: {'id' : x.id, 'text': x.text, 'filename': x.filename, 'vector_score': x.vector_score}, results.docs)))


def search_semantic_redis(search_query, pprint=True):
    embedding = get_embedding(search_query)
    res = find_matching_vectors_in_redis(np.array(embedding))
    if pprint:
        for r in res:
            print(r[:200])
            print()
    return res.reset_index()


def get_semantic_answer(question):
    # question += "\n"
    res = search_semantic_redis(question, pprint=False)

    if len(res) == 0:
        return None, "No vectors matched, try a different question."


    res_text = "\n".join(res['text'][0:number_of_embeddings_for_qna])
    prompt = question_prompt.replace("_QUESTION_", question)
    prompt = f"{res_text}\n\n{prompt}"

    response = openai.Completion.create(
        engine=completion_model,
        prompt=prompt,
        temperature=0.7,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    print(prompt)
    response = response['choices'][0]['text'].strip()
    print(f"{response}\n\n\n")
    return response, prompt