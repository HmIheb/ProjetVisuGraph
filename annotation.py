
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel
import xml.etree.ElementTree as ET
import json
"""
Classe entité défini par un nom et par un type d'entité tout deux en chaine de caracteres
"""



class Entity:
    def __init__(self, entity_id, name, entity_type):
        self.id = entity_id
        self.name = name
        self.type = entity_type
    
    def __eq__(self, other):
        return (self.mention == other.mention and 
                self.entity_type == other.entity_type)

    def __hash__(self):
        return hash((self.mention, self.entity_type))

class Relation:
    def __init__(self, e1, e2, relation_type, directed=False):
        self.entity1 = e1
        self.entity2 = e2
        self.type = relation_type
        self.directed = directed

    def __eq__(self, other):
        return (self.entity1 == other.entity1 and 
                self.entity2 == other.entity2 and 
                self.type == other.type and 
                self.directed == other.directed)

    def __hash__(self):
        return hash((self.entity1, self.entity2, self.type, self.directed))

class Event:
    def __init__(self, trigger, event_type):
        self.trigger = trigger
        self.type = event_type
        self.arguments = []

    def add_argument(self, role, entity):
        self.arguments.append((role, entity))

    def __eq__(self, other):
        return self.trigger == other.trigger and self.type == other.type

    def __hash__(self):
        return hash((self.trigger, self.type))

class Annotation:
    def __init__(self):
        self.entities = []
        self.relations = []
        self.events = []

    def add_entity(self, entity_id, mention, entity_type):
        entity = Entity(entity_id, mention, entity_type)
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


class AnnotationListWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()  # Création du layout principal pour le widget

        # Création des listes d'éléments pour les entités, les relations et les événements
        self.entityListWidget = QListWidget()
        self.relationListWidget = QListWidget()
        self.eventListWidget = QListWidget()

        # Ajout des libellés pour chaque section
        layout.addWidget(QLabel("Entities:"))
        layout.addWidget(self.entityListWidget)
        layout.addWidget(QLabel("Relations:"))
        layout.addWidget(self.relationListWidget)
        layout.addWidget(QLabel("Events:"))
        layout.addWidget(self.eventListWidget)

        # Application du layout créé au widget lui-même
        self.setLayout(layout)

    def update_annotations(self, entities, relations, events):
        # Effacement des contenus précédents des listes
        self.entityListWidget.clear()
        self.relationListWidget.clear()
        self.eventListWidget.clear()

        # Ajout des nouvelles annotations dans les listes correspondantes
        for entity in entities:
            self.entityListWidget.addItem(f"{entity.name} ({entity.type})")

        for relation in relations:
            direction = "->" if relation.directed else "<->"
            self.relationListWidget.addItem(f"{relation.entity1.name} {direction} {relation.entity2.name} ({relation.type})")

            
        for event in events:
            self.eventListWidget.addItem(f"{event.trigger.name} ({event.type})")
            
def parse_xml(f):
    tree = ET.parse(f)
    root = tree.getroot()
    annotation = Annotation()
    for entity_elem in root.findall('entities/entity'):
        entity_id = entity_elem.get('ID')
        name = entity_elem.find('value').text
        entity_type = entity_elem.find('type').text
        annotation.add_entity(entity_id, name, entity_type)
    for relation_elem in root.findall('relations/relation'):
        relation_type = relation_elem.find('type').text
        directed = relation_elem.get('DIRECTED') == 'true'
        entity1_id = relation_elem.find('arg1/entity').get('ID')
        entity2_id = relation_elem.find('arg2/entity').get('ID')
        entity1 = next((e for e in annotation.entities if e.id == entity1_id), None)
        entity2 = next((e for e in annotation.entities if e.id == entity2_id), None)
        annotation.add_relation(entity1, entity2, relation_type, directed)
    for event_elem in root.findall('events/event'):
        trigger_elem = event_elem.find('trigger')
        trigger = annotation.add_entity(trigger_elem.get('ID'), trigger_elem.find('value').text, trigger_elem.find('type').text)
        event_type = event_elem.find('type').text
        event = annotation.add_event(trigger, event_type)
        for argument_elem in event_elem.findall('argument'):
            role = argument_elem.get('ROLE')
            argument_id = argument_elem.get('ENTITY')
            argument = next((e for e in annotation.entities if e.id == argument_id), None)
            event.add_argument(role, argument)
    return annotation

def parse_json(fich):
    data = json.load(fich)
    annotation = Annotation()
    for entity in data['entities']:
        entity_obj = annotation.add_entity(entity['id'], entity['text'], entity['type'])
    for relation in data['relations']:
        entity1 = next((e for e in annotation.entities if e.id == relation['arg1']), None)
        entity2 = next((e for e in annotation.entities if e.id == relation['arg2']), None)
        annotation.add_relation(entity1, entity2, relation['type'], relation.get('directed', False))
    for event in data['events']:
        trigger = annotation.add_entity(event['trigger']['id'], event['trigger']['text'], event['trigger']['type'])
        event_obj = annotation.add_event(trigger, event['type'])
        for argument in event['arguments']:
            argument_entity = next((e for e in annotation.entities if e.id == argument['entity']), None)
            event_obj.add_argument(argument['role'], argument_entity)
    return annotation

def pointcommun_annotation(annotation1, annotation2):
    common_annot = Annotation()

    # les entitées commune
    common_entities = set(annotation1.entities).intersection(set(annotation2.entities))
    common_annot.entities.extend(common_entities)

    # les relations communes
    common_relations = set(annotation1.relations).intersection(set(annotation2.relations))
    common_annot.relations.extend(common_relations)

    # les events communs
    common_events = set(annotation1.events).intersection(set(annotation2.events))
    common_annot.events.extend(common_events)

    return common_annot

def difference_annotation(annotation1, annotation2):
    diff_annot = Annotation()

    # les entitées differentes 
    diff_entities = set(annotation1.entities).symmetric_difference(set(annotation2.entities))
    diff_annot.entities.extend(diff_entities)

    # les relations differentes
    diff_relations = set(annotation1.relations).symmetric_difference(set(annotation2.relations))
    diff_annot.relations.extend(diff_relations)

    # les events differents
    diff_events = set(annotation1.events).symmetric_difference(set(annotation2.events))
    diff_annot.events.extend(diff_events)

    return diff_annot


