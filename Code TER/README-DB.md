# Triangle Database Manager

1. **Objectif Principal**
Le script `triangle_db.py` est une classe `TriangleDatabase` qui gère une base de données SQLite pour stocker et gérer des triangles. C'est un composant central qui :
- Stocke les triangles trouvés
- Suit la progression du traitement des nœuds
- Enregistre des statistiques détaillées.

2. **Structure de la Base de Données**
La base de données contient trois tables :

a) **Table principale c'est la table `triangles`** :
- Elle Stocke les informations de chaque triangle trouvé
- Contient les nœuds (A, B, C) et leurs relations
- Enregistre les poids des relations
- Évite les doublons grâce à une contrainte d'unicité 

  La Table `triangles`
Stocke les informations de chaque triangle trouvé :
- `id` : Identifiant unique auto-incrémenté
- `node_a`, `node_b`, `node_c` : Les trois nœuds formant le triangle
- `relation_a_to_b`, `relation_c_to_b`, `relation_a_to_c` : Types de relations entre les nœuds
- `weight_a_to_b`, `weight_c_to_b`, `weight_a_to_c` : Poids des relations
- `created_at` : Horodatage de création
- Contrainte d'unicité sur la combinaison des nœuds et leurs relations

b) **Table `processed_nodes`** : c'est une table qui garde la traçabilité 
- Suit les nœuds déjà traités
- Garde une trace du statut de traitement ('completed' ou 'in_progress')
- Permet de reprendre le traitement après une interruption
  La Table `processed_nodes`
Suit l'état de traitement des nœuds :
- `node_name` : Nom du nœud (clé primaire)
- `processed_at` : Horodatage du traitement
- `status` : État du traitement ('completed' ou 'in_progress')

c) **Table `statistics`** :
- Stocke les statistiques de chaque session d'exécution
- Enregistre le temps d'exécution, le nombre de triangles, etc.
- Conserve les informations sur les types de relations et les poids moyens

3. **Fonctionnalités Principales**
D'abord, Nous avons une seule classe principale qui gère cette base de données, appelée TriangleDatabase, contenant environ 12 méthodes, que l'on peut classer en plusieurs catégories :

a) Initialisation
__init__() et create_tables() : ou on Initialise la base de données et on crée les tables nécessaires. 
Apres 
b) **La Gestion des Nœuds** :
- `get_last_processed_node()` : Récupère le dernier nœud traité 
- `is_node_processed()` : Vérifie si un nœud a déjà été traité
- `mark_node_in_progress()` : Marque un nœud comme étant en cours de traitement
- `mark_node_processed()` : Marque un nœud comme complètement traité

C) **Gestion des Triangles** :
- `save_triangle()` : Sauvegarde un nouveau triangle dans la base de données
- Évite les doublons grâce à une contrainte d'unicité cad la commande UNIQUE(

d) **Statistiques et Suivi** :
- `get_statistics()` : Calcule des statistiques détaillées sur les triangles
- `get_progress()` : Fournit des informations sur la progression du traitement
- `save_detailed_statistics()` : Sauvegarde les statistiques de la session

4. **Interactions avec d'Autres Scripts**
Le script est conçu pour être utilisé par d'autres composants du système qui :
- Recherchent des triangles dans un graphe
- Ont besoin de suivre leur progression
- Veulent éviter de retraiter les mêmes nœuds
- Doivent stocker et analyser les résultats

5. **Points Techniques Importants**
- Utilise SQLite pour la persistance des données
- Implémente une gestion robuste des transactions
- Gère les erreurs d'intégrité de la base de données
- Stocke les données complexes en JSON
- Permet une reprise après interruption du traitement

6. **Sécurité et Performance**
- Utilise des requêtes paramétrées pour éviter les injections SQL
- Implémente des index pour optimiser les performances
- Gère proprement les connexions à la base de données
- Évite les doublons pour optimiser l'espace de stockage

7. **Cas d'Utilisation**
Ce script est particulièrement utile pour :
- Le traitement de grands graphes
- L'analyse de relations entre nœuds
- Le suivi de la progression d'un traitement long
- La génération de statistiques sur les triangles trouvés

Pour comprendre comment ce script interagit avec les autres composants, il serait utile d'examiner les autres fichiers du projet, notamment ceux qui :
- Appellent les méthodes de `TriangleDatabase`
- Fournissent les données des triangles
- Utilisent les statistiques générées

## Caractéristiques Techniques

### Sécurité
- Utilisation de requêtes paramétrées pour prévenir les injections SQL
- Gestion sécurisée des connexions à la base de données
- Validation des données avant insertion

### Performance
- Indexation optimisée des tables
- Gestion efficace des transactions
- Évitement des doublons pour optimiser l'espace

### Robustesse
- Gestion des erreurs d'intégrité
- Reprise après interruption possible
- Transactions atomiques

