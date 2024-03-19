# MongoDBAtlasBM25Retriever

## これはなに？
  
LlamaIndexで利用できる MongoDBAtlasのBM25 Retrieverです。  
llamaindex0.9.36を利用して作成したため、必要に応じてllamaindexのimportを調整してください  。

## How to use

[MongoDBAtlasVectorSearch](https://docs.llamaindex.ai/en/stable/examples/vector_stores/MongoDBAtlasVectorSearch.html) を参考に作ったので、だいたい同じです。  
そちらを参照してください。

ただし、`MongoDBAtlasVectorSearch`はIndexなのに対し、`MongoDBAtlasBM25Retriever`はRetrieverです