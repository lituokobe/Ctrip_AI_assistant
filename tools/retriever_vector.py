import re
from pathlib import Path

import numpy as np
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings

# get the absolute path of the project
basic_dir = Path(__file__).resolve().parent.parent

# read FAQ
faq_text = None
with open(f'{basic_dir}/order_faq.md', encoding='utf8') as f:
    faq_text = f.read()
# split FAQ to multiple docs
docs = [{"page_content": txt} for txt in re.split(r"(?=\n##)", faq_text)]

embeddings_model = OpenAIEmbeddings()

class VectorStoreRetriever:
    def __init__(self, docs: list, vectors: list):
        self._arr = np.array(vectors)
        self._docs = docs

    @classmethod #@classmethod decorator is used to define a method that operates on the class itself rather than on instances of the class.
    def from_docs(cls, docs):
        # generate embedded vectors from docs
        embeddings = embeddings_model.embed_documents([doc["page_content"] for doc in docs])
        vectors = embeddings
        return cls(docs, vectors)

    def query(self, query: str, k: int = 5) -> list[dict]:
        # generated embedded vectors from query
        embed = embeddings_model.embed_query(query)
        # calculate similarity score between query vector and doc vectors
        scores = np.array(embed) @ self._arr.T
        # obtain the k docs with the highest similarity scores
        top_k_idx = np.argpartition(scores, -k)[-k:]
        top_k_idx_sorted = top_k_idx[np.argsort(-scores[top_k_idx])]
        # return k docs with highest similarity scores and the scores
        return [
            {**self._docs[idx], "similarity": scores[idx]} for idx in top_k_idx_sorted
        ]


# Create an instance
retriever = VectorStoreRetriever.from_docs(docs)

# Create a tool function, for searching arline policies
@tool
def lookup_policy(query: str) -> str:
    """check airline policy and check if a given option is allowed.
    Use this function before change flight or any other database change.
    """
    # check the k docs with highest similarity scores.
    docs = retriever.query(query, k=2)
    # return the docs
    return "\n\n".join([doc["page_content"] for doc in docs])


if __name__ == '__main__':  # testing
    print(lookup_policy('How to get refund for the flight ticket?'))
