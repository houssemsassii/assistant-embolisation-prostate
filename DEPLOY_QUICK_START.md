# 🚀 Déploiement Rapide - 5 Minutes

## Méthode la Plus Simple: Streamlit Community Cloud (100% Gratuit)

### ✅ Prérequis
- Compte GitHub (gratuit): https://github.com/signup
- Clé API Groq (déjà configurée dans votre .env)

---

## 📦 Étape 1: Vérifier que le vector store existe

```bash
cd "/Users/sassihoussem/Desktop/Assistant mécial - Embolisation de la prostate"

# Vérifier si le dossier existe
ls -la vector_store/
```

**Si le dossier n'existe pas ou est vide:**
```bash
python ingest.py
```

✅ Vous devriez voir: `vector_store/index.faiss` et `vector_store/index.pkl`

---

## 🌐 Étape 2: Créer un repository GitHub

### Option A: Via l'interface web (Plus facile)

1. Allez sur https://github.com/new
2. Nom du repository: `assistant-embolisation-prostate`
3. Choisissez "Private" ou "Public"
4. **NE PAS** cocher "Add README"
5. Cliquez "Create repository"

### Option B: Via terminal

```bash
# Dans votre dossier projet
cd "/Users/sassihoussem/Desktop/Assistant mécial - Embolisation de la prostate"

# Initialiser Git
git init
git add .
git commit -m "Assistant médical - Embolisation de la prostate"

# Connecter à GitHub (remplacez USERNAME et REPO)
git remote add origin https://github.com/USERNAME/REPO.git
git branch -M main
git push -u origin main
```

---

## ☁️ Étape 3: Déployer sur Streamlit Cloud

1. **Aller sur:** https://share.streamlit.io/

2. **Se connecter** avec GitHub

3. **Cliquer** sur "New app"

4. **Remplir le formulaire:**
   - Repository: `USERNAME/assistant-embolisation-prostate`
   - Branch: `main`
   - Main file path: `app.py`

5. **Cliquer** sur "Advanced settings"

6. **Dans "Secrets", copier-coller ceci:**
   ```toml
   GROQ_API_KEY = "your-groq-api-key-here"
   MODEL_NAME = "llama-3.3-70b-versatile"
   LLM_PROVIDER = "groq"
   TOP_K_RETRIEVAL = "4"
   TEMPERATURE = "0.1"
   ```

7. **Cliquer** "Deploy!"

---

## ✅ Étape 4: Partager l'URL

Après 2-5 minutes, vous recevrez une URL comme:
```
https://username-assistant-embolisation-prostate-abc123.streamlit.app
```

🎉 **C'est tout!** Partagez cette URL avec qui vous voulez!

---

## 🔧 Mises à Jour

Pour mettre à jour l'application déployée:

```bash
# Faire vos modifications
# Puis:
git add .
git commit -m "Description des changements"
git push

# L'app se redéploie automatiquement en 1-2 minutes!
```

---

## ⚠️ IMPORTANT: Sécurité API

### ❌ ÉVITEZ de partager trop largement
Votre clé API Groq gratuite a des limites:
- **14,400 requêtes/jour** pour llama-3.3-70b-versatile
- Si trop d'utilisateurs → vous atteindrez la limite

### 📊 Surveiller l'usage
Vérifiez votre usage sur: https://console.groq.com/usage

### 💡 Solutions si vous dépassez:
1. **Créer un compte Groq payant** ($0.20 par million tokens)
2. **Limiter l'accès** (partager avec un groupe restreint)
3. **Utiliser OpenAI** à la place (modifier .env)

---

## 🆘 Dépannage

### Erreur: "ModuleNotFoundError"
→ Vérifiez que `requirements.txt` contient tous les packages

### Erreur: "Vector store not found"
→ Assurez-vous que `vector_store/` est bien dans le repository GitHub

### Erreur: "API key not found"
→ Vérifiez que les Secrets sont bien configurés dans Streamlit Cloud

### L'app ne démarre pas
→ Vérifiez les logs dans l'interface Streamlit Cloud

---

## 🎯 Alternatives Rapides

### Hugging Face Spaces
1. https://huggingface.co/spaces
2. "Create new Space" → Type: Streamlit
3. Upload vos fichiers
4. Ajouter secrets dans Settings

### Railway (Gratuit avec limites)
1. https://railway.app
2. Connect GitHub repo
3. Deploy automatiquement

---

## 📞 Besoin d'aide?

- Documentation Streamlit Cloud: https://docs.streamlit.io/streamlit-community-cloud
- Support Streamlit: https://discuss.streamlit.io
- Issues GitHub: Créez un issue dans votre repo
