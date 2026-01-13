# 🎯 COMMENCEZ ICI

## Bienvenue dans votre Assistant Médical RAG !

Ce projet est **100% prêt à l'emploi**. Suivez simplement les étapes ci-dessous.

---

## 🚀 Installation Rapide (2 options)

### Option A : Installation Automatique (Recommandé)

```bash
bash setup.sh
```

Le script va :
1. ✅ Créer l'environnement virtuel
2. ✅ Installer les dépendances
3. ✅ Copier vos PDFs
4. ✅ Configurer l'API (avec votre aide)
5. ✅ Créer l'index vectoriel

### Option B : Installation Manuelle

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Copier vos PDFs
cp Documents/*.pdf data/pdfs/

# 3. Configurer l'API
cp env.example .env
# Éditez .env et ajoutez votre clé Groq (gratuite sur console.groq.com)

# 4. Créer l'index
python ingest.py

# 5. Lancer l'app
streamlit run app.py
```

---

## 🔑 Obtenir votre clé API (GRATUIT)

1. Allez sur : **https://console.groq.com/**
2. Créez un compte (email + mot de passe)
3. Cliquez sur "API Keys"
4. Créez une nouvelle clé
5. Copiez la clé (commence par `gsk_`)
6. Collez-la dans `.env` :

```bash
GROQ_API_KEY=gsk_votre_clé_ici
```

---

## ✅ Vérification Rapide

Avant de lancer, vérifiez que :

- [ ] Les PDFs sont dans `data/pdfs/` (5 détectés)
- [ ] Le fichier `.env` existe et contient `GROQ_API_KEY=gsk_...`
- [ ] L'ingestion a réussi (dossier `vector_store/` créé)

---

## 🎉 Lancement

```bash
streamlit run app.py
```

L'application s'ouvre dans votre navigateur !

**Testez avec :**
- "Qu'est-ce que l'embolisation de la prostate ?"
- "Quels sont les effets secondaires ?"
- "Combien de temps dure la convalescence ?"

---

## 📚 Documentation Disponible

| Fichier | Quand l'utiliser |
|---------|------------------|
| **START_HERE.md** | 👈 Vous êtes ici ! |
| **SETUP_INITIAL.md** | Configuration détaillée |
| **QUICKSTART.md** | Aide-mémoire des commandes |
| **README.md** | Documentation complète |
| **PROJET_COMPLET.md** | Vue d'ensemble du projet |

---

## 🆘 Besoin d'Aide ?

### L'application ne démarre pas
→ Consultez [`SETUP_INITIAL.md`](SETUP_INITIAL.md)

### "Index vectoriel non trouvé"
```bash
python ingest.py
```

### "Clé API non trouvée"
```bash
# Vérifiez votre .env
cat .env
```

### Autres problèmes
→ Section "🐛 Dépannage" dans [`README.md`](README.md)

---

## 🎯 Prochaines Étapes

Après le premier lancement :

1. ✅ Testez le consentement obligatoire
2. ✅ Vérifiez le refus des données personnelles
3. ✅ Consultez les sources affichées
4. ✅ Lancez les tests de sécurité : `python test_safety.py`
5. ✅ Partagez avec d'autres (voir déploiement dans README.md)

---

**Bon test ! 🏥**

Questions ? Consultez la documentation complète dans [`README.md`](README.md)
