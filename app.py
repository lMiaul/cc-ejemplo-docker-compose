import streamlit as st
import os
from datetime import datetime
from pymongo import MongoClient
from google import genai

# 1. Configuración de clientes (Gemini y MongoDB)
ai_client = genai.Client() # Usa GEMINI_API_KEY del entorno

@st.cache_resource
def get_mongo_collection():
    # Nos conectamos usando la URI del docker-compose
    mongo_client = MongoClient(os.getenv("MONGO_URI"))
    db = mongo_client[os.getenv("MONGO_DB_NAME")]
    # Mongo crea la colección 'history' automáticamente al insertar el primer dato
    return db["history"] 

collection = get_mongo_collection()

# 2. Interfaz de Streamlit
st.set_page_config(page_title="AI Studio + Mongo", page_icon="🍃")
st.title("Generador AI con Historial NoSQL")

user_prompt = st.text_area("Ingresa tu consulta para Gemini:", height=150)

if st.button("Generar Respuesta", type="primary"):
    if not user_prompt.strip():
        st.warning("Escribe un prompt primero.")
    else:
        with st.spinner("Consultando a Google AI Studio..."):
            try:
                # Llamada a Gemini 2.5
                response = ai_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=user_prompt,
                )
                ai_text = response.text
                
                # Guardar el documento en MongoDB
                document = {
                    "prompt": user_prompt,
                    "response": ai_text,
                    "created_at": datetime.now()
                }
                collection.insert_one(document)

                st.success("¡Respuesta generada y guardada en MongoDB!")
                st.markdown(ai_text)
                
            except Exception as e:
                st.error(f"Ocurrió un error: {e}")

# 3. Mostrar el historial desde MongoDB
st.divider()
st.subheader("Historial Guardado")

if st.button("Refrescar Historial"):
    # Buscamos los últimos 5 documentos, ordenados por fecha descendente
    recent_chats = list(collection.find().sort("created_at", -1).limit(5))
    
    if recent_chats:
        for chat in recent_chats:
            # chat["created_at"] ya es un objeto datetime gracias a pymongo
            date_str = chat["created_at"].strftime('%Y-%m-%d %H:%M')
            with st.expander(f"📝 {chat['prompt'][:50]}... ({date_str})"):
                st.markdown("**Respuesta:**")
                st.markdown(chat["response"])
    else:
        st.info("Aún no hay registros en la base de datos.")
