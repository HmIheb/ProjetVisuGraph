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
import AListWidget
from creationWidget import createWindow
from graphVisual import GraphView


# MainWindow pour intégrer toutes les fonctionnalités
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Outil de Visualisation de Graphes')
        self.setGeometry(100, 100, 800, 600)

        self.graphVisualizer = GraphView()
        
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
        self.list=AListWidget.AlistWidget(self.annotation,self)
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
        self.graphVisualizer.export_image(a)
        self.list.updatelist()

    def export_to_csv(self):
        options = QFileDialog.Options()
        i=0
        fileName, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if fileName:
            for a in self.annotation:
                Exporter.export_to_csv(a.entities, a.relations, a.events, fileName+i.__str__())
                i=i+1
                print("Exportation en CSV réussie.")

    #ouvre la fenetre de creation d'annotation 
    def openCreate(self):
        c = createWindow()
        if c.exec_() == QDialog.Accepted:
            obj = c.getObject()
            if obj:
                self.annotation.append(obj)
                self.graphVisualizer.export_image(obj)
                self.list.updatelist()

"""
Main qui ouvre une fenetre 
"""
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
