# 🏥 Assistant Médical RAG - Embolisation de la Prostate

## 📋 Description

Assistant conversationnel basé sur la **Retrieval-Augmented Generation (RAG)** pour fournir des informations générales aux patients avant et après une embolisation de la prostate.

### ⚠️ Avertissement Important

**Ce projet est un POC (Proof of Concept) à des fins de recherche et d'évaluation uniquement.**

- ✅ Fournit des informations générales basées sur des documents médicaux validés
- ❌ **Ne remplace PAS une consultation médicale**
- ❌ **Ne donne PAS de diagnostic**
- ❌ **Ne fournit PAS de conseils personnalisés**

---

## 🎯 Fonctionnalités

### Sécurité Médicale
- ✅ **RAG strict** : répond uniquement à partir des documents fournis
- ✅ **Pas d'hallucinations** : refuse de répondre si l'information n'est pas dans les documents
- ✅ **Détection de données personnelles** : refuse automatiquement les questions contenant des informations personnelles
- ✅ **Consentement obligatoire** : écran de conditions d'utilisation avant l'accès au chat

### Interface
- 🌐 **Interface web** avec Streamlit (facilement partageable)
- 💬 **Chat conversationnel** avec historique
- 📚 **Citations des sources** : affiche les extraits de documents utilisés pour chaque réponse
- 🇫🇷 **100% français** : interface et réponses en français

