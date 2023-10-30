# **Full-stack-book**

## **But de l'application**
Web service ayant pour but de rendre une base de données de livres accessible, modifiable, et de permettre à un utilisateur de mettre des livres en favori.

## **Base de données**
La base de données que nous utilisons à été trouvé [ici](https://www.kaggle.com/datasets/jealousleopard/goodreadsbooks). Certaines lignes du fichier .csv comportait des virgules, nous avons modifié le fichier pour que les données soient prises en compte correctement.

## **Mode d'emploi**
* Pour lancer les containeur de l'API et la DB:
    * `docker-compose build` (si première fois)
    * `docker-compose up`
* Pour lancer le front: Exécuter le fichier `front_api.py` dans le dossier **test_front**. Puis ouvrir [localhost:8050](http://localhost:8050/)