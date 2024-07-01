import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                             QWidget, QGraphicsView, QGraphicsScene, 
                             QHBoxLayout, QPushButton, QFileDialog, QLabel, QDialog)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PIL import Image, ImageDraw, ImageFont
from exporter import Exporter
from annotation import Annotation, parse_xml
import AListWidget
from creationWidget import createWindow

# ici g voulu faire un color coding pour l'utiliser dans la fct export image
ENTITY_COLORS = {
    'Company': 'blue',
    'Character': 'green',
    'Place': 'red',
    
}


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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Graph Visualization Tool')
        self.setGeometry(100, 100, 800, 600)

        self.graphVisualizer = GraphVisualizer()
        self.annotation = []

        self.centralWidget = QWidget()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.graphVisualizer)

       
        self.importButton = QPushButton("Import Ace 2005")
        self.importButton.clicked.connect(self.importText)
        self.exportButton = QPushButton("Export Image")
        self.exportButton.clicked.connect(self.export_image)
        self.exportCSVButton = QPushButton("Export CSV")
        self.exportCSVButton.clicked.connect(self.export_to_csv)
        self.addButton = QPushButton("Create Annotation")
        self.addButton.clicked.connect(self.openCreate)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.importButton)
        self.buttonLayout.addWidget(self.exportButton)
        self.buttonLayout.addWidget(self.exportCSVButton)
        self.buttonLayout.addWidget(self.addButton)
        self.layout.addLayout(self.buttonLayout)

        
        self.list = AListWidget.AlistWidget(self.annotation)
        self.layout.addWidget(self.list)

        self.centralWidget.setLayout(self.layout)
        self.setCentralWidget(self.centralWidget)

    def importText(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Import XML File", "", "XML Files (*.xml);;All Files (*)", options=options)
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
            print("CSV Export Successful.")

    def openCreate(self):
        c = createWindow()
        if c.exec_() == QDialog.Accepted:
            obj = c.getObject()
            if obj:
                self.annotation.append(obj)

    def update_annotation_list(self):
        self.annotationListWidget.update_annotations(self.annotation.entities, self.annotation.relations, self.annotation.events)            

    def export_image(self):
        if not self.annotation:
            return
         #va falloir mettre un champs à la place de ça 
        text = "Hello Kitty was created by Sanrio and lives in Birthday Party with her twin sister Mimmy"
        #on découpe bien notre phrase tel une banane dans un banana split ( personne fait ça lol)
        words = text.split()
        #notre canvas de base tout blanc
        image = Image.new('RGB', (1200, 400), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        x, y = 10, 50
        word_positions = {}
        
        def draw_text_with_color(draw, position, text, color, font):
            draw.text(position, text, fill=color, font=font)

        for i, word in enumerate(words):
            entity = None
            for e in self.annotation[0].entities:  
                # on voit ici si notre entité a un attribut "nom" et ça gère aussi les noms composés
                if hasattr(e, 'name') and e.name.lower() in ' '.join(words[i:i + len(e.name.split())]).lower():
                    entity = e
                    break
            
            if entity:
                #on se sert de notre joli color coding pour encadrer les mots
                color = ENTITY_COLORS.get(entity.type, 'black')
                word_length = len(' '.join(words[i:i + len(entity.name.split())]))
                draw.rectangle([x, y, x + word_length * 10, y + 20], outline=color)
                draw.text((x, y), ' '.join(words[i:i + len(entity.name.split())]), fill=color, font=font)
                draw.text((x, y + 20), entity.type[:3].upper(), fill=color, font=font)
                word_positions[entity.name] = (x, y)
                x += word_length * 10 + 10
                i += len(entity.name.split()) - 1
            else:
                draw.text((x, y), word, fill='black', font=font)
                x += len(word) * 10 + 10
        #ici on cherche si 2 entités sont liés par une relation
        for relation in self.annotation[0].relations:
            entity1_pos = word_positions.get(relation.entity1.name)
            entity2_pos = word_positions.get(relation.entity2.name)
            if entity1_pos and entity2_pos:
                draw.line([entity1_pos, entity2_pos], fill='black', width=1)
                mid_x = (entity1_pos[0] + entity2_pos[0]) / 2
                mid_y = (entity1_pos[1] + entity2_pos[1]) / 2
                draw.text((mid_x, mid_y), relation.type, fill='black', font=font)
                
        for event in self.annotation[0].events:
            trigger_pos = word_positions.get(event.trigger.id)
            if trigger_pos:
            # dessiner les trigger en violet
                draw_text_with_color(draw, trigger_pos, event.trigger.name, 'purple', font)
                draw_text_with_color(draw, (trigger_pos[0], trigger_pos[1] + 20), event.type, 'purple', font)

            # on dessine les participants et leur role
                for arg in event.arguments:
                    arg_pos = word_positions.get(arg.entity.id)
                    if arg_pos:
                        draw.line([trigger_pos, arg_pos], fill='purple', width=1)
                        mid_x = (trigger_pos[0] + arg_pos[0]) / 2
                        mid_y = (trigger_pos[1] + arg_pos[1]) / 2
                        draw_text_with_color(draw, (mid_x, mid_y), arg.role, 'purple', font)
                        draw_text_with_color(draw, arg_pos, arg.entity.name, 'purple', font)
                        draw_text_with_color(draw, (arg_pos[0], arg_pos[1] + 20), arg.role, 'purple', font)
       #et hoop en retourne l'image
        image.save('output.png')
        self.graphVisualizer.scene.clear()
        pixmap = QPixmap('output.png')
        self.graphVisualizer.scene.addPixmap(pixmap)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
