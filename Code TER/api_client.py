import requests
from typing import Dict, List, Optional, Set
import time
import json
from collections import defaultdict
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class JDMAPIClient:
    BASE_URL = "https://jdm-api.demo.lirmm.fr/v0"
    TIMEOUT = 10  # seconds
    
    # Liste des types de relations à exclure car non précises
    EXCLUDED_RELATION_TYPES = {0, 666, 777, 4, 1, 2, 200, 1000, 1001, 1002, 2001}
    
    # Mapping des IDs de relations vers leur nom
    RELATION_TYPE_NAMES = {
        0: 'r_associated',
        1: 'r_raff_sem',
        2: 'r_raff_morpho',
        3: 'r_domain',
        4: 'r_pos',
        5: 'r_syn',
        6: 'r_isa',
        7: 'r_anto',
        8: 'r_hypo',
        9: 'r_has_part',
        10: 'r_holo',
        11: 'r_locution',
        12: 'r_flpot',
        13: 'r_agent',
        14: 'r_patient',
        15: 'r_lieu',
        16: 'r_instr',
        17: 'r_carac',
        18: 'r_data',
        19: 'r_lemma',
        20: 'r_has_magn',
        21: 'r_has_antimagn',
        22: 'r_family',
        23: 'r_carac-1',
        24: 'r_agent-1',
        25: 'r_instr-1',
        26: 'r_patient-1',
        27: 'r_domain-1',
        28: 'r_lieu-1',
        29: 'r_chunk_pred',
        30: 'r_lieu_action',
        31: 'r_action_lieu',
        32: 'r_sentiment',
        33: 'r_error',
        34: 'r_manner',
        35: 'r_meaning/glose',
        36: 'r_infopot',
        37: 'r_telic_role',
        38: 'r_agentif_role',
        39: 'r_verbe-action',
        40: 'r_action-verbe',
        41: 'r_has_conseq',
        42: 'r_has_causatif',
        43: 'r_adj-verbe',
        44: 'r_verbe-adj',
        45: 'r_chunk_sujet',
        46: 'r_chunk_objet',
        47: 'r_chunk_loc',
        48: 'r_chunk_instr',
        49: 'r_time',
        50: 'r_object>mater',
        51: 'r_mater>object',
        52: 'r_successeur-time',
        53: 'r_make',
        54: 'r_product_of',
        55: 'r_against',
        56: 'r_against-1',
        57: 'r_implication',
        58: 'r_quantificateur',
        59: 'r_masc',
        60: 'r_fem',
        61: 'r_equiv',
        62: 'r_manner-1',
        63: 'r_agentive_implication',
        64: 'r_has_instance',
        65: 'r_verb_real',
        66: 'r_chunk_head',
        67: 'r_similar',
        68: 'r_set>item',
        69: 'r_item>set',
        70: 'r_processus>agent',
        71: 'r_variante',
        72: 'r_syn_strict',
        73: 'r_is_smaller_than',
        74: 'r_is_bigger_than',
        75: 'r_accomp',
        76: 'r_processus>patient',
        77: 'r_verb_ppas',
        78: 'r_cohypo',
        79: 'r_verb_ppre',
        80: 'r_processus>instr',
        81: 'r_pref_form',
        82: 'r_interact_with',
        83: 'r_alias',
        84: 'r_has_euphemisme',
        99: 'r_der_morpho',
        100: 'r_has_auteur',
        101: 'r_has_personnage',
        102: 'r_can_eat',
        103: 'r_has_actors',
        104: 'r_deplac_mode',
        105: 'r_has_interpret',
        106: 'r_has_color',
        107: 'r_has_cible',
        108: 'r_has_symptomes',
        109: 'r_has_predecesseur-time',
        110: 'r_has_diagnostic',
        111: 'r_has_predecesseur-space',
        112: 'r_has_successeur-space',
        113: 'r_has_social_tie_with',
        114: 'r_tributary',
        115: 'r_sentiment-1',
        116: 'r_linked-with',
        117: 'r_foncteur',
        118: 'r_comparison',
        119: 'r_but',
        120: 'r_but-1',
        121: 'r_own',
        122: 'r_own-1',
        123: 'r_verb_aux',
        124: 'r_predecesseur-logic',
        125: 'r_successeur-logic',
        126: 'r_isa-incompatible',
        127: 'r_incompatible',
        128: 'r_node2relnode-in',
        129: 'r_require',
        130: 'r_is_instance_of',
        131: 'r_is_concerned_by',
        132: 'r_symptomes-1',
        133: 'r_units',
        134: 'r_promote',
        135: 'r_circumstances',
        136: 'r_has_auteur-1',
        137: 'r_processus>agent-1',
        138: 'r_processus>patient-1',
        139: 'r_processus>instr-1',
        140: 'r_node2relnode-out',
        141: 'r_carac_nominale',
        142: 'r_has_topic',
        148: 'r_pourvoyeur',
        149: 'r_compl_agent',
        150: 'r_has_beneficiaire',
        151: 'r_descend_de',
        152: 'r_domain_subst',
        153: 'r_has_prop',
        154: 'r_activ_voice',
        155: 'r_make_use_of',
        156: 'r_is_used_by',
        157: 'r_adj-nomprop',
        158: 'r_nomprop-adj',
        159: 'r_adj-adv',
        160: 'r_adv-adj',
        161: 'r_homophone',
        162: 'r_potential_confusion_with',
        163: 'r_concerning',
        164: 'r_adj>nom',
        165: 'r_nom>adj',
        166: 'r_opinion_of',
        167: 'r_has_value',
        168: 'r_has_value>',
        169: 'r_has_value<',
        170: 'r_sing_form',
        171: 'r_lieu>origine',
        172: 'r_depict',
        173: 'r_has_prop-1',
        174: 'r_quantificateur-1',
        175: 'r_promote-1',
        200: 'r_context',
        222: 'r_pos_seq',
        333: 'r_translation',
        444: 'r_link',
        555: 'r_cooccurrence',
        666: 'r_aki',
        777: 'r_wiki',
        997: 'r_annotation_exception',
        998: 'r_annotation',
        999: 'r_inhib',
        1000: 'r_prev',
        1001: 'r_succ',
        1002: 'r_termgroup',
        2000: 'r_raff_sem-1',
        2001: 'r_learning_model'
    }
    
    def __init__(self):
        self.session = requests.Session()
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,  # number of retries
            backoff_factor=1,  # wait 1, 2, 4 seconds between retries
            status_forcelist=[500, 502, 503, 504]  # HTTP status codes to retry on
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.node_cache = {}  # Cache for node information
        self.relations_cache = defaultdict(list)  # Cache for relations
        self.reverse_relations_cache = defaultdict(list)  # Cache for reverse relations
        self.failed_nodes = set()  # Keep track of nodes that failed
    
    def get_node_info(self, node_id: int) -> Optional[Dict]:
        """Get node information from cache or API."""
        if node_id in self.node_cache:
            return self.node_cache[node_id]
            
        if node_id in self.failed_nodes:
            return None
            
        try:
            url = f"{self.BASE_URL}/node_by_id/{node_id}"
            response = self.session.get(url, timeout=self.TIMEOUT)
            response.raise_for_status()
            node_info = response.json()
            self.node_cache[node_id] = node_info
            return node_info
        except requests.exceptions.RequestException as e:
            print(f"Error getting node info for ID {node_id}: {e}")
            self.failed_nodes.add(node_id)
            return None
    
    def filter_relations(self, relations: List[Dict]) -> List[Dict]:
        """Filter out relations with excluded relation types."""
        return [rel for rel in relations if rel.get('type') not in self.EXCLUDED_RELATION_TYPES]
    
    def get_relations_from(self, word: str) -> List[Dict]:
        """Get all relations where the given word is the source."""
        # Check cache first
        if word in self.relations_cache:
            return self.relations_cache[word]
            
        url = f"{self.BASE_URL}/relations/from/{word}"
        try:
            response = self.session.get(url, timeout=self.TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            if not isinstance(data, dict) or 'relations' not in data or 'nodes' not in data:
                return []
            
            # Debug: Afficher uniquement les poids des relations
            print(f"\nPoids des relations pour {word}:")
            for rel in data['relations']:
                print(f"Poids: {rel.get('w')}")
                
            # Filter relations with excluded types
            data['relations'] = self.filter_relations(data['relations'])
            
            # Create a mapping of node IDs to their information
            node_map = {node['id']: node for node in data['nodes']}
            
            # Process relations and add node information
            processed_relations = []
            for rel in data['relations']:
                # Get source node info (should be the word we queried)
                source_node = node_map.get(rel['node1'])
                if not source_node:
                    source_node = self.get_node_info(rel['node1'])
                    if not source_node:
                        continue
                
                # Get target node info
                target_node = node_map.get(rel['node2'])
                if not target_node:
                    target_node = self.get_node_info(rel['node2'])
                    if not target_node:
                        continue
                
                processed_relation = {
                    'source': source_node['name'],
                    'target': target_node['name'],
                    'type': rel['type'],
                    'weight': float(rel['w'])
                }
                processed_relations.append(processed_relation)
            
            # Cache the results
            self.relations_cache[word] = processed_relations
            return processed_relations
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting relations from {word}: {e}")
            return []
    
    def get_relations_to(self, word: str) -> List[Dict]:
        """Get all relations where the given word is the target."""
        # Check cache first
        if word in self.reverse_relations_cache:
            return self.reverse_relations_cache[word]
            
        url = f"{self.BASE_URL}/relations/to/{word}"
        try:
            response = self.session.get(url, timeout=self.TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            if not isinstance(data, dict) or 'relations' not in data or 'nodes' not in data:
                return []
            
            # Debug: Afficher uniquement les poids des relations
            print(f"\nPoids des relations vers {word}:")
            for rel in data['relations']:
                print(f"Poids: {rel.get('w')}")
                
            # Filter relations with excluded types
            data['relations'] = self.filter_relations(data['relations'])
            
            # Create a mapping of node IDs to their information
            node_map = {node['id']: node for node in data['nodes']}
            
            # Process relations and add node information
            processed_relations = []
            for rel in data['relations']:
                # Get source node info
                source_node = node_map.get(rel['node1'])
                if not source_node:
                    source_node = self.get_node_info(rel['node1'])
                    if not source_node:
                        continue
                
                # Get target node info (should be the word we queried)
                target_node = node_map.get(rel['node2'])
                if not target_node:
                    target_node = self.get_node_info(rel['node2'])
                    if not target_node:
                        continue
                
                processed_relation = {
                    'source': source_node['name'],
                    'target': target_node['name'],
                    'type': rel['type'],
                    'weight': float(rel['w'])
                }
                processed_relations.append(processed_relation)
            
            # Cache the results
            self.reverse_relations_cache[word] = processed_relations
            return processed_relations
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting relations to {word}: {e}")
            return []
    
    def get_node_by_id(self, node_id: int) -> Dict:
        """Get node information by ID."""
        url = f"{self.BASE_URL}/node_by_id/{node_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_node_by_name(self, name: str) -> Dict:
        """Get node information by name."""
        url = f"{self.BASE_URL}/node_by_name/{name}"
        response = self.session.get(url, timeout=self.TIMEOUT)
        response.raise_for_status()
        return response.json()
    
    def get_all_nodes(self) -> List[Dict]:
        """Get all nodes in the database."""
        # Start with a small set of words for testing
        #sample_words = ["poule","chat", "chien", "animal", "maison", "voiture", "bleu", "sourcil"]
        #sample_words = ["poule","chat", "chien"]
        #sample_words = ["animal", "maison", "voiture"]
        #sample_words = ["bleu", "sourcil","singe","avion"]
        sample_words = ["mot", "sac","feuille", "ville","chaine","chaise","arbre","fleur","fruit","lait","pain","fromage","viande","poisson"]
        #sample_words = ["poule"]
        nodes = []
        
        print("\nFetching initial nodes...")
        for word in sample_words:
            try:
                print(f"Getting node for: {word}")
                node = self.get_node_by_name(word)
                if isinstance(node, dict) and not node.get('name', '').startswith('en:'):
                    nodes.append(node)
                    # Cache the node information
                    if 'id' in node:
                        self.node_cache[node['id']] = node
                    print(f"Successfully fetched node: {word}")
                else:
                    print(f"Ignored node (starts with 'en:'): {node.get('name', '')}")
            except requests.exceptions.RequestException as e:
                print(f"Error getting node for {word}: {e}")
                continue
        
        print(f"Successfully fetched {len(nodes)} initial nodes")
        return nodes 