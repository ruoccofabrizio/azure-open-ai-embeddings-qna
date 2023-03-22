import os
from redis import Redis
from redis.commands.search.query import Query
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.field import VectorField, TagField, TextField
from dotenv import load_dotenv
load_dotenv()

index_name = "embeddings-index"
prompt_index_name = "prompt-index"

redis_conn = Redis(host= os.environ.get('REDIS_ADDRESS','localhost'), port=6379, password=os.environ.get('REDIS_PASSWORD',None)) #api for Docker localhost for local execution
print('connecting..')
try:
    print(redis_conn.ft(index_name).info())
except Exception as e: print(e)
