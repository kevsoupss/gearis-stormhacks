import os
import time
import threading
import logging
import csv
from uuid import uuid4
import PyPDF2
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

logger = logging.getLogger("chroma_watcher")

load_dotenv()

class ChromaService:
    instance = None
    RAW_PATH = "files"
    DB_PATH = ".vector_db"
    COLLECTION_NAME = "GIRIS_FILES"

    @staticmethod
    def get_instance():
        if not ChromaService.instance:
            ChromaService.instance = ChromaService()
        return ChromaService.instance

    def __init__(self):
        self.collection_name = ChromaService.COLLECTION_NAME

        # --- Initialize embeddings and vector store ---
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        self.vector_store = Chroma(
            collection_name=ChromaService.COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=ChromaService.DB_PATH,
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,   # number of characters per chunk
            chunk_overlap=200  # overlap between chunks to preserve context
        )

        # --- Watcher state ---
        self._observer = None
        self._reindex_pending = {}
        self._reindex_lock = threading.Lock()

        # Ensure watch folder exists
        if not os.path.exists(ChromaService.RAW_PATH):
            os.makedirs(ChromaService.RAW_PATH)
            logger.info(f"Created watch directory: {ChromaService.RAW_PATH}")

    # ---------------- Watcher Event Handler ----------------
    class _ReindexHandler(FileSystemEventHandler):
        def __init__(self, service):
            self.service = service

        def on_created(self, event):
            if not event.is_directory:
                self.service._schedule_reindex(event.src_path)

        def on_modified(self, event):
            if not event.is_directory:
                self.service._schedule_reindex(event.src_path)

        def on_deleted(self, event):
            if not event.is_directory:
                self.service._delete_file(event.src_path)

    # ---------------- Internal Methods ----------------
    def _schedule_reindex(self, path, delay=1):
        abs_path = os.path.abspath(path)
        with self._reindex_lock:
            if abs_path in self._reindex_pending:
                return
            self._reindex_pending[abs_path] = True

        def delayed():
            time.sleep(delay)
            self.reindex_file(abs_path)
            with self._reindex_lock:
                self._reindex_pending.pop(abs_path, None)

        threading.Thread(target=delayed, daemon=True).start()

    def _delete_file(self, path):
        abs_path = os.path.abspath(path)
        self.vector_store.delete(where={"source": abs_path})
        logger.info(f"Deleted file from vector store: {abs_path}")

    def chunk_document(self, text, metadata):
        texts = self.text_splitter.split_text(text)
        logger.info(f"Chunked {metadata['source']} into {len(texts)} chunks!")
        return [Document(page_content=t, metadata=metadata) for t in texts]

    # ---------------- Public Methods ----------------

    def retrieve(self, query):
        return self.vector_store.similarity_search(query)

    def reindex_file(self, path):
        """Reindex a single file into Chroma"""
        try:
            text = self.read_content(path)
            if not text.strip():
                logger.info(f"No text extracted from {path}, skipping.")
                return
            # Delete old vectors for this file
            self.vector_store.delete(where={"source": path})

            # Create a Document
            # doc = Document(page_content=text, metadata={"source": path})
            document_chunks = self.chunk_document(text, metadata={"source": path})

            # Add to vector store
            uuids = [str(uuid4()) for i in range(len(document_chunks))]
            self.vector_store.add_documents(document_chunks, ids=uuids)
            logger.info(f"Reindexed file: {path}")
        except Exception as e:
            logger.exception(f"Failed to reindex {path}: {e}")

    def read_content(self, path):
        ext = os.path.splitext(path)[1].lower()
        if ext in {".txt", ".md"}:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        elif ext == ".pdf":
            text = ""
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text
        elif ext == ".csv":
            text = ""
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    text += " ".join(row) + "\n"
            return text
        else:
            return ""  # unsupported type

    def start(self):
        """Start the file watcher in background"""
        handler = self._ReindexHandler(self)
        self._observer = Observer()
        self._observer.schedule(handler, ChromaService.RAW_PATH, recursive=True)
        self._observer.start()
        logger.info(f"Started watcher on: {ChromaService.RAW_PATH}")

    def stop(self):
        """Stop the watcher"""
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None
            logger.info("Stopped watcher.")

    # @staticmethod
    # def get_tool():
    #     @tool
    #     def rag(question: str):
    #         """
    #         Searches a folder for relevant results to the given question
            
    #         Args:
    #             question: the user's question
    #         """
    #         prompt = """
    #     You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
    #     Question: {question} 
    #     Context: {context} 
    #     Answer:"""
    #         llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    #         chroma = ChromaService.get_instance()
    #         docs = chroma.retrieve(question)
    #         message = prompt.format(question=question, context="\n\n".join(doc.page_content for doc in docs))
    #         result = llm.invoke(message)
    #         return result.content
        
    #     return [rag]

if __name__ == "__main__":

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Get service instance
    service = ChromaService.get_instance()

    # Start the file watcher
    service.start()

    # # Reindex all existing files in RAW_PATH
    for root, _, files in os.walk(ChromaService.RAW_PATH):
        for fname in files:
            file_path = os.path.join(root, fname)
            logging.info(f"Reindexing existing file: {file_path}")
            service.reindex_file(file_path)

    # logging.info("Initial indexing complete. You can now query the vector store.")

    # Simple interactive RAG test
    try:
        while True:
            query = input("\nEnter a query (or 'exit' to quit): ").strip()
            if query.lower() == "exit":
                break

            results = service.retrieve(query)
            if not results:
                print("No relevant documents found.")
            else:
                print("\nTop results:")
                for i, doc in enumerate(results[:5], start=1):
                    print(f"[{i}] Source: {doc.metadata.get('source')}")
                    print(doc.page_content[:300] + ("..." if len(doc.page_content) > 300 else ""))
                    print("-" * 50)
            prompt = """
        You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
        Question: {question} 
        Context: {context} 
        Answer:"""
            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
            chroma = ChromaService.get_instance()
            docs = chroma.retrieve(query)
            message = prompt.format(question=query, context="\n\n".join(doc.page_content for doc in docs))
            result = llm.invoke(message)
            print(result)
    except KeyboardInterrupt:
        pass
    finally:
        service.stop()
        logging.info("Exiting.")
#     prompt = """
# You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
# Question: {question} 
# Context: {context} 
# Answer:"""
#     question = "when does toby graduate"
#     llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
#     chroma = ChromaService.get_instance()
#     docs = chroma.retrieve(question)
#     message = prompt.format(question=question, context="\n\n".join(doc.page_content for doc in docs))
#     result = llm.invoke(message)
#     print(result)
