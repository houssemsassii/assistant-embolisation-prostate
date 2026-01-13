"""
Script d'ingestion des documents PDF pour le chatbot médical RAG.
Construit un index FAISS à partir des PDF fournis avec:
- Semantic chunking (découpage sémantique)
- Préparation pour hybrid retrieval (vector + keyword search)

⚠️ USAGE MÉDICAL - Ce script traite des documents médicaux validés
pour créer une base de connaissances stricte (pas d'hallucinations).
"""

import os
import sys
from pathlib import Path
from typing import List
import pickle

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# ============================================
# CONFIGURATION
# ============================================

PDF_DIR = Path("data/pdfs")
VECTOR_STORE_DIR = Path("vector_store")

# Configuration pour semantic chunking
USE_SEMANTIC_CHUNKING = os.getenv("USE_SEMANTIC_CHUNKING", "true").lower() == "true"

# Fallback configuration si semantic chunking échoue
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

# Modèle d'embeddings français (optimisé pour le français)
EMBEDDING_MODEL = "dangvantuan/sentence-camembert-large"


def load_pdfs(pdf_directory: Path) -> List:
    """
    Charge tous les fichiers PDF du répertoire spécifié.
    
    Args:
        pdf_directory: Chemin vers le dossier contenant les PDFs
        
    Returns:
        Liste de documents LangChain avec métadonnées
    """
    if not pdf_directory.exists():
        print(f"❌ Erreur: Le dossier {pdf_directory} n'existe pas.")
        print(f"   Créez le dossier et placez-y vos PDFs sur l'embolisation de la prostate.")
        sys.exit(1)
    
    pdf_files = list(pdf_directory.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ Erreur: Aucun fichier PDF trouvé dans {pdf_directory}")
        sys.exit(1)
    
    print(f"📄 {len(pdf_files)} fichier(s) PDF trouvé(s):")
    for pdf_file in pdf_files:
        print(f"   • {pdf_file.name}")
    
    all_documents = []
    
    for pdf_file in pdf_files:
        print(f"\n📖 Chargement de: {pdf_file.name}")
        try:
            loader = PyPDFLoader(str(pdf_file))
            documents = loader.load()
            
            # Ajout de métadonnées personnalisées
            for doc in documents:
                doc.metadata.update({
                    "source_file": pdf_file.name,
                    "procedure": "embolisation de la prostate",
                    "type": "document_patient",
                    "langue": "français"
                })
            
            all_documents.extend(documents)
            print(f"   ✅ {len(documents)} page(s) chargée(s)")
            
        except Exception as e:
            print(f"   ⚠️ Erreur lors du chargement de {pdf_file.name}: {e}")
            continue
    
    if not all_documents:
        print("\n❌ Aucun document n'a pu être chargé.")
        sys.exit(1)
    
    print(f"\n✅ Total: {len(all_documents)} page(s) chargée(s)")
    return all_documents


def split_documents_semantic(documents: List, embeddings) -> List:
    """
    Découpe les documents en utilisant le semantic chunking.
    Les chunks sont créés en fonction de la similarité sémantique du contenu.
    
    Args:
        documents: Liste de documents LangChain
        embeddings: Modèle d'embeddings pour le semantic chunking
        
    Returns:
        Liste de chunks avec métadonnées préservées
    """
    print(f"\n✂️  Découpage sémantique des documents...")
    print(f"   Méthode: Semantic Chunking (basé sur similarité sémantique)")
    print(f"   ⏳ Analyse de la structure sémantique en cours...")
    
    try:
        # Semantic chunker avec percentile breakpoint
        text_splitter = SemanticChunker(
            embeddings,
            breakpoint_threshold_type="percentile",
            breakpoint_threshold_amount=80  # Seuil de similarité
        )
        
        chunks = text_splitter.split_documents(documents)
        
        print(f"   ✅ {len(chunks)} chunk(s) sémantique(s) créé(s)")
        
        # Statistiques sur la taille des chunks
        chunk_sizes = [len(chunk.page_content) for chunk in chunks]
        if chunk_sizes:
            avg_size = sum(chunk_sizes) / len(chunk_sizes)
            min_size = min(chunk_sizes)
            max_size = max(chunk_sizes)
            print(f"   📊 Statistiques des chunks:")
            print(f"      - Taille moyenne: {int(avg_size)} caractères")
            print(f"      - Taille min: {min_size} caractères")
            print(f"      - Taille max: {max_size} caractères")
        
    except Exception as e:
        print(f"   ⚠️ Erreur lors du semantic chunking: {e}")
        print(f"   🔄 Basculement vers RecursiveCharacterTextSplitter...")
        return split_documents_recursive(documents)
    
    # Affichage d'un exemple de chunk pour vérification
    if chunks:
        print(f"\n📝 Exemple de chunk sémantique (premier):")
        print(f"   Source: {chunks[0].metadata.get('source_file', 'N/A')}")
        print(f"   Contenu (100 premiers caractères): {chunks[0].page_content[:100]}...")
    
    return chunks


def split_documents_recursive(documents: List) -> List:
    """
    Découpe les documents avec RecursiveCharacterTextSplitter (fallback).
    
    Args:
        documents: Liste de documents LangChain
        
    Returns:
        Liste de chunks avec métadonnées préservées
    """
    print(f"\n✂️  Découpage récursif des documents...")
    print(f"   Taille de chunk: {CHUNK_SIZE} caractères")
    print(f"   Chevauchement: {CHUNK_OVERLAP} caractères")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", "! ", "? ", ", ", " ", ""],
        add_start_index=True
    )
    
    chunks = text_splitter.split_documents(documents)
    
    print(f"   ✅ {len(chunks)} chunk(s) créé(s)")
    
    # Affichage d'un exemple de chunk pour vérification
    if chunks:
        print(f"\n📝 Exemple de chunk (premier):")
        print(f"   Source: {chunks[0].metadata.get('source_file', 'N/A')}")
        print(f"   Contenu (100 premiers caractères): {chunks[0].page_content[:100]}...")
    
    return chunks


