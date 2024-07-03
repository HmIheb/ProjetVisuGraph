import re
import sys
from PyQt5.QtWidgets import (QMenu,QAction,QApplication, QMainWindow, QTextEdit, QVBoxLayout, 
                             QWidget, QGraphicsView, QGraphicsScene, 
                             QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem,
                             QHBoxLayout, QPushButton, QFileDialog, QLabel, QDialog, QFormLayout, QLineEdit, QDialogButtonBox, 
                             QComboBox, QCheckBox, QListWidget)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QImage,QPainter
from exporter import Exporter
from annotation import Annotation,parse_xml
import AListWidget
from creationWidget import createWindow
from graphVisual import GraphView
from comparaison import comparaisonDialog


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
        
        self.compaButton = QPushButton("Outil de comparaison")
        self.compaButton.clicked.connect(self.comparer)

        self.exportButton = QPushButton("Export")
        self.exportButton.clicked.connect(self.showExportMenu)
        

        self.addButton = QPushButton("Créer annotation")
        self.addButton.clicked.connect(self.openCreate)
        
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.importButton)
        self.buttonLayout.addWidget(self.compaButton)
        self.buttonLayout.addWidget(self.exportButton)
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
            print("hawlik " + fileName)
        
        if fileName.endswith('.apf.xml'):
            fiich_sgm = fileName.replace('.apf.xml', '.sgm')
        else:
            print(f"L'extension n'est pas bonne: {fileName}")
            return

        try:
            with open(fiich_sgm, 'r', encoding='utf-8') as sgm_file:
                contenu = sgm_file.read()
        except FileNotFoundError:
            print(f"Le fichier sgm correspondant n'est pas ici: {fiich_sgm}")
            return

        # dans cette nouvelle version on ignore les autres tags
        match = re.search(r'<TEXT>(.*?)</TEXT>', contenu, re.IGNORECASE | re.DOTALL)
        if match:
            text_content = match.group(1).strip()
            a.phrase = text_content

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

    def showExportMenu(self):
        menu = QMenu(self)

        exportImageAction = QAction('Export as Image', self)
        exportImageAction.triggered.connect(self.export_to_image)
        menu.addAction(exportImageAction)

        exportXMLAction = QAction('Export as XML', self)
        exportXMLAction.triggered.connect(self.export_to_xml)
        menu.addAction(exportXMLAction)

        exportCSVAction = QAction('Export as CSV', self)
        exportCSVAction.triggered.connect(self.export_to_csv)
        menu.addAction(exportCSVAction)

        menu.exec_(self.mapToGlobal(self.exportButton.pos()))
    
    def export_to_image(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Export Image", "", "PNG Files (*.png);;All Files (*)", options=options)
        if fileName:
            self.export_scene_to_image(self.graphVisualizer.scene, fileName)    
    
    def export_scene_to_image(self, scene: QGraphicsScene, file_path: str):
        rect = scene.itemsBoundingRect()
        image = QImage(rect.size().toSize(), QImage.Format_ARGB32)
        image.fill(Qt.white)
        
        painter = QPainter(image)
        scene.render(painter)
        painter.end()
        
        image.save(file_path)
    
    def export_to_xml(self):
        options = QFileDialog.Options()
        i=0
        fileName, _ = QFileDialog.getSaveFileName(self, "Export XML", "", "XML Files (*.xml);;All Files (*)", options=options)
        if fileName:
            for a in self.annotation:
                uri = fileName.split('/')[-1].replace('.xml', '')
                docid = uri
                Exporter.export_to_xml(a.entities, a.relations, a.events, fileName, uri, docid)
                i=i+1
                print("Exportation en XML réussie.")
    
    #ouvre la fenetre de creation d'annotation 
    def openCreate(self):
        c = createWindow()
        if c.exec_() == QDialog.Accepted:
            obj = c.getObject()
            if obj:
                self.annotation.append(obj)
                self.graphVisualizer.export_image(obj)
                self.list.updatelist()

    def comparer(self):
        c = comparaisonDialog(self.annotation,self)
        c.exec_()

"""
Main qui ouvre une fenetre 
"""
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
