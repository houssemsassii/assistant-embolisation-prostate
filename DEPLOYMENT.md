# Guide de Déploiement - Assistant Embolisation de la Prostate

## Option 1: Streamlit Community Cloud (Recommandé - Gratuit)

### Étape 1: Préparer votre code

1. **Créer un fichier `.streamlit/config.toml`** pour la configuration:
```bash
mkdir -p .streamlit
```

2. **Créer `.gitignore`** pour exclure les fichiers sensibles:
```
.env
*.pyc
__pycache__/
.DS_Store
*.bak
```

3. **S'assurer que tous les fichiers nécessaires sont présents:**
   - `app.py` ✓
   - `ingest.py` ✓
   - `requirements.txt` ✓
   - `data/pdfs/` avec vos PDF ✓
   - `vector_store/` (à générer)

### Étape 2: Générer le vector store

**IMPORTANT:** Vous devez générer le vector store AVANT de déployer:

```bash
python ingest.py
```

Cela créera le dossier `vector_store/` avec:
- `index.faiss`
- `index.pkl`

**Ces fichiers DOIVENT être inclus dans votre repository Git.**

### Étape 3: Créer un repository GitHub

1. Allez sur https://github.com et créez un nouveau repository (public ou privé)
2. Nommez-le par exemple: `assistant-embolisation-prostate`

3. Initialisez Git dans votre projet:
```bash
cd "/Users/sassihoussem/Desktop/Assistant mécial - Embolisation de la prostate"
git init
git add .
git commit -m "Initial commit - Assistant médical embolisation prostate"
```

4. Connectez à GitHub:
```bash
git remote add origin https://github.com/VOTRE_USERNAME/assistant-embolisation-prostate.git
git branch -M main
git push -u origin main
```

### Étape 4: Déployer sur Streamlit Community Cloud

1. **Allez sur:** https://streamlit.io/cloud
2. **Connectez-vous** avec votre compte GitHub
3. **Cliquez sur "New app"**
4. **Sélectionnez:**
   - Repository: `VOTRE_USERNAME/assistant-embolisation-prostate`
   - Branch: `main`
   - Main file path: `app.py`

5. **Configurez les Secrets** (IMPORTANT pour l'API Groq):
   - Cliquez sur "Advanced settings"
   - Dans la section "Secrets", ajoutez:
   ```toml
   GROQ_API_KEY = "your-groq-api-key-here"
   MODEL_NAME = "llama-3.3-70b-versatile"
   LLM_PROVIDER = "groq"
   TOP_K_RETRIEVAL = "4"
   TEMPERATURE = "0.1"
   ```

6. **Cliquez sur "Deploy"**

### Étape 5: Partager l'URL

Une fois déployé, vous recevrez une URL comme:
```
https://VOTRE_APP.streamlit.app
```

Partagez cette URL avec qui vous voulez!

---

## Option 2: Hugging Face Spaces (Alternative gratuite)

1. Créez un compte sur https://huggingface.co
2. Créez un nouveau Space (type: Streamlit)
3. Uploadez vos fichiers
4. Configurez les secrets dans Settings > Repository secrets

---

## Option 3: Partage Local (Temporaire)

Si vous voulez juste tester rapidement avec quelqu'un sur votre réseau:

1. L'application tourne déjà sur: `http://192.168.1.119:8501`
2. Partagez cette URL avec des personnes sur le **même réseau WiFi**
3. Votre ordinateur doit rester allumé

**⚠️ Limitations:**
- Fonctionne uniquement sur votre réseau local
- Votre ordinateur doit rester allumé
- Pas accessible depuis Internet

---

## ⚠️ Considérations Importantes

### Sécurité de l'API Key
- **NE JAMAIS** commiter le fichier `.env` sur GitHub
- Utilisez toujours les "Secrets" de Streamlit Cloud
- Votre clé API Groq a des limites d'utilisation gratuites

### Limites de Groq (Free Tier)
- **14,400 requêtes par jour** avec llama-3.3-70b-versatile
- Si vous avez beaucoup d'utilisateurs, surveillez votre usage sur https://console.groq.com

### Taille du Repository
- Les fichiers PDF sont inclus, assurez-vous qu'ils ne sont pas trop volumineux
- GitHub a une limite de 100 MB par fichier
- Le vector store est généralement petit (quelques MB)

### Protection des Données
- L'application est déjà configurée pour refuser les données personnelles
- Les conversations ne sont pas sauvegardées par défaut
- Streamlit Cloud ne stocke pas les conversations

---

## 🚀 Commandes Rapides

### Déploiement complet en quelques commandes:

```bash
# 1. Générer le vector store
python ingest.py

# 2. Créer .gitignore
echo -e ".env\n*.pyc\n__pycache__/\n.DS_Store\n*.bak" > .gitignore

# 3. Initialiser Git et pusher
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/VOTRE_USERNAME/VOTRE_REPO.git
git push -u origin main

# 4. Déployer sur Streamlit Cloud (via interface web)
```

---

## 📞 Support

Pour plus d'informations:
- Streamlit Docs: https://docs.streamlit.io/streamlit-community-cloud
- Groq API Docs: https://console.groq.com/docs
- Hugging Face Spaces: https://huggingface.co/docs/hub/spaces
