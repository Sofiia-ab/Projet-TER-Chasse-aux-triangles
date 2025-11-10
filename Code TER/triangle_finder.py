from typing import Dict, List, Set, Tuple
from collections import defaultdict
from tqdm import tqdm
import pandas as pd
from api_client import JDMAPIClient
import time
import csv
import os

class TriangleFinder:
    def __init__(self, api_client: JDMAPIClient, min_weight: float = 0.0, max_triangles_per_node: int = None, db=None):
        self.api_client = api_client
        self.triangles = []
        self.relation_stats = defaultdict(int)
        self.processed_nodes = set()
        self.rejected_relations = []  # Pour garder une trace des relations rejetées
        self.min_weight = min_weight  # Poids minimal acceptable
        self.max_triangles_per_node = max_triangles_per_node  # Nombre maximum de triangles par nœud
        self.db = db
        
    def find_triangles(self, start_node: Dict) -> List[Dict]:
        """Find all triangles starting from a given node."""
        if not isinstance(start_node, dict):
            return []
            
        node_name = start_node.get('name')
        if not node_name:
            return []
            
        # Skip if we've already processed this node
        if self.db and self.db.is_node_processed(node_name):
            return []
        if node_name in self.processed_nodes:
            return []
            
        self.processed_nodes.add(node_name)
        if self.db:
            self.db.mark_node_in_progress(node_name)
        print(f"\nProcessing node: {node_name}")
        
        # Compteur de triangles pour ce nœud
        triangles_for_node = 0
            
        # Get all relations where start_node is the source (A->B)
        try:
            print(f"Getting relations from {node_name}...")
            relations_from = self.api_client.get_relations_from(node_name)
            if not relations_from:
                print(f"No relations found from {node_name}")
                return []
                
            print(f"Found {len(relations_from)} relations from {node_name}")
                
            # Create a set of target nodes for faster lookup
            target_nodes = {rel['target'] for rel in relations_from}
            print(f"Found {len(target_nodes)} target nodes")
            
            # For each target node, get its incoming relations
            for target_b in target_nodes:
                # Vérifier si on a atteint la limite de triangles pour ce nœud
                if self.max_triangles_per_node is not None and triangles_for_node >= self.max_triangles_per_node:
                    print(f"\nLimite de {self.max_triangles_per_node} triangles atteinte pour le nœud {node_name}")
                    return self.triangles
                
                print(f"Getting relations to {target_b}...")
                relations_to_b = self.api_client.get_relations_to(target_b)
                if not relations_to_b:
                    continue
                    
                print(f"Found {len(relations_to_b)} relations to {target_b}")
                    
                # Create a set of source nodes that point to target_b
                source_nodes = {rel['source'] for rel in relations_to_b if rel['source'] != node_name}
                
                # For each source node, check if it's also a target of start_node
                for source_c in source_nodes:
                    # Vérifier si on a atteint la limite de triangles pour ce nœud
                    if self.max_triangles_per_node is not None and triangles_for_node >= self.max_triangles_per_node:
                        print(f"\nLimite de {self.max_triangles_per_node} triangles atteinte pour le nœud {node_name}")
                        return self.triangles
                        
                    # Check if there's a relation A->C
                    for rel3 in relations_from:
                        if rel3['target'] == source_c:
                            # We found a triangle!
                            # Get the original relations for type and weight
                            rel1 = next(r for r in relations_from if r['target'] == target_b)
                            rel2 = next(r for r in relations_to_b if r['source'] == source_c)
                            
                            # Verify all weights are above minimum threshold
                            #if rel1['weight'] < self.min_weight or rel2['weight'] < self.min_weight or rel3['weight'] < self.min_weight:
                                #continue
                            
                            triangle = {
                                'A': node_name,
                                'B': target_b,
                                'C': source_c,
                                'A_to_B': rel1.get('type', 'unknown'),
                                'C_to_B': rel2.get('type', 'unknown'),
                                'A_to_C': rel3.get('type', 'unknown'),
                                'A_to_B_weight': float(rel1.get('weight', 0)),
                                'C_to_B_weight': float(rel2.get('weight', 0)),
                                'A_to_C_weight': float(rel3.get('weight', 0))
                            }
                            self.triangles.append(triangle)
                            if self.db:
                                self.db.save_triangle(triangle)
                            triangles_for_node += 1
                            print(f"\nTriangle trouvé: {node_name} -> {target_b} -> {source_c}")
                            print(f"Nombre total de triangles trouvés: {len(self.triangles)}")
                            print(f"Triangles trouvés pour {node_name}: {triangles_for_node}")
                            
                            # Update statistics
                            self.relation_stats[rel1.get('type', 'unknown')] += 1
                            
        except Exception as e:
            print(f"Error processing node {node_name}: {e}")
            return []
                    
        if self.db:
            self.db.mark_node_processed(node_name)
        return self.triangles
    
    def find_all_triangles(self) -> List[Dict]:
        """Find all possible triangles in the database."""
        nodes = self.api_client.get_all_nodes()
        if not nodes:
            print("No nodes to process!")
            return []
            
        print(f"\nStarting triangle search with {len(nodes)} nodes")
        print(f"Minimum weight threshold: {self.min_weight}")
        if self.max_triangles_per_node is not None:
            print(f"Maximum triangles per node: {self.max_triangles_per_node}")
        
        for node in tqdm(nodes, desc="Finding triangles"):
            start_time = time.time()
            self.find_triangles(node)
            end_time = time.time()
            print(f"Processed node in {end_time - start_time:.2f} seconds")
            print(f"Current triangle count: {len(self.triangles)}")
            print(f"Total rejected relations: {len(self.rejected_relations)}")
            
        return self.triangles
    
    def save_results(self, filename: str = "triangles.csv"):
        """Save found triangles to a CSV file."""
        # Sauvegarder le fichier triangles.csv
        df = pd.DataFrame(self.triangles)
        df.to_csv(filename, index=False)
        
        # Sauvegarder aussi les relations rejetées
        rejected_df = pd.DataFrame(self.rejected_relations)
        rejected_df.to_csv(os.path.join(os.path.dirname(filename), "rejected_relations.csv"), index=False)

        # Générer un second CSV avec les noms des relations
        relation_names = self.api_client.RELATION_TYPE_NAMES
        with open(os.path.join(os.path.dirname(filename), "triangles_with_names.csv"), "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "A", "nom_relationA_to_B", "B", "C", "nom_relationC_to_B", "B", "A", "nom_relationA_to_C", "C"
            ])
            for t in self.triangles:
                writer.writerow([
                    t['A'],
                    relation_names.get(t['A_to_B'], "unknown"),
                    t['B'],
                    t['C'],
                    relation_names.get(t['C_to_B'], "unknown"),
                    t['B'],
                    t['A'],
                    relation_names.get(t['A_to_C'], "unknown"),
                    t['C']
                ])
        
    def get_statistics(self) -> Dict:
        """Get statistics about found triangles."""
        return {
            'total_triangles': len(self.triangles),
            'total_rejected_relations': len(self.rejected_relations),
            'minimum_weight_threshold': self.min_weight,
            'max_triangles_per_node': self.max_triangles_per_node,
            'relation_types': dict(self.relation_stats),
            'average_weights': {
                'A_to_B': sum(t['A_to_B_weight'] for t in self.triangles) / len(self.triangles) if self.triangles else 0,
                'C_to_B': sum(t['C_to_B_weight'] for t in self.triangles) / len(self.triangles) if self.triangles else 0,
                'A_to_C': sum(t['A_to_C_weight'] for t in self.triangles) / len(self.triangles) if self.triangles else 0
            }
        } 