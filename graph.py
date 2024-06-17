# J'ai fusionné mon fichier graph.py qui ne contenait que les classes pour dessiner les nodes, les aretes avec le main.py de iheb, comme ça le fichier graph.py contient les classes pour dessiner ainsi que la fenetre principale


import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QGraphicsView, QGraphicsScene, QHBoxLayout, 
                             QPushButton, QFileDialog, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsLineItem)
from PyQt5.QtCore import Qt
import networkx as nx
from annotation import parse_xml, parse_json, Annotation, Entity, Relation, Event



class GraphDrawer:
    def __init__(self, annotation):
        self.annotation = annotation
        self.graph = nx.DiGraph()
        
    def draw(self):
        self.creer_noeud()
        self.creer_arete()
        
        
        
        
        
    #ici si vous jugez que j'ai mal compris, corrigez moi, car selon ma compréhension, une entité et un event sont tous les deux representés par des noeuds 
    
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
        
        
# drawer genre un tirroir hhhhh
class EntityDrawer:
    def __init__(self, graph):
        self.graph = graph
        
    def draw_entities(self, entities):
        for entity in entities:
            self.graph.add_node(entity.name, label=entity.name, entity_type=entity.type)

class RelationDrawer:
    def __init__(self, graph):
        self.graph = graph
        
    def draw_relations(self, relations):
        for relation in relations:
            self.graph.add_edge(relation.entity1.name, relation.entity2.name, label=relation.type, directed=relation.directed)

class EventDrawer:
    def __init__(self, graph):
        self.graph = graph
        
    def draw_events(self, events):
        for event in events:
            self.graph.add_node(event.trigger.name, label=event.type, entity_type="event")
            
    def draw_event_arguments(self, events):
        for event in events:
            for role, argument in event.arguments:
                self.graph.add_edge(event.trigger.name, argument.name, label=role)

class GraphVisualizer(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
      
    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        
        self.scale(zoom_factor, zoom_factor)
        
    def draw_graph(self, graph):
        self.scene.clear()
        pos = nx.spring_layout(graph)
        for node, (x, y) in pos.items():
            ellipse = QGraphicsEllipseItem(x * 100, y * 100, 20, 20)
            self.scene.addItem(ellipse)
            text = QGraphicsTextItem(node)
            text.setPos(x * 100, y * 100)
            self.scene.addItem(text)
        for edge in graph.edges(data=True):
            source = pos[edge[0]]
            target = pos[edge[1]]
            line = QGraphicsLineItem(source[0] * 100, source[1] * 100, target[0] * 100, target[1] * 100)
            self.scene.addItem(line)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Outil de Visualisation de Graphes')
        self.setGeometry(100, 100, 800, 600)

        self.graphVisualizer = GraphVisualizer()

        self.centralWidget = QWidget()
        self.layout = QVBoxLayout()
        
        self.layout.addWidget(self.graphVisualizer)
        
        self.importButton = QPushButton("Import XML/JSON")
        self.importButton.clicked.connect(self.importText)
        self.exportButton = QPushButton("Export Image")
        
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.importButton)
        self.buttonLayout.addWidget(self.exportButton)
        
        self.layout.addLayout(self.buttonLayout)
        
        self.centralWidget.setLayout(self.layout)
        self.setCentralWidget(self.centralWidget)

    def importText(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Import File", "", "XML Files (*.xml);;JSON Files (*.json);;All Files (*)", options=options)
        if fileName:
            if fileName.endswith('.xml'):
                with open(fileName, 'r', encoding='utf-8') as file:
                    annotation = parse_xml(file)
            elif fileName.endswith('.json'):
                with open(fileName, 'r', encoding='utf-8') as file:
                    annotation = parse_json(file)
            graph_drawer = GraphDrawer(annotation)
            graph_drawer.draw()
            self.graphVisualizer.draw_graph(graph_drawer.graph)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
