# 🚀 Guide de Mise à Jour - Améliorations RAG

## Nouvelles Fonctionnalités Ajoutées

✅ **Semantic Chunking** - Découpage intelligent basé sur la similarité sémantique  
✅ **Hybrid Retrieval** - Combinaison de recherche vectorielle (FAISS) et par mots-clés (BM25)  
✅ **Reciprocal Rank Fusion (RRF)** - Fusion intelligente des résultats  

---

## 📋 Étapes pour Activer les Améliorations

### Option 1: Automatique (Streamlit Cloud)

Les améliorations sont **déjà déployées** sur votre app Streamlit Cloud!

**Mais attention:** Le vector store existant utilise l'ancienne méthode. Pour bénéficier pleinement des améliorations, vous devez:

1. **Localement**, régénérer le vector store:
   ```bash
   cd "/Users/sassihoussem/Desktop/Assistant mécial - Embolisation de la prostate"
   
   # Installer les nouvelles dépendances
   pip install langchain-experimental==0.3.3 rank-bm25==0.2.2
   
   # Régénérer le vector store avec semantic chunking
   python ingest.py
   ```

2. **Commit et push** le nouveau vector store:
   ```bash
   git add vector_store/
   git commit -m "Update: Regenerate vector store with semantic chunking and BM25 support"
   git push origin main
   ```

3. **Streamlit Cloud** va automatiquement redéployer avec le nouveau vector store

---

### Option 2: Rapide (Utiliser l'ancien vector store temporairement)

L'application fonctionne **déjà** avec les améliorations, mais:
- ⚠️ Sans `chunks.pkl`, elle utilisera uniquement la recherche vectorielle (FAISS)
- ✅ Cela fonctionne toujours correctement!
- 💡 Pour activer le hybrid retrieval, suivez l'Option 1

---

## 🎯 Ce Qui a Changé

### 1. Semantic Chunking

**Avant:**
```
- Découpage fixe de 500 caractères
- Chunks peuvent couper au milieu d'une phrase
```

**Après:**
```
- Découpage basé sur la similarité sémantique
- Chunks respectent les limites sémantiques naturelles
- Taille variable adaptée au contenu
```

### 2. Hybrid Retrieval

**Avant:**
```
- Uniquement recherche vectorielle (embeddings)
- Peut manquer des mots-clés exacts
```

**Après:**
```
- 60% recherche vectorielle (sémantique)
- 40% recherche par mots-clés (BM25)
- Fusion des résultats avec RRF
- Meilleure précision et rappel
```

---

## 📊 Bénéfices Attendus

### Semantic Chunking
- ✅ Chunks plus cohérents sémantiquement
- ✅ Meilleure qualité des réponses
- ✅ Moins de coupures de contexte

### Hybrid Retrieval
- ✅ Trouve à la fois par sens ET par mots exacts
- ✅ Meilleure performance sur les termes médicaux spécifiques
- ✅ Résilience aux variations de formulation

---

## 🔍 Vérifier le Mode de Retrieval

Dans votre app, regardez la **sidebar** → section "Configuration technique":

```
Retrieval: Hybrid (Vector + Keyword)  ← ✅ Hybrid activé
```

ou

```
Retrieval: Vector Only  ← ⚠️ Uniquement vectoriel (chunks.pkl manquant)
```

---

## 🛠️ Paramètres Configurables

### Dans `ingest.py`

```python
USE_SEMANTIC_CHUNKING = True  # Activer/désactiver semantic chunking
```

### Dans `app.py` (HybridRetriever)

```python
alpha=0.6  # 60% vector, 40% keyword (ajustable entre 0 et 1)
```

**Recommandations:**
- `alpha=0.6`: Équilibré (défaut recommandé)
- `alpha=0.8`: Favoriser la sémantique
- `alpha=0.4`: Favoriser les mots-clés exacts

---

## 🐛 Dépannage

### Problème: "Vector Only" s'affiche

**Solution:** Régénérer le vector store (Option 1 ci-dessus)

### Problème: Erreur lors de `python ingest.py`

```bash
# Vérifier que toutes les dépendances sont installées
pip install -r requirements.txt

# Vérifier que les PDFs sont présents
ls data/pdfs/
```

### Problème: L'app Streamlit Cloud ne démarre pas

**Solution:** 
1. Vérifiez les logs dans Streamlit Cloud
2. Le `vector_store/chunks.pkl` doit être présent sur GitHub
3. Si manquant, l'app fonctionnera en mode "Vector Only"

---

## 📚 Documentation Technique

### Semantic Chunking
- Utilise `SemanticChunker` de LangChain
- Méthode: `breakpoint_threshold_type="percentile"`
- Seuil: 80% de similarité

### Hybrid Retrieval
- **Vector Search:** FAISS avec embeddings CamemBERT
- **Keyword Search:** BM25 (Okapi variant)
- **Fusion:** Reciprocal Rank Fusion (RRF)
- **Formule RRF:** `score = 1 / (rank + 60)`

### Fichiers Générés

```
vector_store/
├── index.faiss       # Index vectoriel FAISS
├── index.pkl         # Métadonnées FAISS
└── chunks.pkl        # Chunks pour BM25 (nouveau!)
```

---

## 🎯 Prochaines Étapes

1. ✅ **Tester l'app actuelle** - fonctionne déjà!
2. ⭐ **Régénérer le vector store** - pour activer le hybrid retrieval
3. 📊 **Comparer les performances** - avant/après
4. ⚙️ **Ajuster alpha** - si nécessaire selon les résultats

---

## ℹ️ Support

Questions? Vérifiez:
- Les logs dans Streamlit Cloud
- Le mode de retrieval dans la sidebar
- Que `chunks.pkl` existe dans `vector_store/`

**L'application fonctionne dans tous les cas**, avec ou sans hybrid retrieval!
