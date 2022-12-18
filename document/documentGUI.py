import json
import re
from datetime import datetime
import os
from glob import glob

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QFont

from .highlighter import Highlighter
from .document import Document
from .documentTextGUI import DocumentTextGUI


class DocumentGUI(QMainWindow):
    def __init__(self, parent, document: Document):
        super(DocumentGUI, self).__init__(parent=parent)
        uic.loadUi('doc.ui', self)
        self.document = document
        self.font = QFont('MS Shell Dlg 2', 14)
        self.docTextButton.clicked.connect(lambda: self.show_document_text(document))
        self.saveOntButton.clicked.connect(lambda: self.save_ont(document))

        attached_concepts = [
            (document.node_counts[node['id']], node['original_name']) for node in document.attached_nodes
        ]
        attached_concepts = [
            (index + 1, name, count) for index, (count, name) in enumerate(sorted(attached_concepts, reverse=True))
        ]
        attached_sentences = [
            ' '.join(sent.source_sentence)for sent in document.sentences if sent.attached_nodes
        ]

        if attached_concepts:
            self.saveOntButton.setEnabled(True)

        self.set_content(concepts=attached_concepts, sentences=attached_sentences)
        self.highlighter = Highlighter(document=document, parent=self.sentTextBrowser.document())

    def set_content(self, concepts: list, sentences: list):
        concepts = [self.list_item_with_font(f'{index}. {name} ({count})') for index, name, count in concepts]
        for concept in concepts:
            self.attachedConceptsList.addItem(concept)

        if not concepts:
            self.attachedConceptsList.addItem(self.list_item_with_font('Понятия не привязались'))
        else:
            self.sentTextBrowser.setText('\n'.join(sentences))

    def list_item_with_font(self, s: str):
        item = QListWidgetItem(s)
        item.setFont(self.font)
        return item

    def show_document_text(self, document):
        doc_window = DocumentTextGUI(parent=self, document=document)
        doc_window.show()

    def get_ont_save_filepath(self, filename: str, ext: str = 'ont'):
        now = datetime.now().strftime('%d-%m-%Y')
        ont_name = f'{os.path.splitext(filename)[0]}_{now}'
        self.__create_folder_if_not_exists('data')
        self.__create_folder_if_not_exists('data/saved_ontologies')
        path = os.path.abspath('data/saved_ontologies')
        same_filenames = [os.path.basename(path) for path in glob(os.path.join(path, f'{ont_name}*.json'))]
        file_numbers = self.__get_file_numbers(same_filenames, ext)
        if file_numbers:
            new_filename = f'{ont_name} ({max(file_numbers) + 1}).{ext}'
        else:
            new_filename = f'{ont_name}.{ext}'
        return os.path.join(path, new_filename)

    def __create_folder_if_not_exists(self, name: str):
        if not os.path.exists(name):
            os.mkdir(name)

    def __get_file_numbers(self, filenames, ext):
        file_numbers = []
        for filename in filenames:
            match = re.search(fr"(?<=\()\d+(?=\)\.{ext}$)", filename)
            if match is None:
                file_numbers.append(0)
            else:
                file_numbers.append(int(match.group()))
        return file_numbers

    def save_ont(self, document):
        save_filepath = self.get_ont_save_filepath(document.filename)
        ont_fragment = document.get_ont_fragment()
        with open(save_filepath, 'w') as file:
            json.dump(ont_fragment, file)
        QMessageBox.about(self, 'Онтология успешно сохранена', f'Онтология сохранена по пути: {save_filepath}')
