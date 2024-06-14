# un fichier pour gerer le dessin des graphes
# en gros les entites sont toujours des noeuds et les relations toujours des aretes vous avez capté

import networkx as nx

class GraphDrawer:
    def __init__(self, annotation):
        self.annotation = annotation
        self.graph = nx.Graph()
        
    def draw(self):
        self.creer_noeud()
        self.creer_arete()
        
        
    def creer_noeud(self):
        dessin_entit = EntityDrawer(self.graph)
        dessin_entit.draw_entities(self.annotation.entities)
        
        dessin_event = EventDrawer(self.graph)
        dessin_event.draw_events(self.annotation.events)
        
    def creer_arete(self):
        relation_drawer = RelationDrawer(self.graph)
        relation_drawer.draw_relations(self.annotation.relations)
        
        dessin_event = EventDrawer(self.graph)
        dessin_event.draw_event_arguments(self.annotation.events)

        
class EntityDrawer:
    def __init__(self, graph):
        self.graph = graph
        
    def draw_entities(self, entities):
        for entity in entities:
            self.graph.add_node(entity.id, label=entity.name, entity_type=entity.type)
            
            
class RelationDrawer:
    ...
    # in progress les gars
    
class EventDrawer:
    ...
