"""
Classe entité défini par un nom et par un type d'entité tout deux en chaine de caracteres
"""
class Entity:
    def __init__(self, name, entity_type):
        self.name = name
        self.type = entity_type


"""
Classe Relation défini par deux entité et un type en chaine de caracteres et un boolean pour savoir si la relation est à sens unique
"""
class Relation:
    def __init__(self, e1, e2, relation_type, directed=False):
        self.entity1 = e1
        self.entity2 = e2
        self.type = relation_type
        self.directed = directed


"""
Classe Evenement défini par une entité déclencheuse (trigger), un type en chaine de caractere, et un nombre indéfini d'argument chaque composé d'une entité et de son role dans l'evenement
"""
class Event:
    def __init__(self, trigger, event_type):
        self.trigger = trigger
        self.type = event_type
        self.arguments = []

    def add_argument(self, role, entity):
        self.arguments.append((role, entity))


"""
Classe Annotation comprenant toutes les entités, les relations, les evenements
"""
class Annotation:
    def __init__(self):
        self.entities = []
        self.relations = []
        self.events = []

    def add_entity(self, mention, entity_type):
        entity = Entity(mention, entity_type)
        self.entities.append(entity)
        return entity

    def add_relation(self, entity1, entity2, relation_type, directed=False):
        relation = Relation(entity1, entity2, relation_type, directed)
        self.relations.append(relation)
        return relation

    def add_event(self, trigger, event_type):
        event = Event(trigger, event_type)
        self.events.append(event)
        return event


