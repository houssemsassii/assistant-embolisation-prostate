"""
Script d'ingestion multi-sources pour le chatbot médical RAG.
Construit un index FAISS à partir de:
- PDFs organisés par maladie/procédure (data/pdfs/maladie/*.pdf)
- Pages web du site laradiologiequisoigne.fr

⚠️ USAGE MÉDICAL - Ce script traite des documents médicaux validés
pour créer une base de connaissances stricte (pas d'hallucinations).
"""

import os
import sys
from pathlib import Path
from typing import List, Dict
import pickle

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# ============================================
# CONFIGURATION
# ============================================

PDF_DIR = Path("data/pdfs")
VECTOR_STORE_DIR = Path("vector_store")

# Configuration pour chunking optimisé
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

# Modèle d'embeddings français
EMBEDDING_MODEL = "dangvantuan/sentence-camembert-large"

# URLs des pages web à scraper par maladie (URLs CORRIGÉES - Janvier 2026)
WEB_URLS = {
    # Pages maladies (10 pages)
    "arthrose_genou": "https://www.laradiologiequisoigne.fr/gonarthrose/",
    "epaule_gelee": "https://www.laradiologiequisoigne.fr/epaule-gelee/",
    "prostate": "https://www.laradiologiequisoigne.fr/hyperplasie-benigne-de-la-prostate-hbp/",
    "fibrome_uterin": "https://www.laradiologiequisoigne.fr/fibrome-uterin/",
    "varicocele": "https://www.laradiologiequisoigne.fr/la-varicocele/",
    "hemorroides": "https://www.laradiologiequisoigne.fr/les-hemorroides/",
    "douleurs_marche": "https://www.laradiologiequisoigne.fr/claudication-intermittente/",
    "grosse_jambe": "https://www.laradiologiequisoigne.fr/la-grosse-jambe-post-phlebitique/",
    "cancer": "https://www.laradiologiequisoigne.fr/le-cancer/",
    "douleurs_osseuses": "https://www.laradiologiequisoigne.fr/douleurs-osseuses-chroniques/",
    
    # Pages générales (4 pages)
    "accueil": "https://www.laradiologiequisoigne.fr/",
    "service": "https://www.laradiologiequisoigne.fr/service-radiologie-interventionnelle-hegp/",
    "radiologues": "https://www.laradiologiequisoigne.fr/radiologues-interventionnels-hegp/",
    "actualites": "https://www.laradiologiequisoigne.fr/actualites-service/",
}


def detect_procedure_from_folder(folder_name: str) -> str:
    """
    Détecte la procédure/maladie depuis le nom du dossier.
    
    Args:
        folder_name: Nom du dossier (ex: "embolisation_prostate")
    
    Returns:
        Nom de la procédure formaté
    """
    # Mapping des noms de dossiers possibles
    procedure_mapping = {
        "embolisation_prostate": "Embolisation de la prostate",
        "prostate": "Embolisation de la prostate",
        "embolisation_uterine": "Embolisation utérine",
        "fibrome_uterin": "Fibrome utérin",
        "pose_pac": "Pose de PAC",
        "pac": "Pose de PAC",
        "biopsie_scanner": "Biopsie sous scanner",
        "biopsie": "Biopsie sous scanner",
        "arthrose_genou": "Arthrose du genou (gonarthrose)",
        "gonarthrose": "Arthrose du genou (gonarthrose)",
        "epaule_gelee": "Épaule gelée (capsulite rétractile)",
        "capsulite": "Épaule gelée (capsulite rétractile)",
        "varicocele": "Varicocèle",
        "hemorroides": "Hémorroïdes",
        "douleurs_marche": "Douleurs à la marche",
        "grosse_jambe": "Grosse jambe post-phlébite",
        "cancer": "Cancer",
        "douleurs_osseuses": "Douleurs osseuses",
    }
    
    folder_lower = folder_name.lower().replace(" ", "_").replace("-", "_")
    return procedure_mapping.get(folder_lower, folder_name.replace("_", " ").title())


