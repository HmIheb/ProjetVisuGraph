import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QPushButton, QLabel, QDialog
from annotation import Annotation 

"""
Widget listant les annotations et permettant d'avoir plus de détail sur une d'entre elle en double cliquant
"""
class DetailWindow(QDialog):
    def __init__(self, ann):
        super().__init__()
        self.anno = ann
        self.initUI()
    

    def initUI(self):
        self.layout = QVBoxLayout()
        self.nameLabel = QLabel(f'Phrase: {self.anno.phrase}')
        self.layout.addWidget(self.nameLabel)


        # Création des listes d'éléments pour les entités, les relations et les événements
        self.entityListWidget = QListWidget()
        self.relationListWidget = QListWidget()
        self.eventListWidget = QListWidget()

        # Ajout des libellés pour chaque section
        self.layout.addWidget(QLabel("Entities:"))
        self.layout.addWidget(self.entityListWidget)
        self.layout.addWidget(QLabel("Relations:"))
        self.layout.addWidget(self.relationListWidget)
        self.layout.addWidget(QLabel("Events:"))
        self.layout.addWidget(self.eventListWidget)

        self.update_annotations(self.anno.entities,self.anno.relations,self.anno.events)
        

        
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

class AlistWidget(QWidget):
    def __init__(self, objects):
        super().__init__()

        self.objects = objects
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.listWidget = QListWidget()
        for obj in self.objects:
            self.listWidget.addItem(str(obj))

        self.listWidget.itemClicked.connect(self.openDetailWindow)

        self.layout.addWidget(self.listWidget)
        self.setLayout(self.layout)

        self.setWindowTitle('Liste des objets')
        self.setGeometry(50, 50, 400, 300)
        self.show()

    def updatelist(self,l):
        self.listWidget.clear()
        for obj in self.objects:
            self.listWidget.addItem(str(obj))


    def openDetailWindow(self, item):
        obj_name = item.text()
        selected_obj = next((obj for obj in self.objects if str(obj) == obj_name), None)
        if selected_obj:
            self.detailWindow = DetailWindow(selected_obj)
            self.detailWindow.exec_()