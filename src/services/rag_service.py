"""Сервис для RAG системы."""

import json
from pathlib import Path
from typing import List

import pymupdf4llm
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter, RecursiveJsonSplitter

from config import (
    OPENAI_BASE_URL, OPENAI_API_KEY, MODEL_NAME,
    EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP
)


class RAGService:
    """Сервис для инициализации и работы с RAG системой."""
    
    def __init__(self):
        """Инициализируем сервис без загрузки данных."""
        self.chain = None
    
    def initialize(self, file_paths: List[str]) -> None:
        """
        Инициализируем RAG систему с заданными файлами.
        
        Args:
            file_paths: Список путей к файлам для обработки.
        """
        documents = self._load_documents(file_paths)
        
        # Создаем эмбеддинги
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"}  # Убираем cuda для совместимости
        )
        
        # Создаем векторную базу
        vector_store = FAISS.from_documents(documents, embeddings)
        faiss_retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={'k': 6}
        )
        
        # BM25 ретривер
        bm25_retriever = BM25Retriever.from_documents(documents)
        bm25_retriever.k = 2
        
        # Комбинированный ретривер
        ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, faiss_retriever],
            weights=[0.2, 0.8]
        )
        
        # LLM
        llm = ChatOpenAI(
            model=MODEL_NAME,
            base_url=OPENAI_BASE_URL,
            api_key=OPENAI_API_KEY,
            temperature=0.1
        )
        
        # Промпт
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "Ты консультант по образовательным программам ИТМО. "
                "Отвечай кратко на основе контекста.\n\nКонтекст: {context}"
            ),
            ("human", "{input}"),
        ])
        
        # Создаем цепочку
        doc_chain = create_stuff_documents_chain(llm, prompt)
        self.chain = create_retrieval_chain(ensemble_retriever, doc_chain)
    
    def get_answer(self, question: str) -> str:
        """
        Получаем ответ от RAG системы.
        
        Args:
            question: Вопрос пользователя.
            
        Returns:
            Ответ системы.
        """
        if not self.chain:
            return "RAG система не инициализирована."
        
        result = self.chain.invoke({"input": question})
        return result["answer"]
    
    def _load_documents(self, file_paths: List[str]) -> List[Document]:
        """
        Загружаем документы из файлов.
        
        Args:
            file_paths: Список путей к файлам.
            
        Returns:
            Список документов для векторизации.
        """
        documents = []
        
        for file_path in file_paths:
            path = Path(file_path)
            if not path.exists():
                continue
                
            if path.suffix.lower() == '.json':
                documents.extend(self._load_json(path))
            elif path.suffix.lower() == '.pdf':
                documents.extend(self._load_pdf(path))
        
        return documents
    
    def _load_json(self, file_path: Path) -> List[Document]:
        """
        Загружаем JSON файл.
        
        Args:
            file_path: Путь к JSON файлу.
            
        Returns:
            Список документов.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        splitter = RecursiveJsonSplitter(max_chunk_size=1000)
        json_chunks = splitter.split_json(json_data=data)
        if file_path.name == 'ai_product.json':
            program_name = 'AI Product'
        else:
            program_name = 'AI'
        return splitter.create_documents(
            texts=json_chunks,
            metadatas=[{"source": str(file_path), "About": f"Description of the training area, important dates and entrance tests for {program_name}"} for _ in json_chunks]
        )
    
    def _load_pdf(self, file_path: Path) -> List[Document]:
        """
        Загружаем PDF файл.
        
        Args:
            file_path: Путь к PDF файлу.
            
        Returns:
            Список документов.
        """
        pages = pymupdf4llm.to_markdown(str(file_path), page_chunks=True)
        if file_path.name == 'ai_product_itmo_plan.pdf':
            program_name = 'AI Product'
        else:
            program_name = 'AI'
        docs = [
            Document(
                page["text"],
                metadata={"page": page.get("page", i), "source": file_path.name, "About": f"The curriculum of the program {program_name}"}
            )
            for i, page in enumerate(pages)
        ]
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        return splitter.split_documents(docs) 