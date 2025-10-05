import logging
from storage.main import ChromaService
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

class RagTool:
    prompt = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:"""
    @staticmethod
    def get_tool():
        @tool
        def rag(question: str):
            """
            Searches through the user's uploaded files for relevant context to the given question
            
            Args:
                question: the user's question
            """
            try:

                llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
                chroma = ChromaService.get_instance()
                docs = chroma.retrieve(question)
                message = RagTool.prompt.format(question=question, context="\n\n".join(doc.page_content for doc in docs))
                result = llm.invoke(message)
                logging.info(result.content)
                return result.content
            except Exception as e:
                logging.info(str(e))
                return f"An error occurred. {str(e)}"
        
        return [rag]
    
if __name__ == "__main__":
    question = "when does toby graduate?"
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    chroma = ChromaService.get_instance()
    docs = chroma.retrieve(question)
    message = RagTool.prompt.format(question=question, context="\n\n".join(doc.page_content for doc in docs))
    result = llm.invoke(message)
    print(result)
