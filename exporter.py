import pandas as pd

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


