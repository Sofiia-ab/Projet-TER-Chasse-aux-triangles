from api_client import JDMAPIClient
from triangle_finder import TriangleFinder
from visualizer import Visualizer
from triangle_db import TriangleDatabase
import time
import json
import os

def create_directories():
    """Crée les dossiers nécessaires s'ils n'existent pas."""
    directories = ['Data_graph', 'Liste_Triangles_csv']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Dossier créé : {directory}")

def get_user_input(prompt: str, default_value: str, validation_func=None) -> str:
    """Fonction utilitaire pour obtenir et valider une saisie utilisateur."""
    while True:
        value = input(prompt) or default_value
        if validation_func is None or validation_func(value):
            return value
        print("Valeur invalide. Veuillez réessayer.")

def main():
    print("=== Programme de recherche de triangles ===")
    
    # Créer les dossiers nécessaires
    create_directories()
    
    # Demander à l'utilisateur le poids minimal
    min_weight = float(get_user_input(
        "\nEntrez le poids minimal acceptable pour les relations (par défaut: 0.0): ",
        "0.0",
        lambda x: True  # On accepte toutes les valeurs numériques, y compris négatives
    ))
    
    # Demander à l'utilisateur le nombre maximum de triangles par nœud
    max_triangles = get_user_input(
        "\nEntrez le nombre maximum de triangles à trouver par nœud (laissez vide pour aucune limite): ",
        "",
        lambda x: x == "" or (x.isdigit() and int(x) > 0)
    )
    max_triangles = int(max_triangles) if max_triangles else None
    
    print(f"\nConfiguration :")
    print(f"- Poids minimal : {min_weight}")
    print(f"- Nombre maximum de triangles par nœud : {max_triangles if max_triangles else 'Aucune limite'}")
    
    # Initialiser les composants
    api_client = JDMAPIClient()
    db = TriangleDatabase("triangles.db")
    triangle_finder = TriangleFinder(api_client, min_weight=min_weight, max_triangles_per_node=max_triangles, db=db)
    
    # Recherche des triangles
    print("\nDémarrage de la recherche de triangles...")
    start_time = time.time()
    triangles = triangle_finder.find_all_triangles()
    end_time = time.time()
    
    # Sauvegarder les résultats
    print("\nSauvegarde des résultats...")
    triangle_finder.save_results(os.path.join("Liste_Triangles_csv", "triangles.csv"))
    
    # Obtenir et afficher les statistiques
    stats = triangle_finder.get_statistics()
    print("\n=== Statistiques ===")
    print(f"Temps total d'exécution : {end_time - start_time:.2f} secondes")
    print(f"Nombre total de triangles trouvés : {stats['total_triangles']}")
    print(f"Nombre total de relations rejetées : {stats['total_rejected_relations']}")
    print(f"Seuil de poids minimal : {stats['minimum_weight_threshold']}")
    if stats['max_triangles_per_node']:
        print(f"Limite de triangles par nœud : {stats['max_triangles_per_node']}")
    
    print("\nTypes de relations trouvés :")
    for rel_type, count in stats['relation_types'].items():
        print(f"  Type {rel_type} : {count} triangles")
    
    print("\nPoids moyens des relations :")
    for rel_type, avg_weight in stats['average_weights'].items():
        print(f"  {rel_type} : {avg_weight:.2f}")
    
    # Créer les visualisations
    print("\nCréation des visualisations...")
    visualizer = Visualizer()
    for triangle in triangles:
        visualizer.add_triangle(triangle)
    
    # Visualisation générale des paires de types de relations
    visualizer.plot_relation_type_pairs(os.path.join('Data_graph', 'relation_type_pairs.png'))
    
    # Visualisation des distributions des poids R1 négatifs
    visualizer.plot_negative_r1_distribution(os.path.join('Data_graph', 'negative_r1_distribution.png'))
    
    # Visualisation du nombre de types R1 différents par paire R2-R3
    visualizer.plot_r1_types_per_hat(os.path.join('Data_graph', 'r1_types_per_hat.png'))
    
    # Visualisation du nombre de paires R2-R3 différentes par type R1
    visualizer.plot_hats_per_r1(os.path.join('Data_graph', 'hats_per_r1.png'))
    
    # Visualisation des chapeaux avec poids négatifs par type R1
    visualizer.plot_negative_hats_per_r1(os.path.join('Data_graph', 'negative_hats_per_r1.png'))
    
    visualizer.plot_network(os.path.join("Data_graph", "network.png"))
    visualizer.plot_relation_statistics(stats, os.path.join("Data_graph", "relation_stats.png"))
    visualizer.plot_weight_distribution(triangles, os.path.join("Data_graph", "weight_dist.png"))
    
    print("\nVisualisations de base générées avec succès !")
    print("Fichiers créés :")
    print("- Data_graph/network.png (visualisation du réseau)")
    print("- Data_graph/relation_stats.png (distribution des types de relations)")
    print("- Data_graph/weight_dist.png (distribution des poids)")
    print("- Data_graph/relation_type_pairs.png (distribution des paires R2-R3 par type R1)")
    print("- Data_graph/negative_r1_distribution.png (distribution des poids R1 négatifs par paire R2-R3)")
    print("- Data_graph/r1_types_per_hat.png (nombre de types R1 différents par paire R2-R3)")
    print("- Data_graph/hats_per_r1.png (nombre de paires R2-R3 différentes par type R1)")
    print("- Data_graph/negative_hats_per_r1.png (nombre de chapeaux avec poids négatifs par type R1)")
    print("- Data_graph/relation_type_pairs_summary.txt (résumé détaillé des paires de types)")
    print("- Data_graph/negative_r1_distribution_summary.txt (résumé des distributions des poids R1 négatifs)")
    print("- Data_graph/r1_types_per_hat_summary.txt (résumé des types R1 par paire R2-R3)")
    print("- Data_graph/hats_per_r1_summary.txt (résumé des paires R2-R3 par type R1)")
    print("- Data_graph/negative_hats_per_r1_summary.txt (résumé des chapeaux avec poids négatifs par type R1)")
    
    # Demander à l'utilisateur s'il veut voir la distribution pour un type R1 spécifique
    while True:
        print("\nQue souhaitez-vous visualiser ?")
        print("1. Distribution des paires R2-R3 pour un type R1 spécifique")
        print("2. Distribution des paires R2-R3 pour un couple A-B spécifique")
        print("3. Quitter")
        
        choice = input("Entrez votre choix (1-3) : ")
        
        if choice == '3':
            break
        elif choice == '1':
            # Afficher les types R1 disponibles
            print("\nTypes R1 disponibles :")
            for rel_type, count in stats['relation_types'].items():
                print(f"  Type {rel_type} : {count} triangles")
            
            # Demander le type R1
            r1_type = get_user_input(
                "\nEntrez le type R1 à analyser : ",
                "",
                lambda x: x.isdigit() and int(x) in stats['relation_types']
            )
            
            # Générer la visualisation pour le type R1 spécifique
            visualizer.plot_specific_relation_pairs(int(r1_type), os.path.join("Data_graph", f"relation_pairs_R1_{r1_type}.png"))
        elif choice == '2':
            # Afficher les nœuds A disponibles
            print("\nNœuds A disponibles :")
            a_nodes = sorted(set(t['A'] for t in triangles))
            for i, node in enumerate(a_nodes, 1):
                print(f"{i}. {node}")
            
            # Demander le nœud A
            a_choice = get_user_input(
                "\nEntrez le numéro du nœud A à analyser : ",
                "",
                lambda x: x.isdigit() and 1 <= int(x) <= len(a_nodes)
            )
            node_a = a_nodes[int(a_choice) - 1]
            
            # Afficher les nœuds B disponibles pour ce A
            print(f"\nNœuds B disponibles pour A={node_a} :")
            b_nodes = sorted(set(t['B'] for t in triangles if t['A'] == node_a))
            for i, node in enumerate(b_nodes, 1):
                print(f"{i}. {node}")
            
            # Demander le nœud B
            b_choice = get_user_input(
                "\nEntrez le numéro du nœud B à analyser : ",
                "",
                lambda x: x.isdigit() and 1 <= int(x) <= len(b_nodes)
            )
            node_b = b_nodes[int(b_choice) - 1]
            
            # Générer la visualisation pour le couple A-B spécifique
            visualizer.plot_specific_ab_pairs(node_a, node_b, os.path.join("Data_graph", f"relation_pairs_AB_{node_a}_{node_b}.png"))
        else:
            print("Choix invalide. Veuillez entrer un nombre entre 1 et 3.")

    execution_time = end_time - start_time
    db.save_detailed_statistics(stats, execution_time)

    # Affichage lisible des stats depuis la base
    # On récupère et affiche les types de relations et les poids moyens enregistrés dans la dernière session
    cursor = db.conn.cursor()
    cursor.execute("SELECT relation_types, average_weights FROM statistics ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    if row:
        relation_types = json.loads(row[0])
        average_weights = json.loads(row[1])
        print("\nTypes de relations trouvés (depuis la base) :")
        for rel_type, count in relation_types.items():
            print(f"  Type {rel_type}: {count} triangles")
        print("Poids moyens des relations (depuis la base) :")
        for rel, avg in average_weights.items():
            print(f"  {rel}: {avg:.2f}")

if __name__ == "__main__":
    main() 