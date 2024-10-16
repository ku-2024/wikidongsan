import os
from functools import lru_cache
from langchain_upstage import ChatUpstage, UpstageEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter
from langchain import hub
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain.retrievers import ContextualCompressionRetriever
from langchain.docstore.document import Document

class RAGSystem:
    def __init__(self, api_key):
        os.environ["UPSTAGE_API_KEY"] = api_key
        self.setup_rag_system()
        self.vectorstore_cache = {}

    def setup_rag_system(self):
        self.prompt = hub.pull("rlm/rag-prompt")
        self.chat = ChatUpstage()
        self.embedding_model = UpstageEmbeddings(model="solar-embedding-1-large")
        
        rerank_model = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-v2-m3")
        self.compressor = CrossEncoderReranker(model=rerank_model, top_n=2)

    def create_retriever(self, document, apt_code):
        if document is None:
            raise ValueError("Document content cannot be None")
        
        if apt_code in self.vectorstore_cache:
            retriever = self.vectorstore_cache[apt_code].as_retriever(search_kwargs={"k": 5})
        else:
            doc = Document(page_content=document)
            text_splitter = CharacterTextSplitter(separator='\n', chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.split_documents([doc])
            
            vectorstore = FAISS.from_documents(splits, self.embedding_model)
            self.vectorstore_cache[apt_code] = vectorstore
            retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        
        return ContextualCompressionRetriever(
            base_compressor=self.compressor, base_retriever=retriever
        )

    @staticmethod
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    @lru_cache(maxsize=100)
    def get_response(self, input_text, document, apt_code):
        compression_retriever = self.create_retriever(document, apt_code)
        rag_chain = (
            {"context": compression_retriever | self.format_docs, "question": RunnablePassthrough()}
            | self.prompt
            | self.chat
            | StrOutputParser()
        )
        return rag_chain.invoke(input_text)