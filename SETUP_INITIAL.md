# 🎯 Configuration Initiale du Projet

## ✅ Préparation de vos documents PDF

J'ai détecté que vous avez déjà des documents PDF dans le dossier `Documents/`.

### Option 1 : Déplacer les PDFs (recommandé)

```bash
# Déplacer tous les PDFs vers data/pdfs/
mv Documents/*.pdf data/pdfs/

# Vérifier que les fichiers sont bien là
ls -la data/pdfs/
```

### Option 2 : Copier les PDFs (garder l'original)

```bash
# Copier tous les PDFs vers data/pdfs/
cp Documents/*.pdf data/pdfs/

# Vérifier que les fichiers sont bien là
ls -la data/pdfs/
```

### PDFs détectés :
- ✅ Embolisation-de-la-prostate-EN-SAVOIR-PLUS.pdf
- ✅ Fiche-conseil-Embollisation-de-la-prostate.pdf
- ✅ FIP_RB_EmbolisationArteresProstatiques_042025.pdf
- ✅ INFO-embolisation arteres prostatiques (arteriel).pdf
- ✅ PIM0073 Embolisation de prostate.pdf

**Excellent ! Vous avez 5 documents, c'est parfait pour commencer. 🎉**

---

## 🔑 Configuration de la clé API

### Étape 1 : Obtenir une clé API Groq (GRATUIT)

1. Allez sur : https://console.groq.com/
2. Créez un compte (gratuit)
3. Accédez à "API Keys"
4. Créez une nouvelle clé
5. Copiez la clé (commence par `gsk_...`)

### Étape 2 : Configurer le projet

```bash
# Créer le fichier .env
cp env.example .env

# Éditer le fichier .env avec votre éditeur préféré
nano .env
# ou
open .env
```

Ajoutez votre clé dans le fichier `.env` :

```bash
GROQ_API_KEY=gsk_VOTRE_CLÉ_ICI

LLM_PROVIDER=groq
MODEL_NAME=llama-3.1-70b-versatile
TEMPERATURE=0.1
TOP_K_RETRIEVAL=4
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

---

## 📦 Installation des dépendances

```bash
# Créer un environnement virtuel (recommandé)
python3 -m venv venv

# Activer l'environnement virtuel
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

**Note** : La première installation peut prendre 5-10 minutes (téléchargement des modèles d'embeddings).

---

## 🚀 Premier lancement

### 1️⃣ Préparer les documents

```bash
# Si vous n'avez pas encore déplacé/copié les PDFs :
cp Documents/*.pdf data/pdfs/
```

### 2️⃣ Créer l'index vectoriel

```bash
python ingest.py
```

**Attendez la fin de l'ingestion** (peut prendre quelques minutes).

Vous devriez voir :
```
✅ INGESTION TERMINÉE AVEC SUCCÈS
📊 Statistiques:
   • Documents traités: X pages
   • Chunks créés: Y
```

### 3️⃣ Lancer l'application

```bash
streamlit run app.py
```

L'application s'ouvre automatiquement dans votre navigateur à l'adresse :
```
http://localhost:8501
```

---

## ✅ Checklist de vérification

Avant le premier lancement, vérifiez que :

- [ ] Les PDFs sont dans `data/pdfs/`
- [ ] Le fichier `.env` existe et contient votre clé API
- [ ] Les dépendances sont installées (`pip install -r requirements.txt`)
- [ ] L'ingestion a réussi (`python ingest.py`)
- [ ] Le dossier `vector_store/` a été créé

---

## 🧪 Test de sécurité (optionnel)

Pour vérifier que le système refuse bien les données personnelles :

```bash
python test_safety.py
```

Vous devriez voir :
```
✅ Tous les tests sont passés !
```

---

## 🎉 Vous êtes prêt !

Une fois ces étapes complétées :

```bash
streamlit run app.py
```

Et testez avec des questions comme :
- "Qu'est-ce que l'embolisation de la prostate ?"
- "Quels sont les effets secondaires courants ?"
- "Combien de temps dure la convalescence ?"

---

## ❓ Problème au démarrage ?

### Erreur : "Index vectoriel non trouvé"
→ Relancez : `python ingest.py`

### Erreur : "Clé API non trouvée"
→ Vérifiez votre fichier `.env`

### Erreur : "Aucun PDF trouvé"
→ Déplacez vos PDFs : `cp Documents/*.pdf data/pdfs/`

### Import Error
→ Réinstallez : `pip install -r requirements.txt`

---

**Besoin d'aide ?** Consultez le [README.md](README.md) pour plus de détails.
