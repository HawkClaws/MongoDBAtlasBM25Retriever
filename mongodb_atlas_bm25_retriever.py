from typing import Any, List, Optional, cast
import os
import json
from llama_index.retrievers import BaseRetriever
from llama_index.schema import NodeWithScore,TextNode
from llama_index import QueryBundle

class MongoDBAtlasBM25Retriever(BaseRetriever):
    def __init__(
        self,
        mongodb_client: Optional[Any] = None,
        db_name: str = "default_db",
        collection_name: str = "default_collection",
        index_name: str = "default",
        text_key: str = "text",
        similarity_top_k: int = 5,
    ) -> None:
        """Initialize the vector store.

        Args:
            mongodb_client: A MongoDB client.
            db_name: A MongoDB database name.
            collection_name: A MongoDB collection name.
            index_name: A MongoDB Atlas Vector Search index name.
            text_key: A MongoDB field that will contain the text for each document.
        """
        import_err_msg = "`pymongo` package not found, please run `pip install pymongo`"
        try:
            from importlib.metadata import version
            from pymongo import MongoClient
            from pymongo.driver_info import DriverInfo
        except ImportError:
            raise ImportError(import_err_msg)

        if mongodb_client is not None:
            self._mongodb_client = cast(MongoClient, mongodb_client)
        else:
            if "MONGO_URI" not in os.environ:
                raise ValueError(
                    "Must specify MONGO_URI via env variable "
                    "if not directly passing in client."
                )
            self._mongodb_client = MongoClient(
                os.environ["MONGO_URI"],
                driver=DriverInfo(name="llama-index", version=version("llama-index")),
            )
        self._db = self._mongodb_client[db_name]
        self._collection = self._db[collection_name]
        self._index_name = index_name
        self._text_key = text_key
        self._similarity_top_k = similarity_top_k

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Retrieve nodes given query."""
        query = query_bundle.query_str
        print(self._collection.count_documents({}))

        # BM25検索を実行
        pipeline = [
            {
                "$search": {
                    "index": self._index_name,
                    "text": {"query": query, "path": self._text_key},
                }
            },
            {"$addFields": {"score": {"$meta": "searchScore"}}},
            {"$sort": {"score": -1}},
            {"$limit": self._similarity_top_k},
        ]

        results = list(self._collection.aggregate(pipeline))

        retrieve_nodes = []
        for result in results[:self._similarity_top_k]:
            doc = self._collection.find_one({"_id": result["_id"]})
            node = doc[self._text_key]
            node_content = json.loads(doc.get("metadata",{}).get("_node_content","{}"))
            node = TextNode(
                    text=doc["text"],
                    id_=doc["id"],
                    metadata=doc.get("metadata",{}),
                    start_char_idx=node_content.get("start_char_idx", None),
                    end_char_idx=node_content.get("end_char_idx", None),
                    relationships=node_content.get("relationships", None),
                )
            node_with_score = NodeWithScore(node=node, score=result["score"])
            retrieve_nodes.append(node_with_score)

        return retrieve_nodes
