import sys
from PyQt5.QtWidgets import (QMessageBox, QVBoxLayout, QHBoxLayout, QDialog, 
                             QLabel, QComboBox, QPushButton)
from annotation import Annotation,pointcommun_annotation,difference_annotation

class comparaisonDialog(QDialog):
    def __init__(self, annotations,w):
        super().__init__()
        self.window=w
        self.annotations1 = annotations
        self.annotations2 = annotations
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        # Label and ComboBox for the first list of annotations
        self.label1 = QLabel('Choose from List 1:')
        self.comboBox1 = QComboBox()
        for annotation in self.annotations1:
            self.comboBox1.addItem(str(annotation))

        # Label and ComboBox for the second list of annotations
        self.label2 = QLabel('Choose from List 2:')
        self.comboBox2 = QComboBox()
        for annotation in self.annotations2:
            self.comboBox2.addItem(str(annotation))

        # Add labels and combo boxes to the layout
        self.layout.addWidget(self.label1)
        self.layout.addWidget(self.comboBox1)
        self.layout.addWidget(self.label2)
        self.layout.addWidget(self.comboBox2)

        # Button layout
        self.buttonLayout = QHBoxLayout()
        self.button1 = QPushButton('Générer Graphe intersection')
        self.button2 = QPushButton('Générer Graphe Différence')
        self.button3 = QPushButton('Metriques')

        self.button1.clicked.connect(self.common)
        self.button2.clicked.connect(self.diff)
        self.button3.clicked.connect(self.showmetric)


        self.buttonLayout.addWidget(self.button1)
        self.buttonLayout.addWidget(self.button2)
        self.buttonLayout.addWidget(self.button3)

        # Add button layout to the main layout
        self.layout.addLayout(self.buttonLayout)

        # Set dialog layout
        self.setLayout(self.layout)
        self.setWindowTitle('Annotation Selection Dialog')
        self.setGeometry(100, 100, 400, 200)
    
    def get_selected_annotations(self):
        selected_annotation1 = self.annotations1[self.comboBox1.currentIndex()]
        selected_annotation2 = self.annotations2[self.comboBox2.currentIndex()]
        return selected_annotation1, selected_annotation2
    
    def common(self):
        a1,a2= self.get_selected_annotations()
        if a1.phrase == a2.phrase:
            t=pointcommun_annotation(a1,a2)
            self.window.annotation.append(t)
            self.window.graphVisualizer.export_image(t)
            self.close()

    def diff(self):
        a1,a2= self.get_selected_annotations()
        if a1.phrase == a2.phrase:
            t=difference_annotation(a1,a2)
            self.window.annotation.append(t)
            self.window.graphVisualizer.export_image(t)
            self.close()

    def precision(self,tp, fp):
        return tp / (tp + fp) if (tp + fp) > 0 else 0

    
    def recall(self,tp, fn):
        return tp / (tp + fn) if (tp + fn) > 0 else 0

    
    def f1_score(self,precision, recall):
        return 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    
    def calculate_metrics(self,tp, fp, fn):
        precision = self.precision(tp, fp)
        recall = self.recall(tp, fn)
        f1 = self.f1_score(precision, recall)
        return precision, recall, f1

    def compare_entities(self,entities1, entities2):
        tp = len(set(entities1) & set(entities2))
        fp = len(set(entities1) - set(entities2))
        fn = len(set(entities2) - set(entities1))
        return tp, fp, fn

    def compare_relations(self,relations1, relations2):
        tp = len(set(relations1) & set(relations2))
        fp = len(set(relations1) - set(relations2))
        fn = len(set(relations2) - set(relations1))
        return tp, fp, fn

    def compare_events(self,events1, events2):
        tp = len(set(events1) & set(events2))
        fp = len(set(events1) - set(events2))
        fn = len(set(events2) - set(events1))
        return tp, fp, fn

   


    def showmetric(self):
        a1,a2=self.get_selected_annotations()
        if a1.phrase == a2.phrase:

            tp, fp, fn = self.compare_entities(a1.entities, a2.entities)
            entity_precision, entity_recall, entity_f1 = self.calculate_metrics(tp, fp, fn)

            tp, fp, fn = self.compare_relations(a1.relations, a2.relations)
            relation_precision, relation_recall, relation_f1 = self.calculate_metrics(tp, fp, fn)

            tp, fp, fn = self.compare_events(a1.events, a2.events)
            event_precision, event_recall, event_f1 = self.calculate_metrics(tp, fp, fn)

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)

            msg.setText(f'''Pour les entités :\n 
                                   Précision = {entity_precision}\n
                                   Rappel = {entity_recall} \n
                                   Score F1 = {entity_f1} \n
Pour les relations :\n 
                                   Précision = {relation_precision}\n
                                   Rappel = {relation_recall} \n
                                   Score F1 = {relation_f1} \n
Pour les events :\n 
                                   Précision = {event_precision}\n
                                   Rappel = {event_recall} \n
                                   Score F1 = {event_f1} \n''')

            msg.setWindowTitle("Metrique")
            msg.exec()