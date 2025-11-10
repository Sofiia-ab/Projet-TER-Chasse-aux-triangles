import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List
import pandas as pd
from collections import defaultdict
import os

class Visualizer:
    def __init__(self):
        self.triangles = []
        self.G = nx.DiGraph()
        
    def add_triangle(self, triangle: Dict):
        """Add a triangle to the graph."""
        self.triangles.append(triangle)
        # Add nodes
        self.G.add_node(triangle['A'])
        self.G.add_node(triangle['B'])
        self.G.add_node(triangle['C'])
        
        # Add edges with their types as attributes
        self.G.add_edge(triangle['A'], triangle['B'], 
                           type=triangle['A_to_B'],
                           weight=triangle['A_to_B_weight'])
        self.G.add_edge(triangle['C'], triangle['B'],
                           type=triangle['C_to_B'],
                           weight=triangle['C_to_B_weight'])
        self.G.add_edge(triangle['A'], triangle['C'],
                           type=triangle['A_to_C'],
                           weight=triangle['A_to_C_weight'])
    
    def plot_network(self, filename: str = "network.png"):
        """Plot the network of triangles."""
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(self.G)
        
        # Draw nodes
        nx.draw_networkx_nodes(self.G, pos, node_color='lightblue', 
                             node_size=500, alpha=0.6)
        
        # Draw edges with different colors based on relation types
        edge_colors = []
        for u, v in self.G.edges():
            edge_type = self.G[u][v]['type']
            edge_colors.append(edge_type)
        
        nx.draw_networkx_edges(self.G, pos, edge_color=edge_colors, 
                             width=2, alpha=0.6, arrows=True)
        
        # Add labels
        nx.draw_networkx_labels(self.G, pos)
        
        plt.title("Réseau de Triangles")
        plt.axis('off')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_relation_statistics(self, stats: Dict, filename: str = "relation_stats.png"):
        """Plot statistics about relation types."""
        plt.figure(figsize=(10, 6))
        
        # Create bar plot of relation types
        relation_types = list(stats['relation_types'].keys())
        counts = list(stats['relation_types'].values())
        
        plt.bar(relation_types, counts)
        plt.title("Distribution des Types de Relations")
        plt.xlabel("Type de Relation")
        plt.ylabel("Nombre de Triangles")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_weight_distribution(self, triangles: List[Dict], filename: str = "weight_dist.png"):
        """Plot the distribution of weights in triangles."""
        plt.figure(figsize=(12, 6))
        
        # Create DataFrame for weights
        weights_df = pd.DataFrame({
            'A->B': [t['A_to_B_weight'] for t in triangles],
            'C->B': [t['C_to_B_weight'] for t in triangles],
            'A->C': [t['A_to_C_weight'] for t in triangles]
        })
        
        # Plot weight distributions
        sns.boxplot(data=weights_df)
        plt.title("Distribution of Weights in Triangle Relations")
        plt.xlabel("Relation Type")
        plt.ylabel("Weight")
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_relation_type_pairs(self, filename: str = "relation_type_pairs.png"):
        """Plot the distribution of R2-R3 pairs for each R1 type."""
        # Créer un dictionnaire pour stocker les paires R2-R3 pour chaque R1
        relation_pairs = defaultdict(lambda: defaultdict(int))
        
        # Analyser les triangles pour compter les paires
        for triangle in self.triangles:
            r1 = triangle['A_to_B']  # Type de relation A->B
            r2 = triangle['C_to_B']  # Type de relation C->B
            r3 = triangle['A_to_C']  # Type de relation A->C
            
            # Créer une clé unique pour la paire R2-R3
            pair_key = f"R2{r2}-R3{r3}"
            relation_pairs[r1][pair_key] += 1
        
        # Créer le graphique
        plt.figure(figsize=(15, 10))
        
        # Pour chaque type R1, créer un sous-graphique
        n_types = len(relation_pairs)
        n_cols = 3
        n_rows = (n_types + n_cols - 1) // n_cols
        
        for idx, (r1, pairs) in enumerate(relation_pairs.items(), 1):
            plt.subplot(n_rows, n_cols, idx)
            
            # Trier les paires par fréquence
            sorted_pairs = sorted(pairs.items(), key=lambda x: x[1], reverse=True)
            pair_names = [p[0] for p in sorted_pairs]
            pair_counts = [p[1] for p in sorted_pairs]
            
            # Créer le graphique à barres
            plt.bar(range(len(pair_names)), pair_counts)
            plt.title(f"R1={r1}")
            plt.xticks(range(len(pair_names)), pair_names, rotation=45, ha='right')
            plt.ylabel("Nombre de triangles")
            
            # Ajouter les valeurs au-dessus des barres
            for i, count in enumerate(pair_counts):
                plt.text(i, count, str(count), ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Créer un résumé textuel
        summary_filename = os.path.join(os.path.dirname(filename), 'relation_type_pairs_summary.txt')
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write("Résumé des paires de types de relations par R1:\n\n")
            for r1, pairs in relation_pairs.items():
                f.write(f"Pour R1={r1}:\n")
                for pair, count in sorted(pairs.items(), key=lambda x: x[1], reverse=True):
                    f.write(f"  {pair}: {count} triangles\n")
                f.write("\n")
    
    def plot_specific_relation_pairs(self, r1_type: int, filename: str = None):
        """Plot the distribution of R2-R3 pairs for a specific R1 type."""
        if filename is None:
            filename = f'relation_pairs_R1_{r1_type}.png'
            
        # Filtrer les triangles pour le type R1 spécifique
        r1_triangles = [t for t in self.triangles if t['A_to_B'] == r1_type]
        
        if not r1_triangles:
            print(f"Aucun triangle trouvé pour le type de relation R1={r1_type}")
            return
        
        # Créer un dictionnaire pour stocker les paires R2-R3
        relation_pairs = defaultdict(int)
        
        # Analyser les triangles pour compter les paires
        for triangle in r1_triangles:
            r2 = triangle['C_to_B']  # Type de relation C->B
            r3 = triangle['A_to_C']  # Type de relation A->C
            
            # Créer une clé unique pour la paire R2-R3
            pair_key = f"R2{r2}-R3{r3}"
            relation_pairs[pair_key] += 1
        
        # Créer le graphique
        plt.figure(figsize=(12, 6))
        
        # Trier les paires par fréquence
        sorted_pairs = sorted(relation_pairs.items(), key=lambda x: x[1], reverse=True)
        pair_names = [p[0] for p in sorted_pairs]
        pair_counts = [p[1] for p in sorted_pairs]
        
        # Créer le graphique à barres
        bars = plt.bar(range(len(pair_names)), pair_counts)
        plt.title(f"Distribution des paires R2-R3 pour R1={r1_type}")
        plt.xlabel("Paires de types de relations (R2-R3)")
        plt.ylabel("Nombre de triangles")
        plt.xticks(range(len(pair_names)), pair_names, rotation=45, ha='right')
        
        # Ajouter les valeurs au-dessus des barres
        for i, count in enumerate(pair_counts):
            plt.text(i, count, str(count), ha='center', va='bottom')
        
        # Ajouter une grille pour une meilleure lisibilité
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Créer un résumé textuel
        summary_filename = os.path.join(os.path.dirname(filename), f'relation_pairs_R1_{r1_type}_summary.txt')
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write(f"Résumé des paires de types de relations pour R1={r1_type}:\n\n")
            f.write(f"Nombre total de triangles: {len(r1_triangles)}\n\n")
            for pair, count in sorted_pairs:
                f.write(f"{pair}: {count} triangles\n")
        
        print(f"\nVisualisation créée pour R1={r1_type}")
        print(f"- Graphique sauvegardé dans '{filename}'")
        print(f"- Résumé sauvegardé dans '{summary_filename}'")

    def plot_specific_ab_pairs(self, node_a: str, node_b: str, filename: str = None):
        """Plot the distribution of R2-R3 pairs for a specific A-B couple."""
        if filename is None:
            filename = f'relation_pairs_AB_{node_a}_{node_b}.png'
            
        # Filtrer les triangles pour le couple A-B spécifique
        ab_triangles = [t for t in self.triangles if t['A'] == node_a and t['B'] == node_b]
        
        if not ab_triangles:
            print(f"Aucun triangle trouvé pour le couple A={node_a} -> B={node_b}")
            return
        
        # Créer un dictionnaire pour stocker les paires R2-R3
        relation_pairs = defaultdict(int)
        
        # Analyser les triangles pour compter les paires
        for triangle in ab_triangles:
            r2 = triangle['C_to_B']  # Type de relation C->B
            r3 = triangle['A_to_C']  # Type de relation A->C
            
            # Créer une clé unique pour la paire R2-R3
            pair_key = f"R2{r2}-R3{r3}"
            relation_pairs[pair_key] += 1
        
        # Créer le graphique
        plt.figure(figsize=(12, 6))
        
        # Trier les paires par fréquence
        sorted_pairs = sorted(relation_pairs.items(), key=lambda x: x[1], reverse=True)
        pair_names = [p[0] for p in sorted_pairs]
        pair_counts = [p[1] for p in sorted_pairs]
        
        # Créer le graphique à barres
        bars = plt.bar(range(len(pair_names)), pair_counts)
        plt.title(f"Distribution des paires R2-R3 pour A={node_a} -> B={node_b}")
        plt.xlabel("Paires de types de relations (R2-R3)")
        plt.ylabel("Nombre de triangles")
        plt.xticks(range(len(pair_names)), pair_names, rotation=45, ha='right')
        
        # Ajouter les valeurs au-dessus des barres
        for i, count in enumerate(pair_counts):
            plt.text(i, count, str(count), ha='center', va='bottom')
        
        # Ajouter une grille pour une meilleure lisibilité
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Créer un résumé textuel
        summary_filename = os.path.join(os.path.dirname(filename), f'relation_pairs_AB_{node_a}_{node_b}_summary.txt')
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write(f"Résumé des paires de types de relations pour A={node_a} -> B={node_b}:\n\n")
            f.write(f"Nombre total de triangles: {len(ab_triangles)}\n\n")
            for pair, count in sorted_pairs:
                f.write(f"{pair}: {count} triangles\n")
        
        print(f"\nVisualisation créée pour A={node_a} -> B={node_b}")
        print(f"- Graphique sauvegardé dans '{filename}'")
        print(f"- Résumé sauvegardé dans '{summary_filename}'")

    def plot_negative_r1_distribution(self, filename: str = "negative_r1_distribution.png"):
        """Plot the number of negative R1 weights for each R2-R3 pair."""
        print("\nAnalyse des relations R1 négatives...")
        print(f"Nombre total de triangles à analyser : {len(self.triangles)}")
        
        # Créer un dictionnaire pour stocker le nombre de R1 négatifs pour chaque paire R2-R3
        negative_r1_counts = defaultdict(int)
        
        # Analyser les triangles pour compter les R1 négatifs
        for triangle in self.triangles:
            r1_weight = triangle['A_to_B_weight']
            if r1_weight < 0:  # On ne garde que les poids négatifs
                r2 = triangle['C_to_B']  # Type de relation C->B
                r3 = triangle['A_to_C']  # Type de relation A->C
                
                # Créer une clé unique pour la paire R2-R3
                pair_key = f"R2{r2}-R3{r3}"
                negative_r1_counts[pair_key] += 1
                print(f"Triangle trouvé avec R1 négatif : {pair_key} (poids R1 = {r1_weight})")
        
        if not negative_r1_counts:
            print("Aucune relation R1 avec poids négatif trouvée")
            print("Vérification des poids R1 dans les triangles :")
            for triangle in self.triangles:
                print(f"Triangle : R1={triangle['A_to_B']}, poids={triangle['A_to_B_weight']}")
            return
        
        print(f"\nNombre de paires R2-R3 avec R1 négatif : {len(negative_r1_counts)}")
        for pair, count in negative_r1_counts.items():
            print(f"{pair} : {count} relations R1 négatives")
        
        # Créer le graphique
        plt.figure(figsize=(15, 8))
        
        # Trier les paires par nombre de R1 négatifs
        sorted_pairs = sorted(negative_r1_counts.items(), key=lambda x: x[1], reverse=True)
        pair_names = [p[0] for p in sorted_pairs]
        pair_counts = [p[1] for p in sorted_pairs]
        
        # Créer le graphique à barres
        bars = plt.bar(range(len(pair_names)), pair_counts)
        plt.title("Nombre de relations R1 négatives par paire R2-R3")
        plt.xlabel("Paires de types de relations (R2-R3)")
        plt.ylabel("Nombre de relations R1 négatives")
        plt.xticks(range(len(pair_names)), pair_names, rotation=45, ha='right')
        
        # Ajouter les valeurs au-dessus des barres
        for i, count in enumerate(pair_counts):
            plt.text(i, count, str(count), ha='center', va='bottom')
        
        # Ajouter une grille pour une meilleure lisibilité
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Créer un résumé textuel
        summary_filename = os.path.join(os.path.dirname(filename), 'negative_r1_distribution_summary.txt')
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write("Résumé du nombre de relations R1 négatives par paire R2-R3:\n\n")
            for pair, count in sorted_pairs:
                f.write(f"{pair}: {count} relations R1 négatives\n")

    def plot_r1_types_per_hat(self, filename: str = "r1_types_per_hat.png"):
        """Plot the number of different R1 types for each R2-R3 pair."""
        # Créer un dictionnaire pour stocker les types R1 uniques pour chaque paire R2-R3
        r1_types_per_hat = defaultdict(set)
        
        # Analyser les triangles pour collecter les types R1
        for triangle in self.triangles:
            r1 = triangle['A_to_B']  # Type de relation A->B
            r2 = triangle['C_to_B']  # Type de relation C->B
            r3 = triangle['A_to_C']  # Type de relation A->C
            
            # Créer une clé unique pour la paire R2-R3
            pair_key = f"R2{r2}-R3{r3}"
            r1_types_per_hat[pair_key].add(r1)
        
        if not r1_types_per_hat:
            print("Aucune paire R2-R3 trouvée")
            return
        
        # Créer le graphique
        plt.figure(figsize=(15, 8))
        
        # Trier les paires par nombre de types R1
        sorted_pairs = sorted(r1_types_per_hat.items(), key=lambda x: len(x[1]), reverse=True)
        pair_names = [p[0] for p in sorted_pairs]
        pair_counts = [len(p[1]) for p in sorted_pairs]
        
        # Créer le graphique à barres
        bars = plt.bar(range(len(pair_names)), pair_counts)
        plt.title("Nombre de types de relations R1 différents par paire R2-R3")
        plt.xlabel("Paires de types de relations (R2-R3)")
        plt.ylabel("Nombre de types R1 différents")
        plt.xticks(range(len(pair_names)), pair_names, rotation=45, ha='right')
        
        # Ajouter les valeurs au-dessus des barres
        for i, count in enumerate(pair_counts):
            plt.text(i, count, str(count), ha='center', va='bottom')
        
        # Ajouter une grille pour une meilleure lisibilité
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Créer un résumé textuel
        summary_filename = os.path.join(os.path.dirname(filename), 'r1_types_per_hat_summary.txt')
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write("Résumé du nombre de types R1 différents par paire R2-R3:\n\n")
            for pair, r1_types in sorted_pairs:
                f.write(f"{pair}:\n")
                f.write(f"  Nombre de types R1 différents: {len(r1_types)}\n")
                f.write(f"  Types R1: {sorted(r1_types)}\n\n")

    def plot_hats_per_r1(self, filename: str = "hats_per_r1.png"):
        """Plot the number of different R2-R3 pairs (hats) for each R1 type."""
        # Créer un dictionnaire pour stocker les paires R2-R3 uniques pour chaque R1
        hats_per_r1 = defaultdict(set)
        
        # Analyser les triangles pour collecter les paires R2-R3
        for triangle in self.triangles:
            r1 = triangle['A_to_B']  # Type de relation A->B
            r2 = triangle['C_to_B']  # Type de relation C->B
            r3 = triangle['A_to_C']  # Type de relation A->C
            
            # Créer une clé unique pour la paire R2-R3
            pair_key = f"R2{r2}-R3{r3}"
            hats_per_r1[r1].add(pair_key)
        
        if not hats_per_r1:
            print("Aucun type R1 trouvé")
            return
        
        # Créer le graphique
        plt.figure(figsize=(15, 8))
        
        # Trier les types R1 par nombre de chapeaux
        sorted_r1 = sorted(hats_per_r1.items(), key=lambda x: len(x[1]), reverse=True)
        r1_types = [f"R1{r[0]}" for r in sorted_r1]
        hat_counts = [len(r[1]) for r in sorted_r1]
        
        # Créer le graphique à barres
        bars = plt.bar(range(len(r1_types)), hat_counts)
        plt.title("Nombre de paires R2-R3 différentes par type R1")
        plt.xlabel("Types de relations R1")
        plt.ylabel("Nombre de paires R2-R3 différentes")
        plt.xticks(range(len(r1_types)), r1_types, rotation=45, ha='right')
        
        # Ajouter les valeurs au-dessus des barres
        for i, count in enumerate(hat_counts):
            plt.text(i, count, str(count), ha='center', va='bottom')
        
        # Ajouter une grille pour une meilleure lisibilité
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Créer un résumé textuel
        summary_filename = os.path.join(os.path.dirname(filename), 'hats_per_r1_summary.txt')
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write("Résumé du nombre de paires R2-R3 différentes par type R1:\n\n")
            for r1, hats in sorted_r1:
                f.write(f"R1{r1}:\n")
                f.write(f"  Nombre de paires R2-R3 différentes: {len(hats)}\n")
                f.write(f"  Paires R2-R3: {sorted(hats)}\n\n")

    def plot_negative_hats_per_r1(self, filename: str = "negative_hats_per_r1.png"):
        """Plot the number of hats (R2-R3 pairs) with negative weights for each R1 type."""
        # Créer des dictionnaires pour stocker les différents types de chapeaux négatifs
        r2_negative = defaultdict(set)  # Chapeaux avec R2 négatif
        r3_negative = defaultdict(set)  # Chapeaux avec R3 négatif
        both_negative = defaultdict(set)  # Chapeaux avec R2 et R3 négatifs
        
        # Analyser les triangles pour collecter les chapeaux négatifs
        for triangle in self.triangles:
            r1 = triangle['A_to_B']  # Type de relation A->B
            r2 = triangle['C_to_B']  # Type de relation C->B
            r3 = triangle['A_to_C']  # Type de relation A->C
            r2_weight = triangle['C_to_B_weight']
            r3_weight = triangle['A_to_C_weight']
            
            # Créer une clé unique pour la paire R2-R3
            pair_key = f"R2{r2}-R3{r3}"
            
            # Classifier le chapeau selon ses poids négatifs
            if r2_weight < 0 and r3_weight < 0:
                both_negative[r1].add(pair_key)
            elif r2_weight < 0:
                r2_negative[r1].add(pair_key)
            elif r3_weight < 0:
                r3_negative[r1].add(pair_key)
        
        if not any([r2_negative, r3_negative, both_negative]):
            print("Aucun chapeau avec poids négatif trouvé")
            return
        
        # Créer le graphique
        plt.figure(figsize=(15, 8))
        
        # Obtenir tous les types R1 uniques
        all_r1_types = sorted(set(list(r2_negative.keys()) + list(r3_negative.keys()) + list(both_negative.keys())))
        x = range(len(all_r1_types))
        width = 0.25  # Largeur des barres
        
        # Préparer les données pour chaque type de chapeau négatif
        r2_neg_counts = [len(r2_negative.get(r1, set())) for r1 in all_r1_types]
        r3_neg_counts = [len(r3_negative.get(r1, set())) for r1 in all_r1_types]
        both_neg_counts = [len(both_negative.get(r1, set())) for r1 in all_r1_types]
        
        # Créer les barres groupées
        plt.bar([i - width for i in x], r2_neg_counts, width, label='R2 négatif')
        plt.bar(x, r3_neg_counts, width, label='R3 négatif')
        plt.bar([i + width for i in x], both_neg_counts, width, label='R2 et R3 négatifs')
        
        plt.title("Nombre de chapeaux avec poids négatifs par type R1")
        plt.xlabel("Types de relations R1")
        plt.ylabel("Nombre de chapeaux")
        plt.xticks(x, [f"R1{r1}" for r1 in all_r1_types], rotation=45, ha='right')
        plt.legend()
        
        # Ajouter une grille pour une meilleure lisibilité
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Créer un résumé textuel
        summary_filename = os.path.join(os.path.dirname(filename), 'negative_hats_per_r1_summary.txt')
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write("Résumé des chapeaux avec poids négatifs par type R1:\n\n")
            for r1 in all_r1_types:
                f.write(f"R1{r1}:\n")
                f.write(f"  Chapeaux avec R2 négatif ({len(r2_negative.get(r1, set()))}): {sorted(r2_negative.get(r1, set()))}\n")
                f.write(f"  Chapeaux avec R3 négatif ({len(r3_negative.get(r1, set()))}): {sorted(r3_negative.get(r1, set()))}\n")
                f.write(f"  Chapeaux avec R2 et R3 négatifs ({len(both_negative.get(r1, set()))}): {sorted(both_negative.get(r1, set()))}\n\n") 