#!/bin/bash

# Script d'installation automatique pour l'assistant médical RAG
# Usage: bash setup.sh

set -e  # Arrêt en cas d'erreur

echo "=============================================="
echo "🏥 INSTALLATION ASSISTANT MÉDICAL RAG"
echo "   Embolisation de la prostate"
echo "=============================================="
echo ""

# Vérification de Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé."
    echo "   Installez Python 3.9+ depuis python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python détecté: $PYTHON_VERSION"
echo ""

# Étape 1: Environnement virtuel
echo "📦 Étape 1/5: Création de l'environnement virtuel"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   ✅ Environnement virtuel créé"
else
    echo "   ℹ️  Environnement virtuel existant trouvé"
fi
echo ""

# Activation de l'environnement virtuel
source venv/bin/activate

# Étape 2: Installation des dépendances
echo "📥 Étape 2/5: Installation des dépendances"
echo "   ⏳ Cela peut prendre 5-10 minutes..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "   ✅ Dépendances installées"
echo ""

# Étape 3: Préparation des documents
echo "📄 Étape 3/5: Préparation des documents PDF"
if [ -d "Documents" ] && [ "$(ls -A Documents/*.pdf 2>/dev/null)" ]; then
    echo "   📁 PDFs détectés dans Documents/"
    PDF_COUNT=$(ls -1 Documents/*.pdf 2>/dev/null | wc -l | xargs)
    echo "   📊 $PDF_COUNT fichier(s) PDF trouvé(s)"
    
    # Copier les PDFs
    mkdir -p data/pdfs
    cp Documents/*.pdf data/pdfs/
    echo "   ✅ PDFs copiés vers data/pdfs/"
    
    # Lister les fichiers
    echo ""
    echo "   Documents copiés:"
    for pdf in data/pdfs/*.pdf; do
        echo "      • $(basename "$pdf")"
    done
else
    echo "   ⚠️  Aucun PDF trouvé dans Documents/"
    echo "   📝 Placez vos PDFs dans data/pdfs/ manuellement"
fi
echo ""

# Étape 4: Configuration
echo "🔑 Étape 4/5: Configuration de l'API"
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "   ✅ Fichier .env créé depuis env.example"
        echo ""
        echo "   ⚠️  IMPORTANT: Éditez .env et ajoutez votre clé API Groq"
        echo "   📝 Obtenez une clé gratuite sur: https://console.groq.com/"
        echo ""
        echo "   Appuyez sur Entrée après avoir configuré .env..."
        read
    else
        echo "   ❌ env.example non trouvé"
        exit 1
    fi
else
    echo "   ℹ️  Fichier .env existant trouvé"
    
    # Vérification de la clé API
    if grep -q "GROQ_API_KEY=gsk_" .env 2>/dev/null; then
        echo "   ✅ Clé API Groq détectée"
    else
        echo "   ⚠️  Clé API non configurée dans .env"
        echo "   📝 Ajoutez: GROQ_API_KEY=gsk_votre_clé"
        echo ""
        echo "   Appuyez sur Entrée après avoir configuré .env..."
        read
    fi
fi
echo ""

# Étape 5: Ingestion des documents
echo "🔍 Étape 5/5: Création de l'index vectoriel"
if [ "$(ls -A data/pdfs/*.pdf 2>/dev/null)" ]; then
    echo "   ⏳ Ingestion en cours (peut prendre plusieurs minutes)..."
    if python3 ingest.py; then
        echo "   ✅ Index vectoriel créé avec succès"
    else
        echo "   ❌ Erreur lors de l'ingestion"
        echo "   Vérifiez que:"
        echo "      - Les PDFs sont dans data/pdfs/"
        echo "      - Les dépendances sont installées"
        exit 1
    fi
else
    echo "   ⚠️  Aucun PDF dans data/pdfs/"
    echo "   ⏭️  Étape d'ingestion ignorée"
    echo "   📝 Lancez 'python ingest.py' après avoir ajouté des PDFs"
fi
echo ""

# Résumé
echo "=============================================="
echo "✅ INSTALLATION TERMINÉE"
echo "=============================================="
echo ""
echo "🚀 Pour lancer l'application:"
echo ""
echo "   source venv/bin/activate"
echo "   streamlit run app.py"
echo ""
echo "📚 Documentation:"
echo "   • QUICKSTART.md - Démarrage rapide"
echo "   • README.md - Documentation complète"
echo "   • PROJET_COMPLET.md - Vue d'ensemble"
echo ""
echo "🧪 Test de sécurité (optionnel):"
echo "   python test_safety.py"
echo ""
echo "=============================================="