def load_pdfs_recursive(base_directory: Path) -> List[Document]:
    """
    Charge tous les PDFs de manière récursive depuis les sous-dossiers.
    Chaque sous-dossier représente une maladie/procédure.
    
    Args:
        base_directory: Chemin vers le dossier racine contenant les sous-dossiers
        
    Returns:
        Liste de documents LangChain avec métadonnées enrichies
    """
    if not base_directory.exists():
        print(f"❌ Erreur: Le dossier {base_directory} n'existe pas.")
        print(f"   Structure attendue: data/pdfs/maladie/*.pdf")
        sys.exit(1)
    
    all_documents = []
    subdirs = [d for d in base_directory.iterdir() if d.is_dir()]
    
    if not subdirs:
        # Fallback: chercher PDFs directement dans le dossier racine
        print("⚠️  Aucun sous-dossier trouvé, recherche des PDFs à la racine...")
        subdirs = [base_directory]
    
    print(f"\n📁 Dossiers détectés: {len(subdirs)}")
    
    for subdir in subdirs:
        procedure_name = detect_procedure_from_folder(subdir.name) if subdir != base_directory else "Radiologie interventionnelle"
        pdf_files = list(subdir.glob("*.pdf"))
        
        if not pdf_files:
            print(f"   • {subdir.name}: Aucun PDF")
            continue
        
        print(f"\n📂 Procédure: {procedure_name}")
        print(f"   Dossier: {subdir.name}")
        print(f"   Fichiers: {len(pdf_files)} PDF(s)")
        
        for pdf_file in pdf_files:
            print(f"   📖 Chargement: {pdf_file.name}")
            try:
                loader = PyPDFLoader(str(pdf_file))
                documents = loader.load()
                
                # Ajout de métadonnées enrichies
                for doc in documents:
                    doc.metadata.update({
                        "source_file": pdf_file.name,
                        "source_type": "pdf",
                        "procedure": procedure_name,
                        "folder": subdir.name,
                        "type": "document_patient",
                        "langue": "français"
                    })
                
                all_documents.extend(documents)
                print(f"      ✅ {len(documents)} page(s) chargée(s)")
                
            except Exception as e:
                print(f"      ⚠️ Erreur: {e}")
                continue
    
    if not all_documents:
        print("\n⚠️ Aucun document PDF n'a pu être chargé.")
        print("   Le système continuera avec le contenu web uniquement.")
    else:
        print(f"\n✅ Total PDFs: {len(all_documents)} page(s) chargée(s)")
    
    return all_documents


def scrape_website() -> List[Document]:
    """
    Scrape toutes les pages pertinentes du site laradiologiequisoigne.fr
    
    Returns:
        Liste de documents web avec métadonnées
    """
    print(f"\n🌐 Scraping du site web: laradiologiequisoigne.fr")
    print(f"   Pages à scraper: {len(WEB_URLS)} (10 maladies + 4 pages générales)")
    
    web_documents = []
    
    for procedure_key, url in WEB_URLS.items():
        print(f"\n   🔗 {procedure_key}: {url}")
        try:
            loader = WebBaseLoader(url)
            docs = loader.load()
            
            # Détection de la procédure
            procedure_name = detect_procedure_from_folder(procedure_key)
            
            for doc in docs:
                # Nettoyage du contenu web (enlever navigation, footer, etc.)
                content = doc.page_content
                
                # Ajout de métadonnées
                doc.metadata.update({
                    "source_url": url,
                    "source_type": "web",
                    "source_name": "laradiologiequisoigne.fr",
                    "procedure": procedure_name,
                    "type": "information_generale",
                    "langue": "français"
                })
            
            web_documents.extend(docs)
            print(f"      ✅ Contenu récupéré ({len(docs[0].page_content)} caractères)")
            
        except Exception as e:
            print(f"      ⚠️ Erreur lors du scraping: {e}")
            continue
    
    if not web_documents:
        print("\n⚠️ Aucune page web n'a pu être scrapée.")
        print("   Le système continuera avec les PDFs uniquement.")
    else:
        print(f"\n✅ Total Web: {len(web_documents)} page(s) scrapée(s)")
    
    return web_documents


