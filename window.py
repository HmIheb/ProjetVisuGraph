import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, 
                             QWidget, QGraphicsView, QGraphicsScene, 
                             QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem,
                             QHBoxLayout, QPushButton, QFileDialog, QLabel, QDialog, QFormLayout, QLineEdit, QDialogButtonBox)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPen, QBrush, QFont
import networkx as nx

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
        

        self.centralWidget = QWidget()
        self.layout = QVBoxLayout()
        
        self.layout.addWidget(self.graphVisualizer)
        
        # Ajouter les boutons d'importation et d'exportation
        self.importButton = QPushButton("Import Ace 2005")
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
        fileName, _ = QFileDialog.getOpenFileName(self, "Import xml File", "", "Xml Files (*.xml);;All Files (*)", options=options)
        if fileName:
            with open(fileName, 'r', encoding='utf-8') as file:
                text = file.read()
                #appeler le parser ici
                
    
"""
Main qui ouvre une fenetre 
"""
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())