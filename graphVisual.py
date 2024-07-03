import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QVBoxLayout, QMainWindow
from PyQt5.QtGui import QPixmap, QPainter, QImage
from PyQt5.QtCore import Qt
from PIL import Image, ImageDraw, ImageFont


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
        
        
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        
        self.setScene(QGraphicsScene(self))
        
    def add_image(self, pixmap):
        item = QGraphicsPixmapItem(pixmap)
        item.setFlag(QGraphicsPixmapItem.ItemIsMovable)
        item.setFlag(QGraphicsPixmapItem.ItemIsSelectable)
        self.scene().addItem(item)
        
    def wheelEvent(self, event):
        
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        
        
        zoom_factor = zoom_in_factor if event.angleDelta().y() > 0 else zoom_out_factor
        
        self.scale(zoom_factor, zoom_factor)

    def export_image(self, annotation):
        if not annotation:
            return
        
        text = annotation.phrase
        words = text.split()
        image = Image.new('RGBA', (1200, 800), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        x, y = 10, 50
        line_height = 30
        word_positions = {}

       
        def draw_text_with_color(draw, position, text, color, font):
            draw.text(position, text, fill=color, font=font)

       
        i = 0
        while i < len(words):
            word = words[i]
            found_entity = False

            for e in annotation.entities:
                entity_words = e.name.split()
                if ' '.join(words[i:i + len(entity_words)]).lower() == e.name.lower():
                    color = ENTITY_COLORS.get(e.type, 'black')
                    entity_text = ' '.join(words[i:i + len(entity_words)])
                    draw.rectangle([x, y, x + len(entity_text) * 10, y + 20], outline=color)
                    draw_text_with_color(draw, (x, y), entity_text, color, font)
                    draw_text_with_color(draw, (x, y + 20), e.type[:3].upper(), color, font)
                    word_positions[e.id] = (x, y)
                    x += len(entity_text) * 10 + 10
                    i += len(entity_words)
                    found_entity = True
                    break

            if not found_entity:
                draw_text_with_color(draw, (x, y), word, 'black', font)
                x += len(word) * 10 + 10
                i += 1

            if x > 1100:  # si on depasse la limite bah zip
                x = 10
                y += line_height

         # regarde comment je saute de ligne 
            #y += line_height 

       
        t=10
        for relation in annotation.relations:
            entity1_pos = word_positions.get(relation.entity1.id)
            entity2_pos = word_positions.get(relation.entity2.id)
            if entity1_pos and entity2_pos:
                mid_x = (entity1_pos[0] + entity2_pos[0]) / 2
                mid_y = (entity1_pos[1] + entity2_pos[1]) +t/ 2
                t=t
                draw.line([entity1_pos, entity2_pos], fill='black', width=1)
                draw_text_with_color(draw, (mid_x, mid_y), relation.type, 'black', font) 
        # je saute encore
        #y += line_height * 2

       
        for event in annotation.events:
            trigger_pos = word_positions.get(event.trigger.id)
            if trigger_pos:
                # les triggers
                draw_text_with_color(draw, (trigger_pos[0], y), event.trigger.name, 'purple', font)
                draw_text_with_color(draw, (trigger_pos[0], y + line_height), event.type, 'purple', font)

                # arguments et roles
                for role, arg_entity in event.arguments:
                    arg_pos = word_positions.get(arg_entity.id)
                    if arg_pos:
                        draw.line([trigger_pos, (arg_pos[0], y)], fill='purple', width=1)
                        mid_x = (trigger_pos[0] + arg_pos[0]) / 2
                        mid_y = (trigger_pos[1] + y) / 2
                        draw_text_with_color(draw, (mid_x, mid_y), role, 'purple', font)
                        draw_text_with_color(draw, (arg_pos[0], y), arg_entity.name, 'purple', font)
                        draw_text_with_color(draw, (arg_pos[0], y + line_height), role, 'purple', font)

               # JE SAUTE ENCOOORE
               # y += line_height * 2

        combined_image_data = image.tobytes("raw", "RGBA")
        qimage = QImage(combined_image_data, image.width, image.height, QImage.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qimage)
        self.add_image(pixmap)

    def delete_selected_image(self):
        selected_items = self.scene().selectedItems()
        for item in selected_items:
            if isinstance(item, QGraphicsPixmapItem):
                self.scene().removeItem(item)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graph Visualizer")
        self.setGeometry(100, 100, 1200, 800)
        
        self.graphVisualizer = GraphView()
        
        layout = QVBoxLayout()
        layout.addWidget(self.graphVisualizer)
        
        container = QMainWindow()
        container.setLayout(layout)
        
        self.setCentralWidget(container)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
