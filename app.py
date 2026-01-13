"""
Assistant médical RAG - Embolisation de la prostate
Application Streamlit avec consentement obligatoire et protection des données.

USAGE MÉDICAL - POC à des fins d'information générale uniquement.
Ne remplace PAS une consultation médicale.
"""

import os
import re
import time
import pickle
from pathlib import Path
from typing import List, Dict, Tuple

import streamlit as st
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun

# Chargement des variables d'environnement
load_dotenv()

# ============================================
# CONFIGURATION
# ============================================

VECTOR_STORE_DIR = Path("vector_store")
EMBEDDING_MODEL = "dangvantuan/sentence-camembert-large"
TOP_K = int(os.getenv("TOP_K_RETRIEVAL", "4"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")

# ============================================
# CUSTOM CSS
# ============================================

CUSTOM_CSS = """
<style>
    /* Palette de couleurs médicale professionnelle */
    :root {
        --primary-color: #2C5F8D;
        --secondary-color: #4A90A4;
        --accent-color: #7FB3D5;
        --success-color: #52B788;
        --warning-color: #F4A261;
        --danger-color: #E76F51;
        --light-bg: #F8F9FA;
        --card-bg: #FFFFFF;
        --text-primary: #2C3E50;
        --text-secondary: #5D6D7E;
        --border-color: #E1E8ED;
    }
    
    /* Masquer les éléments Streamlit non désirés */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Titre principal */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 3px solid var(--accent-color);
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: var(--text-secondary);
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Cards et containers */
    .info-card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: box-shadow 0.3s ease;
    }
    
    .info-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }
    
    .warning-card {
        background: linear-gradient(135deg, #FFF4E6 0%, #FFE8CC 100%);
        border-left: 4px solid var(--warning-color);
        border-radius: 8px;
        padding: 1.25rem;
        margin: 1.5rem 0;
    }
    
    .success-card {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        border-left: 4px solid var(--success-color);
        border-radius: 8px;
        padding: 1.25rem;
        margin: 1.5rem 0;
    }
    
    .danger-card {
        background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%);
        border-left: 4px solid var(--danger-color);
        border-radius: 8px;
        padding: 1.25rem;
        margin: 1.5rem 0;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--primary-color);
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--accent-color);
    }
    
    /* Liste stylée */
    .styled-list {
        list-style: none;
        padding-left: 0;
    }
    
    .styled-list li {
        padding: 0.75rem 0;
        padding-left: 2rem;
        position: relative;
        color: var(--text-primary);
        line-height: 1.6;
    }
    
    .styled-list li:before {
        content: "▸";
        position: absolute;
        left: 0.5rem;
        color: var(--secondary-color);
        font-weight: bold;
    }
    
    /* Boutons personnalisés */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(44, 95, 141, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(44, 95, 141, 0.3);
    }
    
    /* Checkbox personnalisé */
    .stCheckbox {
        font-size: 1.1rem;
        padding: 1rem;
        background: var(--light-bg);
        border-radius: 8px;
    }
    
    /* Chat messages */
    .stChatMessage {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Source documents */
    .source-container {
        background: var(--light-bg);
        border-left: 3px solid var(--accent-color);
        border-radius: 6px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .source-title {
        font-weight: 600;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
    }
    
    .source-content {
        color: var(--text-secondary);
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: var(--light-bg);
    }
    
    /* Espacement et typographie générale */
    .stMarkdown {
        line-height: 1.7;
    }
    
    p {
        color: var(--text-primary);
        font-size: 1.05rem;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-top-color: var(--primary-color) !important;
    }
    
    /* Divider personnalisé */
    hr {
        margin: 2rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
    }
</style>
"""

# ============================================
# PROMPTS SYSTÈME (SÉCURITÉ MÉDICALE)
# ============================================

SYSTEM_PROMPT_TEMPLATE = """Tu es un assistant médical spécialisé dans l'information sur l'embolisation de la prostate.

RÈGLES DE SÉCURITÉ ABSOLUES (À RESPECTER IMPÉRATIVEMENT):

1. TU NE RÉPONDS QU'À PARTIR DES DOCUMENTS FOURNIS
   - Si l'information n'est pas dans les documents, réponds EXACTEMENT:
     "Cette information n'est pas disponible dans les documents fournis et doit être discutée avec votre médecin."
   - NE PAS utiliser tes connaissances générales sur le sujet
   - NE PAS inventer ou extrapoler

2. TU NE DONNES PAS DE CONSEILS MÉDICAUX PERSONNALISÉS
   - Ne fais pas de diagnostic
   - Ne recommande pas de traitement spécifique
   - Ne commente pas de situations individuelles

3. DÉTECTION DE DONNÉES PERSONNELLES
   Si la question contient:
   - Des informations personnelles (âge, traitements, antécédents)
   - Des formulations comme "dans mon cas", "dois-je", "suis-je à risque"
   → Réponds: "Je ne peux pas traiter d'informations personnelles. Merci de poser uniquement des questions générales."

4. STYLE DE RÉPONSE
   - Langue: français uniquement
   - Ton: neutre, pédagogique, non alarmiste, non rassurant
   - Explique les termes médicaux simplement
   - Indique ce qui doit être discuté avec un médecin

5. TOUJOURS RAPPELER
   - Pour toute question spécifique à votre situation, consultez votre médecin
   - Les délais, résultats et effets peuvent varier selon les patients

CONTEXTE TIRÉ DES DOCUMENTS:
{context}

QUESTION DU PATIENT:
{question}

RÉPONSE (en respectant TOUTES les règles ci-dessus):"""

PERSONAL_DATA_KEYWORDS = [
    r"\bj'ai\b.*\bans\b",  # "j'ai X ans"
    r"\bmon cas\b",
    r"\bma situation\b",
    r"\bdois-je\b",
    r"\bje prends\b",
    r"\bje suis\b.*\b(malade|traité|opéré)\b",
    r"\bmon médecin\b",
    r"\bmes résultats\b",
    r"\bsuis-je à risque\b",
    r"\best-ce grave\b.*\bmoi\b",
    r"\bdans mon cas\b",
]

# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def detect_personal_data(question: str) -> bool:
    """
    Détecte si la question contient des données personnelles.
    
    Args:
        question: Question de l'utilisateur
        
    Returns:
        True si des données personnelles sont détectées
    """
    question_lower = question.lower()
    
    for pattern in PERSONAL_DATA_KEYWORDS:
        if re.search(pattern, question_lower):
            return True
    
    return False


def init_session_state():
    """
    Initialise l'état de session Streamlit.
    """
    if "consent_given" not in st.session_state:
        st.session_state.consent_given = False
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None
    
    if "hybrid_retriever" not in st.session_state:
        st.session_state.hybrid_retriever = None
    
    if "qa_chain" not in st.session_state:
        st.session_state.qa_chain = None
    
    if "loading_complete" not in st.session_state:
        st.session_state.loading_complete = False


# ============================================
# HYBRID RETRIEVAL
# ============================================

class HybridRetriever(BaseRetriever):
    """
    Retriever hybride combinant recherche vectorielle (FAISS) et recherche par mots-clés (BM25).
    Utilise Reciprocal Rank Fusion (RRF) pour combiner les résultats.
    """
    
    vector_store: FAISS
    bm25: BM25Okapi
    chunks: List[Document]
    k: int = 4
    alpha: float = 0.5  # Poids pour la recherche vectorielle (0.5 = équilibré)
    
    class Config:
        arbitrary_types_allowed = True
    
    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
    ) -> List[Document]:
        """
        Récupère les documents pertinents en combinant recherche vectorielle et BM25.
        """
        # 1. Recherche vectorielle (sémantique)
        vector_docs = self.vector_store.similarity_search(query, k=self.k * 2)
        
        # 2. Recherche BM25 (mots-clés)
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        # Obtenir les top k indices pour BM25
        bm25_top_indices = sorted(
            range(len(bm25_scores)), 
            key=lambda i: bm25_scores[i], 
            reverse=True
        )[:self.k * 2]
        
        bm25_docs = [self.chunks[i] for i in bm25_top_indices]
        
        # 3. Reciprocal Rank Fusion (RRF)
        doc_scores = {}
        
        # Scores from vector search
        for rank, doc in enumerate(vector_docs):
            doc_id = doc.page_content
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + self.alpha / (rank + 60)
        
        # Scores from BM25
        for rank, doc in enumerate(bm25_docs):
            doc_id = doc.page_content
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + (1 - self.alpha) / (rank + 60)
        
        # Trier par score et retourner les top k
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)[:self.k]
        
        # Reconstituer les documents
        doc_map = {doc.page_content: doc for doc in vector_docs + bm25_docs}
        final_docs = [doc_map[doc_id] for doc_id, _ in sorted_docs if doc_id in doc_map]
        
        return final_docs


