import tkinter as tk
from tkinter import scrolledtext
from langchain.chains import create_retrieval_chain
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

import os

# Setting up OpenAI API Key 
os.environ["OPENAI_API_KEY"] = "OPENAI_API_KEY"

# Loading  Research Paper (External Source of Knowledge)
loader = PyPDFLoader("recent_advances_alzheimer_disease.pdf")
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter()
text = text_splitter.split_documents(documents)

# Embedding Model for RAG
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5", encode_kwargs={"normalize_embeddings": True})

# Creating Vector Database
vectorstore = FAISS.from_documents(text, embeddings)

retriever = vectorstore.as_retriever()

# Loadimng LLM Model
llm = ChatOpenAI(model_name="gpt-3.5-turbo")

# Prompt Template for Question-Answering
template = """You are an assistant for question-answering tasks.
Use the provided context only to answer the following question:

<context>
{context}
</context>

Question: {input}
"""
prompt = ChatPromptTemplate.from_template(template)
doc_chain = create_stuff_documents_chain(llm, prompt)


chain = create_retrieval_chain(retriever, doc_chain)

# Function for user question and retrieve answer
def ask_question():
    user_question = entry.get()
    if user_question:
        response = chain.invoke({"input": user_question})
        answer = response.get('answer', "No answer found.")
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, answer)

# Creating GUI window
window = tk.Tk()
window.title("Question Answering System")

# Prompt in GUI
tk.Label(window, text="Enter your question:").pack(pady=5)
entry = tk.Entry(window, width=80)
entry.pack(padx=10, pady=5)

# Ask button for User
ask_button = tk.Button(window, text="Ask", command=ask_question)
ask_button.pack(pady=5)

# Result text box for Answer generated by LLM
result_text = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=100, height=20)
result_text.pack(padx=10, pady=10)


window.mainloop()
