# **Full-stack-book**

## **But de l'application**
Web service ayant pour but de rendre une base de données de livres accessible, modifiable, et de permettre à un utilisateur de mettre des livres en favori.

## **Base de données**
La base de données que nous utilisons à été trouvé [ici](https://www.kaggle.com/datasets/jealousleopard/goodreadsbooks). Certaines lignes du fichier .csv comportait des virgules, nous avons modifié le fichier pour que les données soient prises en compte correctement.

## **Mode d'emploi**
Pour installer le projet sur votre machine, il vous faut cloner le projet sur votre machine personnelle via l'instruction ci-dessous :
     $ git clone https://github.com/kittanh/fullstack-book

Pour lancer les containers de l'API, la DB et le FRONT:
* `docker-compose build` (si première fois)
* `docker-compose up`

On peut accéder à l'API et au FRONT avec les liens suivants:
* API: [localhost:5000](http://localhost:5000/)
* FRONT: [localhost:8050](http://localhost:8050/)