@st.cache_resource
def load_vector_store():
    """
    Charge l'index FAISS et crée le retriever hybride (FAISS + BM25).
    
    Returns:
        Tuple (vector_store, hybrid_retriever)
    """
    if not VECTOR_STORE_DIR.exists():
        st.error("INDEX VECTORIEL NON TROUVÉ. Veuillez d'abord exécuter `python ingest.py`")
        st.stop()
    
    # 1. Charger les embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    # 2. Charger le vector store FAISS
    vector_store = FAISS.load_local(
        str(VECTOR_STORE_DIR),
        embeddings,
        allow_dangerous_deserialization=True
    )
    
    # 3. Charger les chunks pour BM25
    chunks_file = VECTOR_STORE_DIR / "chunks.pkl"
    if chunks_file.exists():
        with open(chunks_file, 'rb') as f:
            chunks = pickle.load(f)
        
        # 4. Créer l'index BM25
        tokenized_chunks = [chunk.page_content.lower().split() for chunk in chunks]
        bm25 = BM25Okapi(tokenized_chunks)
        
        # 5. Créer le hybrid retriever
        hybrid_retriever = HybridRetriever(
            vector_store=vector_store,
            bm25=bm25,
            chunks=chunks,
            k=TOP_K,
            alpha=0.6  # 60% vector search, 40% keyword search
        )
        
        return vector_store, hybrid_retriever
    else:
        # Fallback: si pas de chunks.pkl, utiliser uniquement FAISS
        st.warning("⚠️ Fichier chunks.pkl non trouvé. Utilisation de la recherche vectorielle uniquement.")
        return vector_store, None


