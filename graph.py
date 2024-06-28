import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QHBoxLayout, QPushButton, QFileDialog, QLineEdit, QLabel)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import cv2
import numpy as np
from annotation import parse_xml, parse_json, Annotation


# la phrase pour tester "Ehud Barak met Yasser Arafat in Paris to discuss the Middle East peace process" avec test_pal.xml

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.annotation = None

    def initUI(self):
        self.setWindowTitle('Outil de Visualisation de Texte Annoté')
        self.setGeometry(100, 100, 800, 600)

        self.centralWidget = QWidget()
        self.layout = QVBoxLayout()
        
        self.textInput = QLineEdit(self)
        self.textInput.setPlaceholderText("Entrez une phrase ici")
        self.layout.addWidget(self.textInput)
        
        self.importButton = QPushButton("Import XML/JSON")
        self.importButton.clicked.connect(self.importFile)
        self.layout.addWidget(self.importButton)
        
        self.processButton = QPushButton("Traiter le texte")
        self.processButton.clicked.connect(self.processText)
        self.layout.addWidget(self.processButton)
        
        self.exportButton = QPushButton("Exporter l'image")
        self.exportButton.clicked.connect(self.exportImage)
        self.layout.addWidget(self.exportButton)
        
        self.imageLabel = QLabel(self)
        self.layout.addWidget(self.imageLabel)
        
        self.centralWidget.setLayout(self.layout)
        self.setCentralWidget(self.centralWidget)

    def importFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Import File", "", "XML Files (*.xml);;JSON Files (*.json);;All Files (*)", options=options)
        if fileName:
            if fileName.endswith('.xml'):
                with open(fileName, 'r', encoding='utf-8') as file:
                    self.annotation = parse_xml(file)
            elif fileName.endswith('.json'):
                with open(fileName, 'r', encoding='utf-8') as file:
                    self.annotation = parse_json(file)

    def processText(self):
        if not self.annotation:
            print("Veuillez d'abord importer un fichier XML ou JSON.")
            return

        phrase = self.textInput.text()
        self.annotation.phrase = phrase
        
        # ici limage blanche de base
        img = np.ones((600, 800, 3), np.uint8) * 255
        
        # la je dessine le texte ct super nul avec pillow, opencv c mieux
        cv2.putText(img, phrase, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        # les entités de merde
        y_offset = 60
        for entity in self.annotation.entities:
            if entity.name.lower() in phrase.lower():
                start = phrase.lower().index(entity.name.lower())
                end = start + len(entity.name)
                cv2.rectangle(img, (start*10, y_offset-20), (end*10, y_offset), (255, 0, 0), 2)
                cv2.putText(img, entity.type, (start*10, y_offset+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        
        # les relations
        y_offset = 120
        for relation in self.annotation.relations:
            text = f"{relation.entity1.name} - {relation.type} -> {relation.entity2.name}"
            cv2.putText(img, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            y_offset += 30
        
        # les events 
        y_offset += 30
        for event in self.annotation.events:
            text = f"Event: {event.type} (Trigger: {event.trigger.name})"
            cv2.putText(img, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            y_offset += 30
            for role, argument in event.arguments:
                text = f"  - {role}: {argument.name}"
                cv2.putText(img, text, (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                y_offset += 30
        
        # convertir l'image en QPixmap et l'afficher, merci a reddit pour cette partie entierement copiée collée hhhh
        height, width, channel = img.shape
        bytesPerLine = 3 * width
        qImg = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.imageLabel.setPixmap(QPixmap.fromImage(qImg))

    def exportImage(self):
        if self.imageLabel.pixmap():
            options = QFileDialog.Options()
            fileName, _ = QFileDialog.getSaveFileName(self, "Sauvegarder l'image", "", "PNG Files (*.png);;JPG Files (*.jpg);;All Files (*)", options=options)
            if fileName:
                self.imageLabel.pixmap().save(fileName)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
