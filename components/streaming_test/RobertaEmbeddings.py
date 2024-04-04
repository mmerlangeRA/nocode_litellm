import numpy as np

from typing import List
from langchain.embeddings.base import Embeddings
from transformers import AutoTokenizer
from sentence_transformers import SentenceTransformer
from Singleton import Singleton


class RobertaEmbeddings(Embeddings, metaclass=Singleton):
    def __init__(self):
        self.model = SentenceTransformer('sentence-transformers/all-roberta-large-v1')
        self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-roberta-large-v1')
        self.__dimension = 1024

    def get_dimension(self):
        return self.__dimension

    def _embedding_func(self, text: str) -> List[float]:
        text = text.replace("\n", " ")
        embeddings = self.model.encode([text])
        return embeddings[0]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts)
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        embeddings = self._embedding_func(text)
        return embeddings

    def embed_documents_with_safe_length(self, sentences: List[str], max_len=128):
        embeddings = []
        for sentence in sentences:
            encoded_sentence = self.tokenizer.encode(sentence)
            if len(encoded_sentence) > max_len:
                # Divide the encoded sentence into chunks
                chunks = [encoded_sentence[i:i + max_len] for i in
                          range(0, len(encoded_sentence), max_len)]  # Get length of each chunks
                chunk_lens = [len(chunk) for chunk in chunks]  # Decode the chunks
                decoded_sentences = self.tokenizer.batch_decode(chunks,
                                                                skip_special_tokens=True)
                chunk_embeddings = self.model.encode(decoded_sentences)
                chunk_embeddings = np.average(chunk_embeddings, axis=0, weights=chunk_lens)
                chunk_embeddings = chunk_embeddings / np.linalg.norm(chunk_embeddings)
                embeddings.append(chunk_embeddings)
            else:
                embeddings.append(self.model.encode(sentence))
        return embeddings


if __name__ == '__main__':
    embeddings = RobertaEmbeddings()
    vectors = embeddings.embed_query("hey this is a test text")
    print(vectors)
    print()
    vectors = embeddings.embed_documents_with_safe_length(["hey this is a test text", "hey how are you"])
    print(vectors)