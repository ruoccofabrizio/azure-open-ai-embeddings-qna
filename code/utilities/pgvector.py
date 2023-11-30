import json
import logging
import uuid
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Tuple

# from langchain.vectorstores.pgvector import BaseModel, CollectionStore, EmbeddingStore, QueryResult, DistanceStrategy, PGVector
from langchain.vectorstores.pgvector import DistanceStrategy, PGVector
from langchain.docstore.document import Document
from langchain.embeddings.base import Embeddings
from langchain.vectorstores.base import VectorStore

import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy import engine,MetaData, Table


logger = logging.getLogger()
DEFAULT_DISTANCE_STRATEGY = DistanceStrategy.EUCLIDEAN

class PGVectorExtended(PGVector):
    def __init__(
        self,
        connection_string: str,
        embedding_function: Embeddings,
        collection_name: str ,
        collection_metadata: Optional[dict] = None,
        distance_strategy: DistanceStrategy = DEFAULT_DISTANCE_STRATEGY,
        pre_delete_collection: bool = False,
        logger: Optional[logging.Logger]= None,
        connection: Optional[sqlalchemy.engine.Connection] = None,
    ):
        super().__init__(connection_string, embedding_function, collection_name, collection_metadata, distance_strategy, pre_delete_collection, logger)
        self.connection = super().connect()


    
    def delete_keys(
        self,
        ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        """Delete vectors by custom_id(this column store the embedding key in this case).
     
        Args:
            ids: List of ids to delete.
        """
 
        # self._conn = super().connect()

        with Session(self.connection) as session:
            table_name = "langchain_pg_embedding"
            metadata = MetaData()
            table = Table(table_name, metadata, autoload_with=self.connection)
            delete_statement = table.delete().where(table.c.custom_id.in_(ids))
            session.execute(delete_statement)
            session.commit()