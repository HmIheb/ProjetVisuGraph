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
from annotation import Annotation,parse_xml
from AnnotationListWidget import AnnotationListWidget
import AListWidget
from creationWidget import createWindow

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
        
        self.annotation = []
        

        self.centralWidget = QWidget()
        self.layout = QVBoxLayout()
        
        self.layout.addWidget(self.graphVisualizer)
        
        # Ajouter les boutons d'importation et d'exportation
        self.importButton = QPushButton("Import Ace 2005")
        self.importButton.clicked.connect(self.importText)
        self.exportButton = QPushButton("Export Image")
        
        self.exportCSVButton = QPushButton("Export CSV")
        self.exportCSVButton.clicked.connect(self.export_to_csv)

        self.addButton = QPushButton("Créer annotation")
        self.addButton.clicked.connect(self.openCreate)
        
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.importButton)
        self.buttonLayout.addWidget(self.exportButton)
        self.buttonLayout.addWidget(self.exportCSVButton)
        self.buttonLayout.addWidget(self.addButton)
        

        self.layout.addLayout(self.buttonLayout)

        

        # Ajouter le widget de liste d'annotations
        self.list=AListWidget.AlistWidget(self.annotation)
        self.layout.addWidget(self.list)
        
        self.centralWidget.setLayout(self.layout)
        self.setCentralWidget(self.centralWidget)

    def importText(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Import xml File", "", "Xml Files (*.xml);;All Files (*)", options=options)
        if fileName:
            with open(fileName, 'r', encoding='utf-8') as file:
                a = parse_xml(file)
        self.annotation.append(a)
        self.list.updatelist(self.annotation)

    def export_to_csv(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if fileName:
            Exporter.export_to_csv(self.annotation.entities, self.annotation.relations, self.annotation.events, fileName)
            print("Exportation en CSV réussie.")

    def openCreate(self):
        c = createWindow()
        if c.exec_() == QDialog.Accepted:
            obj = c.getObject()
            if obj:
                self.annotation.append(obj)

    # Mettre à jour la liste des annotations dans AnnotationListWidget
    def update_annotation_list(self):
        self.annotationListWidget.update_annotations(self.annotation.entities, self.annotation.relations, self.annotation.events)            

"""
Main qui ouvre une fenetre 
"""
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
