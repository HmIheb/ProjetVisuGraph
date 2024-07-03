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
        return (self.name == other.name and 
                self.type == other.type)

    def __hash__(self):
        return hash((self.name, self.type))

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
        self.phrase="Six Palestinians Live in the West Bank "
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

            
def parse_xml(f):
    tree = ET.parse(f)
    root = tree.getroot()
    annotation = Annotation() #ok on a notre annotation bismichaytan

    #la ca cherche les entites
    for entite_compose in root.findall('.//composite_entity'):
        for entity_elem in entite_compose.findall('entity'):
            entity_id = entity_elem.get('ID')
            entity_type = entity_elem.get('TYPE')
            for mention_elem in entity_elem.findall('entity_mention'):
                
                name = mention_elem.find('./extent/charseq').text
                annotation.add_entity(entity_id, name, entity_type)
    
    #dive pour les relations (susceptible de trouver la relation de attal et bardella)
    for relation_elem in root.findall('.//relation'):
        relation_mention_elem = relation_elem.find('.//relation_mention')
        
        if relation_mention_elem is None:
            print(f"YA PAS DE relation_mention: {ET.tostring(relation_elem, encoding='unicode')}")
            continue
        
        
        extent_elem = relation_mention_elem.find('extent/charseq')
        if extent_elem is None:
            print(f"extent/charseq maakch: {ET.tostring(relation_mention_elem, encoding='unicode')}")
            continue
        
        extent_text = extent_elem.text
        
        
        relation_mention_arguments = []
        for arg_elem in relation_mention_elem.findall('relation_mention_argument'):
            entity_id = arg_elem.get('ENTITYID')
            if entity_id is None:
                print(f"ENTITYID makach: {ET.tostring(arg_elem, encoding='unicode')}")
                continue
            relation_mention_arguments.append(entity_id)
        
        
        entity1_id = relation_mention_arguments[0] if len(relation_mention_arguments) > 0 else None
        entity2_id = relation_mention_arguments[1] if len(relation_mention_arguments) > 1 else None
        print("hawlik "+ entity1_id)
        
        
        entity1 = next((e for e in annotation.entities if e.id == entity1_id), None)
        entity2 = next((e for e in annotation.entities if e.id == entity2_id), None)
        
        
        if entity1 and entity2:
            annotation.add_relation(entity1, entity2, extent_text, directed=True) 
    
    
    for event_elem in root.findall('.//event'):
        trigger_elem = event_elem.find('trigger')
        if trigger_elem is None:
            print(f"le trigger ya pas wesh: {ET.tostring(event_elem, encoding='unicode')}")
            continue
        trigger_id = trigger_elem.get('ID')
        trigger_value = trigger_elem.find('value')
        trigger_type = trigger_elem.find('type')
        if trigger_value is None or trigger_type is None:
            print(f"trigger elem missing 'value' or 'type': {ET.tostring(trigger_elem, encoding='unicode')}")
            continue
        trigger = annotation.add_entity(trigger_id, trigger_value.text, trigger_type.text)
        event_type_elem = event_elem.find('type')
        if event_type_elem is None:
            print(f"ya pas cet event 'type': {ET.tostring(event_elem, encoding='unicode')}")
            continue
        event_type = event_type_elem.text
        event = annotation.add_event(trigger, event_type)
        for argument_elem in event_elem.findall('argument'):
            role = argument_elem.get('ROLE')
            argument_id = argument_elem.get('ENTITY')
            argument = next((e for e in annotation.entities if e.id == argument_id), None)
            if argument:
                annotation.add_event_argument(event, role, argument)
    
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