import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QVBoxLayout, QMainWindow
from PyQt5.QtGui import QPixmap, QPainter ,QImage
from PyQt5.QtCore import Qt
from PIL import Image, ImageDraw, ImageFont

# ici g voulu faire un color coding pour l'utiliser dans la fct export image
ENTITY_COLORS = {
    'Company': 'blue',
    'Character': 'green',
    'Place': 'red',
    
}

class GraphView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
        # Enable dragging
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        
        self.setScene(QGraphicsScene(self))
        
    def add_image(self, pixmap):
        item = QGraphicsPixmapItem(pixmap)
        item.setFlag(QGraphicsPixmapItem.ItemIsMovable)
        item.setFlag(QGraphicsPixmapItem.ItemIsSelectable)
        self.scene().addItem(item)
        
    def wheelEvent(self, event):
        # Zoom factor
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        
        # Set the current zoom factor based on the wheel movement
        zoom_factor = zoom_in_factor if event.angleDelta().y() > 0 else zoom_out_factor
        
        self.scale(zoom_factor, zoom_factor)

    def export_image(self,annotation):
        if not annotation:
            return
         #va falloir mettre un champs à la place de ça 
        text = "Hello Kitty was created by Sanrio and lives in London with her twin sister Mimmy"
        text = annotation.phrase
        #on découpe bien notre phrase 
        words = text.split()
        #notre canvas de base tout blanc
        image = Image.new('RGBA', (1200, 400), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        x, y = 10, 50
        word_positions = {}

        t=0

        for i, word in enumerate(words):
            entity = None
            for e in annotation.entities:  
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
        for relation in annotation.relations:
            entity1_pos = word_positions.get(relation.entity1.name)
            entity2_pos = word_positions.get(relation.entity2.name)
            if entity1_pos and entity2_pos:
                mid_x = (entity1_pos[0] + entity2_pos[0]) / 2
                mid_y = (entity1_pos[1] + entity2_pos[1]) +t / 2
                draw.line([(entity1_pos[0],mid_y), (entity2_pos[0],mid_y)], fill='black', width=1)
                t=t+30
                draw.text((mid_x, mid_y), relation.type, fill='black', font=font)
       #et hoop en retourne l'image
        image_data = image.tobytes("raw", "RGBA")
        qimage = QImage(image_data, image.width, image.height, QImage.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qimage)
        self.add_image(pixmap)

    def delete_selected_image(self):
        selected_items = self.scene().selectedItems()
        for item in selected_items:
            if isinstance(item, QGraphicsPixmapItem):
                self.scene().removeItem(item)