def split_documents(documents: List[Document]) -> List[Document]:
    """
    Découpe les documents avec RecursiveCharacterTextSplitter optimisé.
    
    Args:
        documents: Liste de documents LangChain
        
    Returns:
        Liste de chunks avec métadonnées préservées
    """
    print(f"\n✂️  Découpage intelligent des documents...")
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
    
    # Statistiques par source
    pdf_chunks = [c for c in chunks if c.metadata.get('source_type') == 'pdf']
    web_chunks = [c for c in chunks if c.metadata.get('source_type') == 'web']
    
    if pdf_chunks:
        print(f"      • Chunks PDFs: {len(pdf_chunks)}")
    if web_chunks:
        print(f"      • Chunks Web: {len(web_chunks)}")
    
    # Affichage d'exemples
    if chunks:
        print(f"\n📝 Exemples de chunks:")
        if pdf_chunks:
            print(f"   [PDF] {pdf_chunks[0].metadata.get('procedure', 'N/A')}")
            print(f"         Source: {pdf_chunks[0].metadata.get('source_file', 'N/A')}")
            print(f"         Extrait: {pdf_chunks[0].page_content[:80]}...")
        if web_chunks:
            print(f"   [WEB] {web_chunks[0].metadata.get('procedure', 'N/A')}")
            print(f"         URL: {web_chunks[0].metadata.get('source_url', 'N/A')}")
            print(f"         Extrait: {web_chunks[0].page_content[:80]}...")
    
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


def build_vector_store(chunks: List[Document], embeddings) -> FAISS:
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


def save_vector_store(vector_store: FAISS, chunks: List[Document]):
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
    Pipeline principal d'ingestion multi-sources.
    """
    print("=" * 80)
    print("🏥 INGESTION MULTI-SOURCES - RADIOLOGIE INTERVENTIONNELLE")
    print("   Sources: PDFs (par maladie) + Site web (laradiologiequisoigne.fr)")
    print("   Features: Intelligent Chunking + Hybrid Retrieval")
    print("=" * 80)
    
    all_documents = []
    
    # 1. Chargement des PDFs (par sous-dossier)
    print("\n📚 PHASE 1: Chargement des PDFs")
    pdf_documents = load_pdfs_recursive(PDF_DIR)
    all_documents.extend(pdf_documents)
    
    # 2. Scraping du site web
    print("\n🌐 PHASE 2: Scraping du site web")
    web_documents = scrape_website()
    all_documents.extend(web_documents)
    
    if not all_documents:
        print("\n❌ ERREUR: Aucun document chargé (ni PDF ni Web)")
        print("   Vérifiez que:")
        print("   1. Les PDFs sont dans data/pdfs/maladie/*.pdf")
        print("   2. La connexion internet fonctionne pour le scraping")
        sys.exit(1)
    
    print(f"\n✅ Total documents chargés: {len(all_documents)}")
    print(f"   • PDFs: {len(pdf_documents)}")
    print(f"   • Web: {len(web_documents)}")
    
    # 3. Découpage en chunks
    print("\n✂️  PHASE 3: Découpage des documents")
    chunks = split_documents(all_documents)
    
    # 4. Création des embeddings
    print("\n🧠 PHASE 4: Création des embeddings")
    embeddings = create_embeddings()
    
    # 5. Construction de l'index vectoriel
    print("\n🔍 PHASE 5: Construction de l'index FAISS")
    vector_store = build_vector_store(chunks, embeddings)
    
    # 6. Sauvegarde (FAISS + chunks pour BM25)
    print("\n💾 PHASE 6: Sauvegarde")
    save_vector_store(vector_store, chunks)
    
    print("\n" + "=" * 80)
    print("✅ INGESTION TERMINÉE AVEC SUCCÈS")
    print("=" * 80)
    print(f"\n📊 Statistiques finales:")
    print(f"   • Documents sources: {len(all_documents)}")
    print(f"     - PDFs: {len(pdf_documents)} pages")
    print(f"     - Web: {len(web_documents)} pages")
    print(f"   • Chunks créés: {len(chunks)}")
    
    # Statistiques par procédure
    procedures = {}
    for chunk in chunks:
        proc = chunk.metadata.get('procedure', 'Inconnu')
        procedures[proc] = procedures.get(proc, 0) + 1
    
    print(f"   • Procédures couvertes: {len(procedures)}")
    for proc, count in sorted(procedures.items(), key=lambda x: x[1], reverse=True):
        print(f"     - {proc}: {count} chunks")
    
    print(f"\n   • Index sauvegardé: {VECTOR_STORE_DIR}/")
    print(f"\n🚀 Vous pouvez maintenant lancer l'application:")
    print(f"   streamlit run app.py")
    print(f"\n💡 L'application utilisera:")
    print(f"   • Vector Search (FAISS) - recherche sémantique")
    print(f"   • Keyword Search (BM25) - recherche par mots-clés")
    print(f"   • Hybrid Retrieval - combinaison optimale")
    print(f"   • Multi-procédures - toutes les maladies couvertes")
    print()


if __name__ == "__main__":
    main()
