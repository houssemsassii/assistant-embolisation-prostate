# 🚀 Guide de Démarrage Rapide

## Installation en 5 minutes

### 1️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```

### 2️⃣ Configurer la clé API

Copiez le fichier de configuration :
```bash
cp env.example .env
```

Éditez `.env` et ajoutez votre clé API Groq (gratuite) :

```bash
# Obtenez votre clé sur : https://console.groq.com/
GROQ_API_KEY=gsk_votre_clé_ici
```

### 3️⃣ Ajouter vos PDF

Placez vos documents PDF dans :
```
data/pdfs/
```

### 4️⃣ Créer l'index vectoriel

```bash
python ingest.py
```

Attendez le message : ✅ **INGESTION TERMINÉE AVEC SUCCÈS**

### 5️⃣ Lancer l'application

```bash
streamlit run app.py
```

L'application s'ouvre automatiquement dans votre navigateur ! 🎉

---

## ⚡ Commandes Essentielles

| Commande | Description |
|----------|-------------|
| `python ingest.py` | Créer/mettre à jour l'index (après ajout de PDFs) |
| `streamlit run app.py` | Lancer l'application web |
| `pip install -r requirements.txt` | Installer les dépendances |

---

## 🐛 Problème ?

### L'application ne démarre pas
```bash
# Vérifiez que les dépendances sont installées
pip install -r requirements.txt
```

### "Index vectoriel non trouvé"
```bash
# Lancez l'ingestion
python ingest.py
```

### "Clé API non trouvée"
```bash
# Vérifiez votre fichier .env
cat .env
# Doit contenir : GROQ_API_KEY=gsk_...
```

---

## 📚 Documentation Complète

Consultez le [README.md](README.md) pour :
- Configuration avancée
- Déploiement en ligne
- Tests de sécurité
- Dépannage détaillé

---

**Bon test ! 🏥**
