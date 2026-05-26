import streamlit as st
import os
from datetime import datetime
from pymongo import MongoClient
from google import genai
from google.genai import types

# 1. Configuración de clientes
ai_client = genai.Client()

@st.cache_resource
def get_mongo_collection():
    mongo_client = MongoClient(os.getenv("MONGO_URI"))
    db = mongo_client[os.getenv("MONGO_DB_NAME")]
    return db["history"]

collection = get_mongo_collection()

# 2. Configuración de la IA (El Cerebro del Senior Data Scientist)
SYSTEM_INSTRUCTION = """
Eres un Científico de Datos Senior con más de 10 años de experiencia, experto en Machine Learning, Deep Learning y Analítica de Datos.

REGLAS ESTRICTAS:
1. SOLO puedes responder preguntas relacionadas con Machine Learning, IA, matemáticas aplicadas a datos o estadística. 
2. Si el usuario pregunta sobre cualquier otro tema (cocina, historia, programación general no orientada a datos, etc.), DEBES rechazar la pregunta cortésmente indicando tu especialidad.
3. Tus respuestas DEBEN seguir SIEMPRE y OBLIGATORIAMENTE esta estructura exacta usando Markdown:

### 📖 Definición Formal
[Proporciona una definición técnica, rigurosa y académica del concepto].

### 🧠 Analogía
[Explica el concepto usando una analogía del mundo real que cualquier persona pueda entender].

### 🌍 Ejemplo en la Industria
[Proporciona un caso de uso práctico específico detallando cómo se aplica este concepto para resolver un problema de negocio].
"""

# 3. Interfaz de Streamlit
st.set_page_config(page_title="Data Science Hub", page_icon="🧠", layout="wide")

# Título llamativo
st.title("🤖 Oracle ML: Tu Arquitecto de Datos Senior")
st.markdown("Consulta conceptos de Machine Learning y recibe explicaciones estructuradas a nivel experto.")

# --- INICIO DEL MENÚ LATERAL ---
# Inicializamos el estado para la caja de texto
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

def set_prompt(text):
    st.session_state.input_text = text

with st.sidebar:
    st.header("💡 Consultas Rápidas")
    st.markdown("Haz clic en un concepto para cargarlo:")
    
    # Botones que inyectan el texto en la caja principal
    st.button("¿Qué es el Overfitting?", 
              on_click=set_prompt, args=("Explícame qué es el Overfitting en redes neuronales.",), use_container_width=True)
    
    st.button("Modelos XAI (SHAP vs LIME)", 
              on_click=set_prompt, args=("¿Cuál es la diferencia entre SHAP y LIME al interpretar modelos predictivos para riesgo crediticio?",), use_container_width=True)
    
    st.button("Gradient Descent", 
              on_click=set_prompt, args=("¿Cómo funciona el algoritmo de Gradient Descent bajo el capó?",), use_container_width=True)
    
    st.button("Random Forest vs XGBoost", 
              on_click=set_prompt, args=("Compara Random Forest con XGBoost a nivel de arquitectura de árboles.",), use_container_width=True)

    st.divider()
    st.header("⚙️ Administración")
    if st.button("🗑️ Limpiar Historial DB", type="secondary"):
        collection.delete_many({})
        st.success("Base de datos MongoDB limpiada.")
# --- FIN DEL MENÚ LATERAL ---

# 4. Caja de entrada principal
user_prompt = st.text_area("Ingresa tu consulta sobre Inteligencia Artificial:", 
                           value=st.session_state.input_text, 
                           height=100)

if st.button("Procesar Consulta", type="primary"):
    if not user_prompt.strip():
        st.warning("Escribe un prompt primero.")
    else:
        with st.spinner("Analizando con rigor matemático..."):
            try:
                # Llamada a Gemini 2.5 con System Instructions y Temperatura baja
                response = ai_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.2, # Respuestas más factuales y menos creativas/alucinadas
                    )
                )
                ai_text = response.text
                
                # Guardar en MongoDB
                document = {
                    "prompt": user_prompt,
                    "response": ai_text,
                    "created_at": datetime.now()
                }
                collection.insert_one(document)

                st.success("Análisis completado y registrado.")
                
                # Mostrar respuesta en una tarjeta (container) visualmente atractiva
                with st.container(border=True):
                    st.markdown(ai_text)
                
            except Exception as e:
                st.error(f"Ocurrió un error en el clúster: {e}")

# 5. Historial desde MongoDB
st.divider()
st.subheader("📚 Bitácora de Consultas")

# Buscamos los últimos 5 documentos
recent_chats = list(collection.find().sort("created_at", -1).limit(5))

if recent_chats:
    for chat in recent_chats:
        date_str = chat["created_at"].strftime('%Y-%m-%d %H:%M')
        # Usamos el prompt como título del desplegable
        with st.expander(f"🔍 {chat['prompt'][:60]}... ({date_str})"):
            st.markdown(chat["response"])
else:
    st.info("La bitácora de la base de datos está vacía. Inicia una consulta.")