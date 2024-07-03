import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, 
                             QWidget, QGraphicsView, QGraphicsScene, 
                             QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem,
                             QHBoxLayout, QPushButton, QFileDialog, QLabel, QDialog, QFormLayout, QLineEdit, QDialogButtonBox, 
                             QComboBox, QCheckBox, QListWidget,QMenu,QAction)
from annotation import Annotation 
from PyQt5.QtCore import Qt

"""
Fenetre permettant la création d'annotation
"""
class createWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.annotation = Annotation()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.nameLabel = QLabel('Phrase:')
        self.phrase = QTextEdit()
        self.layout.addWidget(self.nameLabel)
        self.layout.addWidget(self.phrase)

        # Création des listes d'éléments pour les entités, les relations et les événements
        self.entityListWidget = QListWidget()
        self.relationListWidget = QListWidget()
        self.eventListWidget = QListWidget()

        # Ajouter les menus contextuels
        self.entityListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.entityListWidget.customContextMenuRequested.connect(self.show_entity_context_menu)

        self.relationListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.relationListWidget.customContextMenuRequested.connect(self.show_relation_context_menu)

        self.eventListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.eventListWidget.customContextMenuRequested.connect(self.show_event_context_menu)


        # Ajouter les boutons pour créer des entités, des relations et des événements
        self.createEntityButton = QPushButton("Créer Entité")
        self.createEntityButton.clicked.connect(self.create_entity_dialog)
        self.createRelationButton = QPushButton("Créer Relation")
        self.createRelationButton.clicked.connect(self.create_relation_dialog)
        self.createEventButton = QPushButton("Créer Événement")
        self.createEventButton.clicked.connect(self.create_event_dialog)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.createEntityButton)
        self.buttonLayout.addWidget(self.createRelationButton)
        self.buttonLayout.addWidget(self.createEventButton)

        # Ajout des libellés pour chaque section
        self.layout.addWidget(QLabel("Entities:"))
        self.layout.addWidget(self.entityListWidget)
        self.layout.addWidget(QLabel("Relations:"))
        self.layout.addWidget(self.relationListWidget)
        self.layout.addWidget(QLabel("Events:"))
        self.layout.addWidget(self.eventListWidget)

        self.update_annotations(self.annotation.entities,self.annotation.relations,self.annotation.events)
        self.layout.addLayout(self.buttonLayout)


        self.button = QPushButton('OK', self)
        self.button.clicked.connect(self.accept)
        
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)
        self.setWindowTitle('Détails de l\'objet')
        self.setGeometry(100, 100, 300, 200)

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
    # Méthode pour créer une nouvelle entité via une boîte de dialogue
    def create_entity_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Créer Entité")

        layout = QVBoxLayout()
        formLayout = QFormLayout()

        idLabel = QLabel("ID:")
        idLineEdit = QLineEdit()
        formLayout.addRow(idLabel, idLineEdit)

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
            id= idLineEdit.text()
            name = nameLineEdit.text()
            entity_type = typeLineEdit.text()
            entity = self.annotation.add_entity(id,name, entity_type)
            self.update_annotations(self.annotation.entities, self.annotation.relations, self.annotation.events)

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
            self.update_annotations(self.annotation.entities, self.annotation.relations, self.annotation.events)

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
            self.update_annotations(self.annotation.entities, self.annotation.relations, self.annotation.events)

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
    
    def show_entity_context_menu(self, position):
        menu = QMenu()
        delete_action = QAction('Supprimer', self)
        delete_action.triggered.connect(lambda: self.delete_item(self.entityListWidget))
        menu.addAction(delete_action)
        menu.exec_(self.entityListWidget.viewport().mapToGlobal(position))

    def show_relation_context_menu(self, position):
        menu = QMenu()
        delete_action = QAction('Supprimer', self)
        delete_action.triggered.connect(lambda: self.delete_item(self.relationListWidget))
        menu.addAction(delete_action)
        menu.exec_(self.relationListWidget.viewport().mapToGlobal(position))

    def show_event_context_menu(self, position):
        menu = QMenu()
        delete_action = QAction('Supprimer', self)
        delete_action.triggered.connect(lambda: self.delete_item(self.eventListWidget))
        menu.addAction(delete_action)
        menu.exec_(self.eventListWidget.viewport().mapToGlobal(position))

    def delete_item(self, list_widget):
        selected_items = list_widget.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            row = list_widget.row(item)
            list_widget.takeItem(row)

            # Remove from annotation data
            if list_widget == self.entityListWidget:
                del self.annotation.entities[row]
            elif list_widget == self.relationListWidget:
                del self.annotation.relations[row]
            elif list_widget == self.eventListWidget:
                del self.annotation.events[row]

    def getObject(self):
        self.annotation.phrase = self.phrase.toPlainText()
        return getattr(self, 'annotation', None)