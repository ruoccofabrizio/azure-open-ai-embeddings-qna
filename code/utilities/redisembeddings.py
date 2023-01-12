from redis import Redis
from redis.commands.search.query import Query
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.field import VectorField, TagField, TextField
import typing as t
import numpy as np
import pandas as pd
from pprint import pprint
import uuid
import os

# Redis configuration
DIM = 12288
VECT_NUMBER = 3155

def create_index(redis_conn: Redis, index_name="embeddings-index", prefix = "embedding",number_of_vectors = VECT_NUMBER, distance_metric:str="COSINE"):
    text = TextField(name="text")
    embeddings = VectorField("embeddings",
                "HNSW", {
                    "TYPE": "FLOAT32",
                    "DIM": DIM,
                    "DISTANCE_METRIC": distance_metric,
                    "INITIAL_CAP": number_of_vectors,
                })
    # Create index
    redis_conn.ft(index_name).create_index(
        fields = [text, embeddings],
        definition = IndexDefinition(prefix=[prefix], index_type=IndexType.HASH)
    )

def execute_query(np_vector:np.array, return_fields: list=[], search_type: str="KNN", number_of_results: int=20, vector_field_name: str="embeddings"):
    base_query = f'*=>[{search_type} {number_of_results} @{vector_field_name} $vec_param AS vector_score]'
    query = Query(base_query)\
        .sort_by("vector_score")\
        .paging(0, number_of_results)\
        .return_fields(*return_fields)\
        .dialect(2)
    
    params_dict = {"vec_param": np_vector.astype(dtype=np.float32).tobytes()}

    results = redis_conn.ft(index_name).search(query, params_dict)
    return pd.DataFrame(list(map(lambda x: {'id' : x.id, 'text': x.text, 'vector_score': x.vector_score}, results.docs)))

def get_documents(number_of_results: int=VECT_NUMBER):
    base_query = f'*'
    return_fields = ['id','text']
    query = Query(base_query)\
        .paging(0, number_of_results)\
        .return_fields(*return_fields)\
        .dialect(2)
    results = redis_conn.ft(index_name).search(query)
    if results.docs:
        return pd.DataFrame(list(map(lambda x: {'id' : x.id, 'text': x.text}, results.docs))).sort_values(by='id')
    else:
        return pd.DataFrame()

def set_document(elem):
    index = str(uuid.uuid4())
    redis_conn.hset(
        f"embedding:{index}",
        mapping={
            "text": elem['text'],
            "embeddings": np.array(elem['davinci_search']).astype(dtype=np.float32).tobytes()
        }
    )

def delete_document(index):
    redis_conn.delete(f"{index}")

# Connect to the Redis server
redis_conn = Redis(host= os.environ.get('REDIS_ADDRESS','localhost'), port=6379, password=os.environ.get('REDIS_PASSWORD',None)) #api for Docker localhost for local execution

# Check if Redis index exists
index_name = "embeddings-index"
try:
    if redis_conn.ft(index_name).info():
        print("Index exists")
except:
    print("Index does not exist")
    print("Creating index")
    # Create index 
    create_index(redis_conn)