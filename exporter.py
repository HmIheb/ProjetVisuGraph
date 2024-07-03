import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom

'''
Contient les méthode d'exportation 
'''
class Exporter:
    @staticmethod
    def export_to_csv(entities, relations, events, file_name):
        # Créer un DataFrame pour les entités
        entities_data = [(entity.name, entity.type) for entity in entities]
        entities_df = pd.DataFrame(entities_data, columns=['Entity Name', 'Entity Type'])
        
        # Créer un DataFrame pour les relations
        relations_data = [(relation.entity1.name, relation.entity2.name, relation.type, relation.directed) for relation in relations]
        relations_df = pd.DataFrame(relations_data, columns=['Entity 1', 'Entity 2', 'Relation Type', 'Directed'])
        
        # Créer un DataFrame pour les événements
        events_data = [(event.trigger.name, event.type, ', '.join([f'{role}: {arg.name}' for role, arg in event.arguments])) for event in events]
        events_df = pd.DataFrame(events_data, columns=['Trigger', 'Event Type', 'Arguments'])
        
        # Écrire les DataFrames dans un fichier CSV
        with open(file_name + '.csv', 'w', encoding='utf-8') as csvfile:
            entities_df.to_csv(csvfile, index=False)
            relations_df.to_csv(csvfile, index=False)
            events_df.to_csv(csvfile, index=False)
    
        print("Exportation en CSV réussie.")

    def export_to_xml(entities, relations, events, file_name, uri, docid):
        source_file = ET.Element("source_file", {
            "URI": uri,
            "SOURCE": "newswire",
            "TYPE": "text",
            "VERSION": "4.0",
            "AUTHOR": "LDC",
            "ENCODING": "UTF-8"
        })

        document = ET.SubElement(source_file, "document", {"DOCID": docid})

        for entity in entities:
            entity_elem = ET.SubElement(document, "entity", {
                "ID": entity.name,  # Assuming name is used as ID
                "TYPE": entity.type
            })
            for mention in getattr(entity, 'mentions', []):
                mention_elem = ET.SubElement(entity_elem, "entity_mention", {"ID": mention.id})
                extent = ET.SubElement(mention_elem, "extent")
                charseq_extent = ET.SubElement(extent, "charseq", {
                    "START": mention.extent_start,
                    "END": mention.extent_end
                })
                charseq_extent.text = mention.extent_text
                head = ET.SubElement(mention_elem, "head")
                charseq_head = ET.SubElement(head, "charseq", {
                    "START": mention.head_start,
                    "END": mention.head_end
                })
                charseq_head.text = mention.head_text

        for relation in relations:
            relation_elem = ET.SubElement(document, "relation", {
                "ID": f"{relation.entity1.name}_{relation.entity2.name}",
                "TYPE": relation.type,
                "DIRECTED": str(relation.directed).lower()
            })
            ET.SubElement(relation_elem, "arg", {"ENTITYID": relation.entity1.name, "ROLE": "arg1"})
            ET.SubElement(relation_elem, "arg", {"ENTITYID": relation.entity2.name, "ROLE": "arg2"})

        for event in events:
            event_elem = ET.SubElement(document, "event", {
                "ID": event.trigger.name,
                "TYPE": event.type
            })
            for role, arg in event.arguments:
                ET.SubElement(event_elem, "arg", {"ROLE": role, "ENTITYID": arg.name})

        tree = ET.ElementTree(source_file)

        # Convertir l'élément tree en une chaîne XML
        xml_str = ET.tostring(source_file, encoding='utf-8', method='xml')

        # Utiliser minidom pour formater avec une indentation
        parsed_xml = minidom.parseString(xml_str)
        pretty_xml_as_str = parsed_xml.toprettyxml(indent="    ")

        print(f"Writing to file: {file_name}")
        try:
            with open(file_name, 'w', encoding='utf-8') as files:
                files.write(pretty_xml_as_str)
            print("Exportation en XML réussie.")
        except Exception as e:
            print(f"Erreur lors de l'exportation en XML: {e}")