### Technique
- 🧠 **Embeddings français** : modèle CamemBERT optimisé
- 🔍 **FAISS** : recherche vectorielle locale (pas de base de données externe)
- 🤖 **LLM configurable** : supporte OpenAI et Groq
- 📊 **Métadonnées enrichies** : tracking des sources et procédures

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                   PDFs fournis                   │
│  (Documents validés sur l'embolisation prostate) │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
         ┌───────────────┐
         │  ingest.py    │  Découpage + Embeddings
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │  FAISS Index  │  Base vectorielle locale
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │    app.py     │  Interface Streamlit
         └───────┬───────┘
                 │
     ┌───────────┼───────────┐
     ▼           ▼           ▼
Consentement  Chat RAG   Sources
```

---

## 📦 Installation

### Prérequis

- Python 3.9 ou supérieur
- Clé API pour un LLM (OpenAI ou Groq)

### Étape 1 : Cloner ou télécharger le projet


### Étape 2 : Créer un environnement virtuel (recommandé)

```bash
python -m venv venv
source venv/bin/activate  # Sur macOS/Linux
# ou
venv\Scripts\activate  # Sur Windows
```

### Étape 3 : Installer les dépendances

```bash
pip install -r requirements.txt
```

⏳ **Note** : La première installation peut prendre plusieurs minutes (téléchargement des modèles d'embeddings).

### Étape 4 : Configurer les variables d'environnement

1. Copiez le fichier d'exemple :
```bash
cp env.example .env
```

2. Éditez `.env` et ajoutez votre clé API :

**Option A : Groq (gratuit, recommandé pour le développement)**
```bash
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_votre_clé_ici
MODEL_NAME=llama-3.1-70b-versatile
```

Obtenez une clé gratuite sur : https://console.groq.com/

**Option B : OpenAI (payant)**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-votre_clé_ici
MODEL_NAME=gpt-3.5-turbo
```

### Étape 5 : Ajouter vos documents PDF

Placez vos PDFs dans le dossier `data/pdfs/` :

```bash
mkdir -p data/pdfs
# Copiez vos PDFs dans data/pdfs/
```

**Format des PDFs attendus :**
- Documents en français
- Relatifs à l'embolisation de la prostate
- Orientés patients (pré-op, post-op, FAQ)
- Validés par des professionnels de santé

---

## 🚀 Utilisation

### Étape 1 : Ingestion des documents

Créez l'index vectoriel à partir de vos PDFs :

```bash
python ingest.py
```

**Sortie attendue :**
```
======================================================================
🏥 INGESTION DES DOCUMENTS MÉDICAUX
   Embolisation de la prostate - Base de connaissances RAG
======================================================================

📄 3 fichier(s) PDF trouvé(s):
   • Embolisation_prostate_info_patient.pdf
   • Guide_preoperatoire.pdf
   • FAQ_postoperatoire.pdf

📖 Chargement de: Embolisation_prostate_info_patient.pdf
   ✅ 12 page(s) chargée(s)
...

✅ INGESTION TERMINÉE AVEC SUCCÈS
```

**Note** : Cette étape ne doit être exécutée qu'une seule fois, ou lorsque vous modifiez les PDFs.

### Étape 2 : Lancer l'application

```bash
streamlit run app.py
```

**L'application s'ouvrira automatiquement dans votre navigateur** à l'adresse :
```
http://localhost:8501
```

### Étape 3 : Utiliser le chatbot

1. **Accepter les conditions d'utilisation** (obligatoire)
2. **Poser des questions générales**, par exemple :
   - "Qu'est-ce que l'embolisation de la prostate ?"
   - "Quels sont les effets secondaires possibles ?"
   - "Combien de temps dure la convalescence ?"
   - "Quelles sont les précautions avant l'intervention ?"

3. **Consulter les sources** : cliquez sur "📚 Sources utilisées" pour voir les extraits de documents

---

## 🔒 Règles de Sécurité

### ❌ Questions Refusées

Le chatbot refuse automatiquement les questions contenant des données personnelles :

**Exemples de questions refusées :**
- "J'ai 70 ans, puis-je faire cette intervention ?"
- "Je prends du Kardegic, dois-je l'arrêter ?"
- "Dans mon cas, quels sont les risques ?"
- "Mon médecin m'a dit que... est-ce normal ?"

**Réponse type :**
> 🔒 Je ne peux pas traiter d'informations personnelles.
> Merci de poser uniquement des questions générales.

### ✅ Questions Acceptées

**Exemples de questions valides :**
- "Qu'est-ce que l'embolisation de la prostate ?"
- "Quels sont les effets secondaires courants ?"
- "Combien de temps dure l'hospitalisation généralement ?"
- "Quels examens sont faits avant l'intervention ?"

---

## 🌐 Déploiement (Partage avec d'autres)

### Option 1 : Streamlit Community Cloud (Gratuit)

**Avantages :** Gratuit, facile, accessible en ligne

**Étapes :**

1. **Créer un compte sur** [Streamlit Community Cloud](https://streamlit.io/cloud)

2. **Pousser le projet sur GitHub** :
```bash
git init
git add .
git commit -m "Initial commit - Assistant RAG embolisation prostate"
git branch -M main
git remote add origin https://github.com/votre-username/assistant-embolisation.git
git push -u origin main
```

3. **Déployer depuis Streamlit Cloud** :
   - Connectez-vous à Streamlit Cloud
   - Cliquez sur "New app"
   - Sélectionnez votre repository GitHub
   - Fichier principal : `app.py`
   - Ajoutez vos secrets (clés API) dans "Advanced settings" → "Secrets"

4. **Configurer les secrets** :
```toml
# Dans l'interface Streamlit Cloud, section "Secrets"
GROQ_API_KEY = "gsk_votre_clé"
LLM_PROVIDER = "groq"
MODEL_NAME = "llama-3.1-70b-versatile"
TEMPERATURE = "0.1"
```

5. **Partager le lien** généré (ex: `https://votre-app.streamlit.app`)

### Option 2 : Partage Local (Réseau)

Pour partager sur votre réseau local :

```bash
streamlit run app.py --server.address 0.0.0.0
```

Les autres utilisateurs peuvent accéder via :
```
http://votre_ip_locale:8501
```

---

## ⚙️ Configuration Avancée

### Variables d'environnement (.env)

| Variable | Description | Défaut | Valeurs possibles |
|----------|-------------|--------|-------------------|
| `LLM_PROVIDER` | Fournisseur LLM | `groq` | `openai`, `groq` |
| `MODEL_NAME` | Modèle à utiliser | `llama-3.1-70b-versatile` | Voir ci-dessous |
| `TEMPERATURE` | Créativité du modèle | `0.1` | `0.0` - `1.0` (médical : 0.0-0.3) |
| `TOP_K_RETRIEVAL` | Nombre de documents récupérés | `4` | `1` - `10` |
| `CHUNK_SIZE` | Taille des chunks | `500` | `200` - `1000` |
| `CHUNK_OVERLAP` | Chevauchement | `50` | `0` - `200` |

### Modèles disponibles

**Groq (gratuit) :**
- `llama-3.1-70b-versatile` ✅ Recommandé
- `llama-3.1-8b-instant` (plus rapide, moins précis)
- `mixtral-8x7b-32768`

**OpenAI (payant) :**
- `gpt-3.5-turbo` (économique)
- `gpt-4` (plus précis, plus cher)
- `gpt-4-turbo`

---

## 🧪 Tests et Validation

### Tests de sécurité

Testez que le système refuse les données personnelles :

```python
# Questions à tester (doivent être refusées)
questions_test = [
    "J'ai 65 ans, puis-je faire cette opération ?",
    "Je prends du Plavix, dois-je l'arrêter ?",
    "Dans mon cas, quels sont les risques ?",
]
```

### Tests de RAG strict

Testez que le système ne répond que depuis les documents :

```python
# Question hors documents (doit dire "information non disponible")
"Quel est le coût de l'intervention ?"  # Si non dans les PDFs
```

### Tests fonctionnels

```python
# Questions générales (doivent recevoir une réponse)
questions_valides = [
    "Qu'est-ce que l'embolisation de la prostate ?",
    "Quels sont les effets secondaires courants ?",
    "Combien de temps dure l'hospitalisation ?",
]
```

---

## 📁 Structure du Projet

```
Assistant médical - Embolisation de la prostate/
│
├── data/
│   └── pdfs/                      # Vos documents PDF sources
│       ├── Document1.pdf
│       └── Document2.pdf
│
├── vector_store/                  # Index FAISS (généré par ingest.py)
│   ├── index.faiss
│   └── index.pkl
│
├── ingest.py                      # Script d'ingestion des PDFs
├── app.py                         # Application Streamlit principale
├── requirements.txt               # Dépendances Python
├── env.example                    # Template de configuration
├── .env                          # Votre configuration (non versionné)
├── .gitignore                    # Fichiers à ignorer
└── README.md                     # Ce fichier
```

---

## 🐛 Dépannage

### Erreur : "Index vectoriel non trouvé"

**Cause :** `python ingest.py` n'a pas été exécuté.

**Solution :**
```bash
python ingest.py
```

### Erreur : "Clé API non trouvée"

**Cause :** Le fichier `.env` n'est pas configuré.

**Solution :**
1. Copiez `env.example` vers `.env`
2. Ajoutez votre clé API dans `.env`

### Erreur : "Aucun fichier PDF trouvé"

**Cause :** Le dossier `data/pdfs/` est vide.

**Solution :**
```bash
mkdir -p data/pdfs
# Copiez vos PDFs dans ce dossier
```

### Performances lentes

**Optimisations possibles :**
1. Réduire `TOP_K_RETRIEVAL` dans `.env` (ex: 3 au lieu de 4)
2. Utiliser un modèle plus rapide (ex: `llama-3.1-8b-instant`)
3. Augmenter `CHUNK_SIZE` pour réduire le nombre de chunks

### L'assistant hallucine (invente des réponses)

**Solutions :**
1. Réduire `TEMPERATURE` à 0.0 dans `.env`
2. Améliorer le prompt système dans `app.py`
3. Vérifier que les PDFs contiennent bien l'information

---

## 🔐 Confidentialité et RGPD

### Données collectées

**Par l'application :**
- ❌ Aucune donnée personnelle stockée
- ✅ Conversations en mémoire uniquement (effacées à la fermeture)
- ✅ Pas de base de données externe
- ✅ Tout est local (sauf appels API LLM)

**Par les fournisseurs LLM :**
- **Groq** : Politique de confidentialité sur groq.com
- **OpenAI** : Politique de confidentialité sur openai.com

**Recommandation RGPD :**
- Informez les utilisateurs que les conversations transitent par un LLM tiers
- Ajoutez une mention dans les conditions d'utilisation
- Pour un usage en production hospitalière, envisagez un LLM auto-hébergé

---

## 📚 Documentation Technique

### Stack Technique

| Composant | Technologie | Rôle |
|-----------|------------|------|
| Interface | Streamlit | Application web interactive |
| Embeddings | CamemBERT | Vectorisation français |
| Vector Store | FAISS | Recherche de similarité |
| Orchestration | LangChain | Pipeline RAG |
| LLM | Groq/OpenAI | Génération de réponses |
| PDF Processing | PyPDF | Extraction de texte |

### Flux RAG

```
Question utilisateur
     │
     ▼
Détection données personnelles
     │
     ├─ OUI ──> Refus
     │
     ▼ NON
Vectorisation de la question
     │
     ▼
Recherche dans FAISS (top-k chunks)
     │
     ▼
Prompt système + Context + Question
     │
     ▼
LLM génère réponse
     │
     ▼
Affichage + Sources
```

---

## 🤝 Contribution et Support

### Améliorer le système

**Pistes d'amélioration :**
1. Ajouter plus de documents PDF
2. Ajuster les paramètres de chunking
3. Améliorer le prompt système
4. Ajouter des patterns de détection de données personnelles
5. Tester différents modèles d'embeddings

### Support

Pour toute question technique :
1. Vérifiez d'abord la section "Dépannage"
2. Consultez les logs Streamlit
3. Vérifiez la configuration `.env`

---

## ⚖️ Licence et Usage

**Ce projet est un POC à des fins de recherche et d'évaluation.**

### Limitations légales
- ❌ Ne constitue pas un dispositif médical
- ❌ Ne remplace pas une consultation médicale
- ❌ Aucune garantie de précision médicale
- ❌ Utilisation à vos propres risques

### Usage autorisé
- ✅ Recherche académique
- ✅ Évaluation et tests
- ✅ Démonstration de concept RAG
- ✅ Formation et sensibilisation

### Usage en production hospitalière
**Avant toute mise en production :**
1. Validation médicale complète
2. Audit de sécurité
3. Conformité RGPD
4. Déclaration auprès des autorités compétentes (selon juridiction)
5. Assurance responsabilité civile

---

## 📞 Contact

Pour toute question sur l'aspect médical de ce projet, consultez les professionnels de santé de votre établissement.

Pour l'aspect technique : voir section "Contribution et Support".

---

## 🙏 Remerciements

Ce projet utilise :
- **Streamlit** pour l'interface web
- **LangChain** pour l'orchestration RAG
- **FAISS** (Meta AI) pour la recherche vectorielle
- **CamemBERT** pour les embeddings français
- **Groq/OpenAI** pour les LLMs

Merci à tous les contributeurs de ces projets open source.

---

**Version :** 1.0.0  
**Dernière mise à jour :** Janvier 2026  
**Statut :** POC - Proof of Concept
