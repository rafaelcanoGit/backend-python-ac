# from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.memory import VectorStoreRetrieverMemory
from langchain.schema import HumanMessage
import os

# ✅ 1. Embeddings + Vectorstore persistente
embedding_model = OpenAIEmbeddings()
chroma_store = Chroma(
    collection_name="long_term_memory",
    embedding_function=embedding_model,
    persist_directory="./chroma_db",  # 🧠 Se guarda en disco
)

# ✅ 2. Recuperador con filtro por user_id.
retriever = chroma_store.as_retriever(search_kwargs={"k": 3})

# ✅ 3. Memoria personalizada con metadatos
memory = VectorStoreRetrieverMemory(
    retriever=retriever, memory_key="chat_history", input_key="input"
)


# ✅ 4. Guardar recuerdos por paciente (user_id)
def save_user_message(user_id: str, message: str):
    chroma_store.add_texts(texts=[message], metadatas=[{"user_id": user_id}])


# ✅ 5. Recuperar contexto relevante por paciente
def get_relevant_memories(user_id: str, question: str):
    return chroma_store.similarity_search(
        question,
        k=3,
        filter={"user_id": user_id},  # 🔎 Importante: filtrar por paciente
    )


# ✅ 6. LLM para la respuesta
llm = ChatOpenAI(model="gpt-4o", temperature=0.4)

# ✅ 7. Interacción simulada
user_id = "patient_123"
input_message = "¿Puedo tomar amoxicilina si soy alérgico a la penicilina?"

# Guardamos algún mensaje previo
save_user_message(user_id, "Soy alérgico a la penicilina.")

# Recuperamos recuerdos relevantes
memories = get_relevant_memories(user_id, input_message)

# Formateamos los recuerdos
context = "\n".join([doc.page_content for doc in memories])

# Construimos el prompt completo
full_prompt = f"""Paciente: {input_message}
Contexto clínico:
{context}

Asistente:"""

# Generamos respuesta
response = llm([HumanMessage(content=full_prompt)])
print(response.content)


# ======================================

# main.py
# Implementación paso a paso de un chatbot con memorias a largo plazo
# usando Chroma, OpenAIEmbeddings y LangGraph

# main.py
# Implementación paso a paso de un chatbot con memorias a largo plazo
# usando Chroma, OpenAIEmbeddings y LangGraph, buscando por user_phone

import os
import uuid
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

# 1. Carga variables de entorno
load_dotenv()

# 2. Configuración de Embeddings + Chroma (persistente)
PERSIST_DIR = os.getenv("PERSIST_DIRECTORY", "./chroma_data")
embeddings = OpenAIEmbeddings()
vectorstore = Chroma(
    collection_name="patient_assistant",
    persist_directory=PERSIST_DIR,
    embedding_function=embeddings,
)


# 3. Herramientas de memorias a largo plazo (save & recall) usando user_phone
def get_user_phone(config: RunnableConfig) -> str:
    return config["configurable"]["user_phone"]


@tool
def save_longterm_memory(message: str, config: RunnableConfig) -> str:
    """Guarda un recuerdo en Chroma con metadata user_phone"""
    user_phone = get_user_phone(config)
    doc = Document(
        page_content=message, id=str(uuid.uuid4()), metadata={"user_phone": user_phone}
    )
    vectorstore.add_documents([doc])
    return f"Memoria guardada para usuario con teléfono {user_phone}."


@tool
def recall_longterm_memories(message: str, config: RunnableConfig) -> list[str]:
    """Recupera los k recuerdos más relevantes para user_phone"""
    user_phone = get_user_phone(config)
    docs = vectorstore.similarity_search(
        message, k=3, filter={"user_phone": user_phone}
    )
    return [d.page_content for d in docs]


# 4. Modelo de lenguaje para respuestas
llm = ChatOpenAI(model="gpt-4o", temperature=0.4)


# 5. Estado para LangGraph
class ChatState(dict):
    """Estado de conversación para LangGraph"""

    pass


# 6. Nodos LangGraph
# Nodo: Recuperar memorias relevantes
def retrieve_memories(state: ChatState) -> ChatState:
    # Recuperar memorias semánticas para este input: message
    memories = recall_longterm_memories.invoke(
        state["input"], config={"configurable": {"user_phone": state["user_phone"]}}
    )
    state["memories"] = memories
    return state


# Nodo: Generar respuesta incluyendo memorias
def generate_response(state: ChatState) -> ChatState:
    context = "\n".join(f"- {m}" for m in state.get("memories", []))
    prompt = (
        f"Memorias relevantes:\n{context}\n\nPaciente: {state['input']}\nAsistente:"
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    state["response"] = response.content
    return state


# Nodo: Guardar la nueva interacción como memoria
def save_memory(state: ChatState) -> ChatState:
    # Guardar input+respuesta como nuevos recuerdos
    save_longterm_memory.invoke(
        state["input"], config={"configurable": {"user_phone": state["user_phone"]}}
    )
    save_longterm_memory.invoke(
        state["response"], config={"configurable": {"user_phone": state["user_phone"]}}
    )
    return state


# 7. Construcción del grafo
builder = StateGraph(ChatState)
builder.add_node("recuperar_memorias", retrieve_memories)
builder.add_node("generar_respuesta", generate_response)
builder.add_node("guardar_memoria", save_memory)
builder.set_entry_point("recuperar_memorias")
builder.add_edge("recuperar_memorias", "generar_respuesta")
builder.add_edge("generar_respuesta", "guardar_memoria")
builder.add_edge("guardar_memoria", END)
graph = builder.compile()



# 8. Ejemplo de interacción con un paciente usando user_phone
if __name__ == "__main__":
    user_phone = "+573001234567"

    # Simular que paciente ya dijo algo antes
    save_longterm_memory.invoke(
        "Tengo migrañas crónicas desde hace 2 años.",
        config={"configurable": {"user_phone": user_phone}},
    )

    # Nueva consulta del paciente
    input_text = "Últimamente me duele mucho la cabeza cuando hay mucho ruido."
    state = {"user_phone": user_phone, "input": input_text}
    result = graph.invoke(state)

    print("Asistente:", result["response"])