def get_llm():
    """
    Initialise le LLM selon le provider configuré.
    
    Returns:
        Instance de LLM LangChain
    """
    if LLM_PROVIDER == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("CLÉ API OPENAI NON TROUVÉE. Configurez OPENAI_API_KEY dans .env")
            st.stop()
        
        return ChatOpenAI(
            model=MODEL_NAME,
            temperature=TEMPERATURE,
            api_key=api_key
        )
    
    elif LLM_PROVIDER == "groq":
        # Utilise ChatGroq de langchain-groq
        from langchain_groq import ChatGroq
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            st.error("CLÉ API GROQ NON TROUVÉE. Configurez GROQ_API_KEY dans .env")
            st.stop()
        
        return ChatGroq(
            model=MODEL_NAME,
            temperature=TEMPERATURE,
            groq_api_key=api_key
        )
    
    else:
        st.error(f"PROVIDER '{LLM_PROVIDER}' NON SUPPORTÉ. Utilisez 'openai' ou 'groq'")
        st.stop()


def create_qa_chain(vector_store, hybrid_retriever=None):
    """
    Crée la chaîne RAG avec le prompt système.
    Utilise le hybrid retriever si disponible, sinon FAISS seul.
    
    Args:
        vector_store: Vector store FAISS
        hybrid_retriever: Retriever hybride (optionnel)
        
    Returns:
        Chaîne RetrievalQA
    """
    try:
        llm = get_llm()
        if llm is None:
            raise ValueError("Le LLM n'a pas été initialisé correctement")
        
        prompt = PromptTemplate(
            template=SYSTEM_PROMPT_TEMPLATE,
            input_variables=["context", "question"]
        )
        
        # Utiliser le hybrid retriever si disponible, sinon FAISS
        if hybrid_retriever is not None:
            retriever = hybrid_retriever
        else:
            retriever = vector_store.as_retriever(search_kwargs={"k": TOP_K})
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )
        
        if qa_chain is None:
            raise ValueError("La chaîne RetrievalQA n'a pas été créée")
        
        return qa_chain
    except Exception as e:
        st.error(f"ERREUR LORS DE LA CRÉATION DE LA CHAÎNE RAG: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        raise


def get_response(qa_chain, question: str) -> Tuple[str, List]:
    """
    Obtient une réponse du système RAG.
    
    Args:
        qa_chain: Chaîne RAG
        question: Question de l'utilisateur
        
    Returns:
        Tuple (réponse, documents sources)
    """
    if qa_chain is None:
        raise ValueError("La chaîne RAG n'est pas initialisée")
    
    try:
        result = qa_chain.invoke({"query": question})
        return result["result"], result.get("source_documents", [])
    except Exception as e:
        raise Exception(f"Erreur lors de l'invocation de la chaîne RAG: {str(e)}")


# ============================================
# INTERFACE STREAMLIT
# ============================================

def show_consent_screen():
    """
    Affiche l'écran de consentement obligatoire avec un design amélioré.
    """
    # Injection du CSS personnalisé
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # En-tête principal avec logo médical
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="font-size: 4rem; color: var(--primary-color); margin-bottom: 1rem;">⚕</div>
        <h1 class="main-title" style="border-bottom: none;">Assistant d'information médical</h1>
        <p class="subtitle">Embolisation de la prostate</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Introduction
    st.markdown("""
    <div class="info-card">
        <p>Cet assistant a été conçu pour vous fournir <strong>des informations générales</strong> 
        sur la procédure d'embolisation de la prostate, les étapes pré-opératoires et post-opératoires, 
        ainsi que des réponses aux questions fréquentes.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Avertissements importants
    st.markdown('<h2 class="section-header">⚠ Avertissements importants</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="success-card">
            <h4 style="margin-top:0; color: var(--success-color);">Ce que cet assistant PEUT faire</h4>
            <ul class="styled-list">
                <li>Fournir des informations générales validées</li>
                <li>Répondre aux questions sur la procédure</li>
                <li>Expliquer les termes médicaux</li>
                <li>Partager des informations post-opératoires</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="danger-card">
            <h4 style="margin-top:0; color: var(--danger-color);">Ce que cet assistant NE PEUT PAS faire</h4>
            <ul class="styled-list">
                <li>Remplacer une consultation médicale</li>
                <li>Fournir un diagnostic</li>
                <li>Donner des conseils personnalisés</li>
                <li>Évaluer votre situation individuelle</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Protection des données
    st.markdown('<h2 class="section-header">🔒 Protection de vos données personnelles</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="warning-card">
        <h4 style="margin-top:0; color: var(--warning-color);">Pour votre sécurité et votre vie privée</h4>
        <p><strong>Vous ne devez PAS fournir :</strong></p>
        <ul class="styled-list">
            <li>Votre identité (nom, prénom)</li>
            <li>Votre âge ou date de naissance</li>
            <li>Vos antécédents médicaux</li>
            <li>Vos traitements en cours</li>
            <li>Vos résultats d'examens</li>
            <li>Toute autre information personnelle ou médicale</li>
        </ul>
        <p style="margin-bottom:0;"><strong>Si vous tentez de partager des informations personnelles, l'assistant refusera d'y répondre.</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Utilisation des conversations
    st.markdown('<h2 class="section-header">📊 Utilisation des conversations</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card">
        <p>Les conversations avec cet assistant peuvent être utilisées de manière <strong>anonyme</strong> à des fins de :</p>
        <ul class="styled-list">
            <li>Recherche médicale</li>
            <li>Amélioration du service</li>
            <li>Évaluation de la qualité</li>
        </ul>
        <p style="margin-bottom:0;">Aucune donnée personnelle n'est collectée si vous respectez les consignes ci-dessus.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Consultation médicale
    st.markdown('<h2 class="section-header">⚕ Consultation médicale obligatoire</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card">
        <p><strong>Toute question concernant votre situation personnelle doit être posée à votre médecin.</strong></p>
        <p>Seul votre médecin peut :</p>
        <ul class="styled-list">
            <li>Évaluer votre état de santé</li>
            <li>Poser un diagnostic</li>
            <li>Prescrire un traitement</li>
            <li>Répondre à vos préoccupations individuelles</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Consentement
    st.markdown('<h2 class="section-header">✓ Consentement</h2>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Checkbox de consentement
    consent_checkbox = st.checkbox(
        "J'ai lu et j'accepte les conditions d'utilisation",
        value=False
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Bouton de démarrage
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Commencer la discussion", type="primary", use_container_width=True, disabled=not consent_checkbox):
            st.session_state.consent_given = True
            st.rerun()
    
    if not consent_checkbox:
        st.markdown("""
        <div class="warning-card">
            <p style="margin:0; text-align:center;">
                <strong>Vous devez accepter les conditions d'utilisation pour continuer.</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)


def show_loading_screen():
    """
    Affiche un écran de chargement professionnel pendant l'initialisation.
    """
    # Injection du CSS personnalisé
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem;">
        <div style="font-size: 5rem; color: var(--primary-color); margin-bottom: 2rem; animation: pulse 2s infinite;">
            ⚕
        </div>
        <h1 style="color: var(--primary-color); font-size: 2rem; margin-bottom: 1rem;">
            Initialisation de l'assistant médical
        </h1>
        <p style="color: var(--text-secondary); font-size: 1.2rem; margin-bottom: 2rem;">
            Chargement de la base de connaissances médicales...
        </p>
        <div style="max-width: 400px; margin: 0 auto;">
            <div style="background: var(--light-bg); border-radius: 10px; height: 10px; overflow: hidden;">
                <div style="background: linear-gradient(90deg, var(--primary-color), var(--secondary-color)); 
                            height: 100%; width: 0%; animation: loading 2s ease-in-out infinite;"></div>
            </div>
        </div>
    </div>
    
    <style>
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(1.05); }
        }
        
        @keyframes loading {
            0% { width: 0%; }
            50% { width: 70%; }
            100% { width: 100%; }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Chargement effectif des ressources
    with st.spinner(""):
        if st.session_state.vector_store is None:
            # Charger le vector store et le hybrid retriever
            st.session_state.vector_store, st.session_state.hybrid_retriever = load_vector_store()
            
            # Créer la chaîne QA avec le hybrid retriever
            st.session_state.qa_chain = create_qa_chain(
                st.session_state.vector_store,
                st.session_state.hybrid_retriever
            )
        
        # Marquer le chargement comme complet
        st.session_state.loading_complete = True
        
        # Petit délai pour que l'utilisateur voie l'animation complète
        time.sleep(1)
        
        # Recharger la page pour afficher l'interface de chat
        st.rerun()


def show_chat_interface():
    """
    Affiche l'interface de chat principale avec un design amélioré.
    """
    # Injection du CSS personnalisé
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # En-tête avec logo
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
        <div style="font-size: 2.5rem; color: var(--primary-color); margin-right: 1rem;">⚕</div>
        <h1 class="main-title" style="margin: 0; border: none; padding: 0;">Assistant : Embolisation de la prostate</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Disclaimer permanent
    st.markdown("""
    <div class="warning-card">
        <p style="margin:0; text-align:center;">
            <strong>Ce chatbot fournit des informations générales et ne remplace pas une consultation médicale.</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Affichage de l'historique des messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Affichage des sources si disponibles
            if message["role"] == "assistant" and "sources" in message:
                with st.expander("Sources documentaires utilisées"):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f"""
                        <div class="source-container">
                            <div class="source-title">Source {i}: {source['file']}</div>
                            <div class="source-content">{source['content'][:250]}...</div>
                        </div>
                        """, unsafe_allow_html=True)
    
    # Input utilisateur
    if question := st.chat_input("Posez votre question sur l'embolisation de la prostate..."):
        
        # Vérification des données personnelles
        if detect_personal_data(question):
            # Affichage de la question
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)
            
            # Réponse de refus
            refusal_message = """
**Je ne peux pas traiter d'informations personnelles.**

Merci de poser uniquement des **questions générales** sur l'embolisation de la prostate.

Pour toute question concernant votre situation personnelle, veuillez consulter votre médecin.
            """
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": refusal_message
            })
            
            with st.chat_message("assistant"):
                st.markdown(refusal_message)
            
            st.rerun()
        
        else:
            # Question valide - traitement normal
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)
            
            # Génération de la réponse
            with st.chat_message("assistant"):
                with st.spinner("Recherche dans les documents médicaux..."):
                    try:
                        response, source_docs = get_response(st.session_state.qa_chain, question)
                        
                        # Affichage de la réponse
                        st.markdown(response)
                        
                        # Extraction des sources
                        sources = []
                        for doc in source_docs:
                            sources.append({
                                "file": doc.metadata.get("source_file", "Document"),
                                "content": doc.page_content
                            })
                        
                        # Affichage des sources
                        if sources:
                            with st.expander("Sources documentaires utilisées"):
                                for i, source in enumerate(sources, 1):
                                    st.markdown(f"""
                                    <div class="source-container">
                                        <div class="source-title">Source {i}: {source['file']}</div>
                                        <div class="source-content">{source['content'][:250]}...</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                        
                        # Sauvegarde dans l'historique
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response,
                            "sources": sources
                        })
                    
                    except Exception as e:
                        error_msg = f"ERREUR : Impossible de générer une réponse. {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })
    
    # Sidebar
    with st.sidebar:
        st.markdown('<h3 style="color: var(--primary-color);">⚙ Actions</h3>', unsafe_allow_html=True)
        if st.button("↻ Nouvelle conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
        
        st.markdown('<h3 style="color: var(--primary-color);">⚙ Configuration technique</h3>', unsafe_allow_html=True)
        
        # Déterminer le mode de retrieval
        retrieval_mode = "Hybrid (Vector + Keyword)" if st.session_state.hybrid_retriever else "Vector Only"
        
        st.markdown(f"""
        <div class="info-card">
            <p style="margin:0.25rem 0;"><strong>Modèle:</strong> {MODEL_NAME}</p>
            <p style="margin:0.25rem 0;"><strong>Provider:</strong> {LLM_PROVIDER}</p>
            <p style="margin:0.25rem 0;"><strong>Retrieval:</strong> {retrieval_mode}</p>
            <p style="margin:0.25rem 0;"><strong>Température:</strong> {TEMPERATURE}</p>
            <p style="margin:0.25rem 0;"><strong>Documents par requête:</strong> {TOP_K}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown('<h3 style="color: var(--primary-color);">ⓘ Rappels importants</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-card">
            <ul class="styled-list">
                <li>Pas de données personnelles</li>
                <li>Information générale uniquement</li>
                <li>Consultez votre médecin pour toute question spécifique</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


# ============================================
# POINT D'ENTRÉE PRINCIPAL
# ============================================

def main():
    """
    Point d'entrée principal de l'application.
    """
    # Configuration de la page
    st.set_page_config(
        page_title="Assistant médical - Embolisation prostate",
        page_icon="⚕",  # Medical symbol (logo acceptable)
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialisation de l'état
    init_session_state()
    
    # Routing selon l'état de l'application
    if not st.session_state.consent_given:
        # Écran de consentement
        show_consent_screen()
    elif not st.session_state.loading_complete:
        # Écran de chargement après consentement
        show_loading_screen()
    else:
        # Interface de chat une fois tout chargé
        show_chat_interface()


if __name__ == "__main__":
    main()
