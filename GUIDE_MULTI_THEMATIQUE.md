# Guide : Chatbot Multi-Thématique (Radiologie Interventionnelle)

## 📁 Organisation des fichiers

### Structure recommandée

```
data/
└── pdfs/
    ├── embolisation_prostate/
    │   ├── fiche_information.pdf
    │   ├── conseils_patient.pdf
    │   └── ...
    ├── embolisation_uterine/
    │   ├── info_fibrome.pdf
    │   └── ...
    ├── pose_pac/
    │   ├── guide_pac.pdf
    │   └── ...
    ├── biopsie_scanner/
    │   ├── preparation_biopsie.pdf
    │   └── ...
    ├── arthrose_genou/
    │   └── ...
    ├── epaule_gelee/
    │   └── ...
    ├── varicocele/
    │   └── ...
    ├── hemorroides/
    │   └── ...
    ├── douleurs_marche/
    │   └── ...
    ├── grosse_jambe/
    │   └── ...
    ├── cancer/
    │   └── ...
    └── douleurs_osseuses/
        └── ...
```

**Règle :** Chaque sous-dossier = une maladie/procédure. Le nom du dossier sera automatiquement détecté.

## 🚀 Étapes de déploiement

### 1. Organiser vos PDFs

```bash
# Créer les dossiers par maladie
mkdir -p data/pdfs/embolisation_prostate
mkdir -p data/pdfs/embolisation_uterine
mkdir -p data/pdfs/pose_pac
mkdir -p data/pdfs/biopsie_scanner
# ... etc pour toutes les maladies

# Déplacer vos PDFs dans les bons dossiers
# Exemple:
mv fichier_prostate.pdf data/pdfs/embolisation_prostate/
mv fichier_fibrome.pdf data/pdfs/embolisation_uterine/
```

### 2. Installer les nouvelles dépendances

```bash
pip install beautifulsoup4==4.12.3 lxml==5.1.0
```

Ou réinstaller toutes les dépendances :
```bash
pip install -r requirements.txt
```

### 3. Lancer l'ingestion

```bash
python ingest.py
```

**Ce que fait le script :**
1. ✅ Parcourt tous les sous-dossiers de `data/pdfs/`
2. ✅ Charge tous les PDFs avec détection automatique de la procédure
3. ✅ Scrape toutes les pages du site [laradiologiequisoigne.fr](https://www.laradiologiequisoigne.fr)
4. ✅ Combine PDFs + Web dans un seul index FAISS
5. ✅ Génère `vector_store/` avec index + chunks pour BM25

### 4. Lancer le chatbot

```bash
streamlit run app.py
```

Le chatbot aura maintenant accès à :
- ✅ Tous vos PDFs (organisés par maladie)
- ✅ Toutes les pages web du site HEGP
- ✅ Recherche hybride (vector + keyword)

## 📊 Vérification

Après l'ingestion, vous verrez des statistiques comme :

```
📊 Statistiques finales:
   • Documents sources: 45
     - PDFs: 35 pages
     - Web: 10 pages
   • Chunks créés: 523
   • Procédures couvertes: 12
     - Embolisation de la prostate: 156 chunks
     - Fibrome utérin: 89 chunks
     - Pose de PAC: 67 chunks
     - Biopsie sous scanner: 45 chunks
     - ...
```

## 🔧 Personnalisation

### Ajouter une nouvelle maladie

1. Créer un dossier : `data/pdfs/nouvelle_maladie/`
2. Ajouter les PDFs dedans
3. **Optionnel :** Ajouter l'URL web dans `ingest.py` (section `WEB_URLS`)
4. Relancer : `python ingest.py`

### Désactiver le scraping web

Si vous ne voulez que les PDFs, commentez dans `ingest.py` :

```python
# 2. Scraping du site web
# print("\n🌐 PHASE 2: Scraping du site web")
# web_documents = scrape_website()
# all_documents.extend(web_documents)
```

### Ajouter d'autres URLs

Dans `ingest.py`, section `WEB_URLS`, ajoutez :

```python
WEB_URLS = {
    # ... existantes
    "nouvelle_page": "https://www.laradiologiequisoigne.fr/nouvelle-page/",
}
```

## ⚠️ Limitations

- **Scraping web :** Nécessite connexion internet lors de l'ingestion
- **Mise à jour web :** Relancer `ingest.py` pour récupérer nouveau contenu
- **Encodage :** Si caractères spéciaux mal affichés, vérifier encodage PDFs

## 🆘 Dépannage

### Erreur : "No module named 'bs4'"
```bash
pip install beautifulsoup4
```

### Erreur de scraping web
- Vérifier connexion internet
- Le script continuera avec PDFs uniquement si scraping échoue

### PDFs non détectés
- Vérifier que fichiers sont bien `.pdf`
- Vérifier que dossiers sont dans `data/pdfs/`
- Essayer sans sous-dossiers (mettre PDFs directement dans `data/pdfs/`)

## 📝 Notes

- Le chatbot répondra automatiquement sur toutes les procédures
- Les sources (PDF ou web) seront citées dans les réponses
- Temps d'ingestion : 3-10 minutes selon nombre de documents
- Index généré : réutilisable, pas besoin de réingérer si pas de changement
