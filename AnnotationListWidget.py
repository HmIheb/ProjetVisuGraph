from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel
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