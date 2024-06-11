"""
Classe entité défini par un nom et par un type d'entité tout deux en chaine de caracteres
"""
import xml.etree.ElementTree as ET
import json


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


    def parse_xml(f):
    tree = ET.parse(f)
    root = tree.getroot()
    
    annotation = Annotation()
    
   
    for entity_elem in root.findall('entities/entity'):
        name = entity_elem.find('value').text
        entity_type = entity_elem.find('type').text
        entity = annotation.add_entity(name, entity_type)
    
    
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
        trigger = annotation.add_entity(trigger_elem.find('value').text, trigger_elem.find('type').text)
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
        entity_obj = annotation.add_entity(entity['text'], entity['type'])
        entity_obj.id = entity['id']
    
 
    for relation in data['relations']:
        entity1 = next((e for e in annotation.entities if e['id'] == relation['arg1']), None)
        entity2 = next((e for e in annotation.entities if e['id'] == relation['arg2']), None)
        annotation.add_relation(entity1, entity2, relation['type'], relation.get('directed', False))
    
    for event in data['events']:
        trigger = annotation.add_entity(event['trigger']['text'], event['trigger']['type'])
        event_obj = annotation.add_event(trigger, event['type'])
        
        for argument in event['arguments']:
            argument_entity = next((e for e in annotation.entities if e['id'] == argument['entity']), None)
            event_obj.add_argument(argument['role'], argument_entity)
    
    return annotation






        
      


