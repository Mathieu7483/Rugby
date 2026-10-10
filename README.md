<p align="center"\>
<img src="https://github.com/Mathieu7483/Rugby-Predictor-WC2027/blob/main/World%20rugby%20prediction%202027.jpg"\>
</p>

---

# Rugby Predictor - WC 2027

Prédiction des résultats de matchs internationaux de rugby à l'aide de modèles de Machine Learning entraînés sur l'intégralité des données historiques du rugby international.

---

## 📋 Table des matières

1. [À propos du projet](https://github.com/Mathieu7483/Rugby-Predictor-WC2027#-%C3%A0-propos-du-projet)
2. [Structure du projet](https://github.com/Mathieu7483/Rugby-Predictor-WC2027#%EF%B8%8F-structure-du-projet)
3. [Pipeline de Machine Learning](https://github.com/Mathieu7483/Rugby-Predictor-WC2027#%EF%B8%8F-pipeline-de-machine-learning)
4. [Installation et Prérequis](https://github.com/Mathieu7483/Rugby-Predictor-WC2027#%EF%B8%8F-installation-et-pr%C3%A9requis)
5. [Utilisation](https://github.com/Mathieu7483/Rugby-Predictor-WC2027#-utilisation)
6. [Interface Web](https://github.com/Mathieu7483/Rugby-Predictor-WC2027#-interface-web)

---

## 🎯 À propos du projet

Ce projet vise à modéliser et prédire l'issue des rencontres internationales de rugby en s'appuyant sur un dataset exhaustif retraçant l'historique de ce sport depuis ses débuts. En exploitant des algorithmes de Machine Learning, le système analyse les performances passées pour estimer les probabilités de victoire, de défaite ou de match nul, avec un regard tourné vers la Coupe du Monde 2027.

---

## 🗂️ Structure du projet

```text
mathieu7483-rugby/
├── README.md
├── export_predictions.py
├── index.html
├── predict.py
├── train_and_save.py
├── train_model.py
└── web/
    └── predictions.js

```

* **`train_model.py` / `train_and_save.py**` : Scripts dédiés au chargement du dataset historique, au traitement des données (feature engineering), à l'entraînement et à la persistance du modèle de Machine Learning.
* **`predict.py`** : Script d'inférence permettant de générer des prédictions sur de nouvelles confrontations.
* **`export_predictions.py`** : Exporte les résultats et probabilités calculés pour les rendre exploitables par l'interface web.
* **`index.html` & `web/predictions.js**` : Interface front-end interactive permettant de visualiser les prédictions.

---

## ⚙️ Pipeline de Machine Learning

1. **Prétraitement des données** : Nettoyage et structuration du dataset historique international (gestion des équipes, scores, dates, lieux de match).
2. **Ingénierie des caractéristiques (*Feature Engineering*)** : Création de variables pertinentes (formes récentes, confrontations directes, avantage à domicile).
3. **Entraînement** : Ajustement des modèles de classification/régression pour estimer l'issue des rencontres.
4. **Export et Visualisation** : Génération des prédictions sous un format interfacé avec le front-end web.

---

## 🛠️ Installation et Prérequis

Assurez vous d'avoir **Python (>= 3.8)** installé sur votre machine.

1. Clonez le dépôt :
```bash
git clone https://github.com/Mathieu7483/Rugby-Predictor-WC2027.git
cd Rugby-Predictor-WC2027

```


2. Créez et activez un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate

```


3. Installez les dépendances nécessaires (selon votre projet) :
```bash
pip install -r requirements.txt

```



---

## 🚀 Utilisation

* **Entraîner le modèle :**
```bash
python train_and_save.py

```


* **Générer de nouvelles prédictions :**
```bash
python predict.py

```


* **Exporter les données pour le web :**
```bash
python export_predictions.py

```
---

## 🌐 Interface Web

L'interface web permet de consulter de manière ergonomique et interactive les prédictions générées par les modèles de Machine Learning.

* **Fichiers clés :**
* `index.html` : La page principale structurant l'affichage des rencontres et des probabilités.
* `web/predictions.js` : Le script front-end qui récupère, structure et dynamise l'affichage des données exportées par le pipeline Python.


* **Lancement local :**
Pour visualiser l'interface, tu peux simplement ouvrir le fichier `index.html` dans ton navigateur web ou utiliser un serveur local (comme l'extension *Live Server* sous VS Code).

---

## ✒️ Author

**Mathieu GODALIER** - *Student at Holberton School, Machine Learning * [Ma page GitHub](https://github.com/Mathieu7483)