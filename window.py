import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, 
                             QWidget, QGraphicsView, QGraphicsScene, 
                             QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem,
                             QHBoxLayout, QPushButton, QFileDialog, QLabel, QDialog, QFormLayout, QLineEdit, QDialogButtonBox, 
                             QComboBox, QCheckBox, QListWidget)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPen, QBrush, QFont
import networkx as nx
from exporter import Exporter
from annotation import Annotation, AnnotationListWidget

# GraphVisualizer pour visualiser les graphes d'entités et de relations
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

# MainWindow pour intégrer toutes les fonctionnalités
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Outil de Visualisation de Graphes')
        self.setGeometry(100, 100, 800, 600)

        self.graphVisualizer = GraphVisualizer()
        
        self.annotation = Annotation()

        self.centralWidget = QWidget()
        self.layout = QVBoxLayout()
        
        self.layout.addWidget(self.graphVisualizer)
        
        # Ajouter les boutons d'importation et d'exportation
        self.importButton = QPushButton("Import Ace 2005")
        self.importButton.clicked.connect(self.importText)
        self.exportButton = QPushButton("Export Image")
        
        self.exportCSVButton = QPushButton("Export CSV")
        self.exportCSVButton.clicked.connect(self.export_to_csv)

        # Ajouter les boutons pour créer des entités, des relations et des événements
        self.createEntityButton = QPushButton("Créer Entité")
        self.createEntityButton.clicked.connect(self.create_entity_dialog)
        self.createRelationButton = QPushButton("Créer Relation")
        self.createRelationButton.clicked.connect(self.create_relation_dialog)
        self.createEventButton = QPushButton("Créer Événement")
        self.createEventButton.clicked.connect(self.create_event_dialog)     
        
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.importButton)
        self.buttonLayout.addWidget(self.exportButton)
        self.buttonLayout.addWidget(self.exportCSVButton)
        self.buttonLayout.addWidget(self.createEntityButton)
        self.buttonLayout.addWidget(self.createRelationButton)
        self.buttonLayout.addWidget(self.createEventButton)

        self.layout.addLayout(self.buttonLayout)

        # Ajouter le widget de liste d'annotations
        self.annotationListWidget = AnnotationListWidget()
        self.layout.addWidget(self.annotationListWidget)
        
        self.centralWidget.setLayout(self.layout)
        self.setCentralWidget(self.centralWidget)

   

    
    def importText(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Import xml File", "", "Xml Files (*.xml);;All Files (*)", options=options)
        if fileName:
            with open(fileName, 'r', encoding='utf-8') as file:
                text = file.read()
                #appeler le parser ici

    def export_to_csv(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if fileName:
            Exporter.export_to_csv(self.annotation.entities, self.annotation.relations, self.annotation.events, fileName)
            print("Exportation en CSV réussie.")

    # Mettre à jour la liste des annotations dans AnnotationListWidget
    def update_annotation_list(self):
        self.annotationListWidget.update_annotations(self.annotation.entities, self.annotation.relations, self.annotation.events)            

    # Méthode pour créer une nouvelle entité via une boîte de dialogue
    def create_entity_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Créer Entité")

        layout = QVBoxLayout()
        formLayout = QFormLayout()

        nameLabel = QLabel("Nom:")
        nameLineEdit = QLineEdit()
        formLayout.addRow(nameLabel, nameLineEdit)

        typeLabel = QLabel("Type:")
        typeLineEdit = QLineEdit()
        formLayout.addRow(typeLabel, typeLineEdit)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(dialog.accept)
        buttonBox.rejected.connect(dialog.reject)

        layout.addLayout(formLayout)
        layout.addWidget(buttonBox)

        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            name = nameLineEdit.text()
            entity_type = typeLineEdit.text()
            entity = self.annotation.add_entity(name, entity_type)
            self.annotationListWidget.update_annotations(self.annotation.entities, self.annotation.relations, self.annotation.events)

    # Méthode pour créer une nouvelle relation via une boîte de dialogue
    def create_relation_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Créer Relation")

        layout = QVBoxLayout()
        formLayout = QFormLayout()

        entity1Label = QLabel("Entité 1:")
        entity1ComboBox = QComboBox()
        for entity in self.annotation.entities:
            entity1ComboBox.addItem(entity.name)

        formLayout.addRow(entity1Label, entity1ComboBox)

        entity2Label = QLabel("Entité 2:")
        entity2ComboBox = QComboBox()
        for entity in self.annotation.entities:
            entity2ComboBox.addItem(entity.name)

        formLayout.addRow(entity2Label, entity2ComboBox)

        typeLabel = QLabel("Type:")
        typeLineEdit = QLineEdit()
        formLayout.addRow(typeLabel, typeLineEdit)

        directedLabel = QLabel("Directed:")
        directedCheckBox = QCheckBox()
        formLayout.addRow(directedLabel, directedCheckBox)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(dialog.accept)
        buttonBox.rejected.connect(dialog.reject)

        layout.addLayout(formLayout)
        layout.addWidget(buttonBox)

        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            entity1 = self.annotation.entities[entity1ComboBox.currentIndex()]
            entity2 = self.annotation.entities[entity2ComboBox.currentIndex()]
            relation_type = typeLineEdit.text()
            directed = directedCheckBox.isChecked()
            relation = self.annotation.add_relation(entity1, entity2, relation_type, directed)
            self.annotationListWidget.update_annotations(self.annotation.entities, self.annotation.relations, self.annotation.events)

    # Méthode pour créer un nouvel événement via une boîte de dialogue
    def create_event_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Créer Événement")

        layout = QVBoxLayout()
        formLayout = QFormLayout()

        triggerLabel = QLabel("Trigger:")
        triggerComboBox = QComboBox()
        for entity in self.annotation.entities:
            triggerComboBox.addItem(entity.name)

        formLayout.addRow(triggerLabel, triggerComboBox)

        typeLabel = QLabel("Type:")
        typeLineEdit = QLineEdit()
        formLayout.addRow(typeLabel, typeLineEdit)

        addButton = QPushButton("Ajouter Argument")
        formLayout.addWidget(addButton)

        argumentsLabel = QLabel("Arguments:")
        argumentsListWidget = QListWidget()
        formLayout.addRow(argumentsLabel, argumentsListWidget)

        addButton.clicked.connect(lambda: self.add_argument(argumentsListWidget, triggerComboBox))

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(dialog.accept)
        buttonBox.rejected.connect(dialog.reject)

        layout.addLayout(formLayout)
        layout.addWidget(buttonBox)

        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            trigger = self.annotation.entities[triggerComboBox.currentIndex()]
            event_type = typeLineEdit.text()
            event = self.annotation.add_event(trigger, event_type)
            for index in range(argumentsListWidget.count()):
                item = argumentsListWidget.item(index)
                argument = item.text()
                role, entity_name = argument.split(': ')
                entity = next((e for e in self.annotation.entities if e.name == entity_name), None)
                if entity:
                    event.add_argument(role, entity)
            self.annotationListWidget.update_annotations(self.annotation.entities, self.annotation.relations, self.annotation.events)

    # Méthode pour ajouter un argument à un événement via une boîte de dialogue
    def add_argument(self, argumentsListWidget, triggerComboBox):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter Argument")

        layout = QVBoxLayout()
        formLayout = QFormLayout()

        roleLabel = QLabel("Role:")
        roleLineEdit = QLineEdit()
        formLayout.addRow(roleLabel, roleLineEdit)

        entityLabel = QLabel("Entité:")
        entityComboBox = QComboBox()
        for entity in self.annotation.entities:
            entityComboBox.addItem(entity.name)

        formLayout.addRow(entityLabel, entityComboBox)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(dialog.accept)
        buttonBox.rejected.connect(dialog.reject)

        layout.addLayout(formLayout)
        layout.addWidget(buttonBox)

        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            role = roleLineEdit.text()
            entity = self.annotation.entities[entityComboBox.currentIndex()]
            argumentsListWidget.addItem(f"{role}: {entity.name}")                
    
"""
Main qui ouvre une fenetre 
"""
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
