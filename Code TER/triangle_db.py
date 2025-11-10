# =============================================================
# triangle_db.py : Gestion de la base de données des triangles
# =============================================================
# Cette classe centralise toutes les opérations sur la base SQLite :
#   - Stockage des triangles
#   - Suivi des nœuds traités
#   - Calcul et sauvegarde des statistiques
# =============================================================

import sqlite3
from typing import Dict, List, Set, Optional
from datetime import datetime
import json

class TriangleDatabase:
    """
    Classe principale pour la gestion de la base de données SQLite des triangles.
    Elle permet de stocker les triangles, suivre la progression des nœuds,
    et enregistrer des statistiques détaillées sur les sessions d'exécution.
    """

    # -----------------------------
    # Initialisation et tables
    # -----------------------------
    def __init__(self, db_name: str = "triangles.db"):
        """
        Initialise la connexion à la base de données et crée les tables si besoin.
        
        Args:
            db_name (str): Nom du fichier de base de données (par défaut : triangles.db)
        """
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        """
        Crée les tables nécessaires dans la base de données si elles n'existent pas déjà :
        - triangles : stocke chaque triangle trouvé
        - processed_nodes : suit les nœuds déjà traités
        - statistics : enregistre les statistiques de chaque session
        """
        cursor = self.conn.cursor()
        # Table des triangles
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS triangles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_a TEXT,
            node_b TEXT,
            node_c TEXT,
            relation_a_to_b TEXT,
            relation_c_to_b TEXT,
            relation_a_to_c TEXT,
            weight_a_to_b REAL,
            weight_c_to_b REAL,
            weight_a_to_c REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(node_a, node_b, node_c, relation_a_to_b, relation_c_to_b, relation_a_to_c)
        )
        ''')
        # Table des nœuds traités
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_nodes (
            node_name TEXT PRIMARY KEY,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'completed'  -- 'completed' ou 'in_progress'
        )
        ''')
        # Table des statistiques
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            execution_time REAL,
            total_triangles INTEGER,
            total_rejected_relations INTEGER,
            minimum_weight_threshold REAL,
            max_triangles_per_node INTEGER,
            relation_types TEXT,
            average_weights TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        self.conn.commit()

    # -----------------------------
    # Gestion des nœuds
    # -----------------------------
    def get_last_processed_node(self) -> Optional[str]:
        """
        Retourne le dernier nœud traité (pour permettre une reprise intelligente).
        
        Returns:
            str | None : Nom du dernier nœud traité, ou None si aucun nœud n'a été traité.
        """
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT node_name 
        FROM processed_nodes 
        WHERE status = 'completed'
        ORDER BY processed_at DESC 
        LIMIT 1
        ''')
        result = cursor.fetchone()
        return result[0] if result else None

    def is_node_processed(self, node_name: str) -> bool:
        """
        Vérifie si un nœud a déjà été traité (pour éviter de le refaire).
        
        Args:
            node_name (str): Nom du nœud à vérifier
        Returns:
            bool : True si le nœud a déjà été traité, False sinon
        """
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT 1 
        FROM processed_nodes 
        WHERE node_name = ? AND status = 'completed'
        ''', (node_name,))
        return cursor.fetchone() is not None

    def mark_node_in_progress(self, node_name: str):
        """
        Marque un nœud comme étant en cours de traitement (utile pour la reprise après interruption).
        
        Args:
            node_name (str): Nom du nœud à marquer
        """
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO processed_nodes (node_name, status)
        VALUES (?, 'in_progress')
        ''', (node_name,))
        self.conn.commit()

    def mark_node_processed(self, node_name: str):
        """
        Marque un nœud comme complètement traité (pour ne pas le refaire).
        
        Args:
            node_name (str): Nom du nœud à marquer comme traité
        """
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO processed_nodes (node_name, status)
        VALUES (?, 'completed')
        ''', (node_name,))
        self.conn.commit()

    # -----------------------------
    # Gestion des triangles
    # -----------------------------
    def save_triangle(self, triangle: dict) -> bool:
        """
        Sauvegarde un triangle dans la base de données s'il n'existe pas déjà (évite les doublons).
        
        Args:
            triangle (dict): Dictionnaire contenant les informations du triangle
        Returns:
            bool : True si le triangle a été ajouté, False s'il existait déjà
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
            INSERT OR IGNORE INTO triangles (
                node_a, node_b, node_c,
                relation_a_to_b, relation_c_to_b, relation_a_to_c,
                weight_a_to_b, weight_c_to_b, weight_a_to_c
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                triangle['A'], triangle['B'], triangle['C'],
                triangle['A_to_B'], triangle['C_to_B'], triangle['A_to_C'],
                triangle['A_to_B_weight'], triangle['C_to_B_weight'], triangle['A_to_C_weight']
            ))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            return False

    # -----------------------------
    # Statistiques et progression
    # -----------------------------
    def get_statistics(self) -> Dict:
        """
        Calcule et retourne des statistiques détaillées sur les triangles et les nœuds traités.
        
        Returns:
            dict : Statistiques (nombre total, distribution des types, poids moyens, etc.)
        """
        cursor = self.conn.cursor()
        stats = {}
        # Nombre total de triangles
        cursor.execute('SELECT COUNT(*) FROM triangles')
        stats['total_triangles'] = cursor.fetchone()[0]
        # Nombre de nœuds traités
        cursor.execute('SELECT COUNT(*) FROM processed_nodes WHERE status = "completed"')
        stats['processed_nodes'] = cursor.fetchone()[0]
        # Distribution des types de relations
        cursor.execute('''
        SELECT 
            relation_a_to_b as relation_type,
            COUNT(*) as count
        FROM triangles
        GROUP BY relation_a_to_b
        ORDER BY count DESC
        ''')
        stats['relation_types'] = dict(cursor.fetchall())
        # Poids moyens par type de relation
        cursor.execute('''
        SELECT 
            relation_a_to_b as relation_type,
            AVG(weight_a_to_b) as avg_weight
        FROM triangles
        GROUP BY relation_a_to_b
        ''')
        stats['average_weights_by_type'] = dict(cursor.fetchall())
        # Statistiques globales sur les poids
        cursor.execute('''
        SELECT 
            AVG(weight_a_to_b) as avg_a_to_b,
            AVG(weight_c_to_b) as avg_c_to_b,
            AVG(weight_a_to_c) as avg_a_to_c,
            MIN(weight_a_to_b) as min_weight,
            MAX(weight_a_to_b) as max_weight
        FROM triangles
        ''')
        weights = cursor.fetchone()
        stats['weight_statistics'] = {
            'average_weights': {
                'A_to_B': weights[0],
                'C_to_B': weights[1],
                'A_to_C': weights[2]
            },
            'min_weight': weights[3],
            'max_weight': weights[4]
        }
        # Nœuds les plus fréquents
        cursor.execute('''
        SELECT node_a, COUNT(*) as count
        FROM triangles
        GROUP BY node_a
        ORDER BY count DESC
        LIMIT 10
        ''')
        stats['most_common_nodes'] = dict(cursor.fetchall())
        return stats

    def get_progress(self) -> Dict:
        """
        Retourne des informations sur la progression du traitement (dernier nœud traité, nœuds en cours).
        
        Returns:
            dict : Informations de progression (dernier nœud traité, nœuds en cours)
        """
        cursor = self.conn.cursor()
        progress = {}
        # Dernier nœud traité
        cursor.execute('''
        SELECT node_name, processed_at
        FROM processed_nodes
        WHERE status = 'completed'
        ORDER BY processed_at DESC
        LIMIT 1
        ''')
        last_node = cursor.fetchone()
        progress['last_processed_node'] = {
            'name': last_node[0] if last_node else None,
            'time': last_node[1] if last_node else None
        }
        # Nœuds en cours de traitement
        cursor.execute('''
        SELECT COUNT(*)
        FROM processed_nodes
        WHERE status = 'in_progress'
        ''')
        progress['nodes_in_progress'] = cursor.fetchone()[0]
        return progress

    def close(self):
        """
        Ferme proprement la connexion à la base de données.
        """
        self.conn.close()

    def save_detailed_statistics(self, stats: dict, execution_time: float):
        """
        Sauvegarde les statistiques détaillées de la session dans la table statistics.
        
        Args:
            stats (dict): Dictionnaire des statistiques à sauvegarder
            execution_time (float): Temps total d'exécution (en secondes)
        """
        cursor = self.conn.cursor()
        # On s'assure que la table existe (sécurité)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            execution_time REAL,
            total_triangles INTEGER,
            total_rejected_relations INTEGER,
            minimum_weight_threshold REAL,
            max_triangles_per_node INTEGER,
            relation_types TEXT,
            average_weights TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        # Insertion des statistiques (les champs complexes sont stockés en JSON)
        cursor.execute('''
            INSERT INTO statistics (
                execution_time, total_triangles, total_rejected_relations, minimum_weight_threshold, max_triangles_per_node, relation_types, average_weights
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            execution_time,
            stats.get('total_triangles', 0),
            stats.get('total_rejected_relations', 0),
            stats.get('minimum_weight_threshold', 0.0),
            stats.get('max_triangles_per_node'),
            json.dumps(stats.get('relation_types', {})),
            json.dumps(stats.get('average_weights', {}))
        ))
        self.conn.commit() 