def create_embeddings():
    """
    Crée le modèle d'embeddings français.
    """
    print(f"\n🧠 Initialisation du modèle d'embeddings...")
    print(f"   Modèle: {EMBEDDING_MODEL}")
    print(f"   ⏳ Téléchargement en cours (peut prendre quelques minutes la première fois)...")
    
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    print(f"   ✅ Modèle chargé avec succès")
    return embeddings


def build_vector_store(chunks: List, embeddings) -> FAISS:
    """
    Construit l'index FAISS à partir des chunks.
    
    Args:
        chunks: Liste de chunks de documents
        embeddings: Modèle d'embeddings
        
    Returns:
        Vector store FAISS
    """
    print(f"\n🔍 Construction de l'index vectoriel FAISS...")
    print(f"   ⏳ Génération des embeddings pour {len(chunks)} chunks...")
    print(f"   (Cela peut prendre plusieurs minutes)")
    
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    print(f"   ✅ Index FAISS créé avec succès")
    return vector_store


def save_vector_store(vector_store: FAISS, chunks: List):
    """
    Sauvegarde l'index FAISS et les données pour hybrid retrieval.
    
    Args:
        vector_store: Vector store FAISS à sauvegarder
        chunks: Liste des chunks (pour BM25)
    """
    print(f"\n💾 Sauvegarde de l'index vectoriel...")
    
    VECTOR_STORE_DIR.mkdir(exist_ok=True)
    
    # Sauvegarde de l'index FAISS
    vector_store.save_local(str(VECTOR_STORE_DIR))
    print(f"   ✅ Index FAISS sauvegardé")
    
    # Sauvegarde des chunks pour BM25 (hybrid retrieval)
    chunks_file = VECTOR_STORE_DIR / "chunks.pkl"
    with open(chunks_file, 'wb') as f:
        pickle.dump(chunks, f)
    print(f"   ✅ Chunks sauvegardés pour hybrid retrieval")
    
    print(f"\n   📁 Fichiers créés dans {VECTOR_STORE_DIR}/:")
    for file in sorted(VECTOR_STORE_DIR.iterdir()):
        size = file.stat().st_size
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.1f} MB"
        print(f"      • {file.name} ({size_str})")


def main():
    """
    Pipeline principal d'ingestion.
    """
    print("=" * 70)
    print("🏥 INGESTION DES DOCUMENTS MÉDICAUX")
    print("   Embolisation de la prostate - Base de connaissances RAG")
    print("   Features: Semantic Chunking + Hybrid Retrieval")
    print("=" * 70)
    
    # 1. Chargement des PDFs
    documents = load_pdfs(PDF_DIR)
    
    # 2. Création des embeddings (nécessaire avant le semantic chunking)
    embeddings = create_embeddings()
    
    # 3. Découpage en chunks (sémantique ou récursif)
    if USE_SEMANTIC_CHUNKING:
        chunks = split_documents_semantic(documents, embeddings)
    else:
        chunks = split_documents_recursive(documents)
    
    # 4. Construction de l'index vectoriel
    vector_store = build_vector_store(chunks, embeddings)
    
    # 5. Sauvegarde (FAISS + chunks pour BM25)
    save_vector_store(vector_store, chunks)
    
    print("\n" + "=" * 70)
    print("✅ INGESTION TERMINÉE AVEC SUCCÈS")
    print("=" * 70)
    print(f"\n📊 Statistiques:")
    print(f"   • Documents traités: {len(documents)} pages")
    print(f"   • Chunks créés: {len(chunks)}")
    print(f"   • Méthode: {'Semantic Chunking' if USE_SEMANTIC_CHUNKING else 'Recursive Chunking'}")
    print(f"   • Index sauvegardé: {VECTOR_STORE_DIR}/")
    print(f"\n🚀 Vous pouvez maintenant lancer l'application:")
    print(f"   streamlit run app.py")
    print(f"\n💡 L'application utilisera:")
    print(f"   • Vector Search (FAISS) - recherche sémantique")
    print(f"   • Keyword Search (BM25) - recherche par mots-clés")
    print(f"   • Hybrid Retrieval - combinaison des deux méthodes")
    print()


if __name__ == "__main__":
    main()
