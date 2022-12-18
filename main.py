import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
from PyQt5 import uic
from PyQt5.QtCore import Qt

from document.document import Document
from document.documentGUI import DocumentGUI
from document.docMetricsGUI import DocumentMetricsGUI
from parser import Onto


class GUI(QMainWindow):
    def __init__(self):
        super(GUI, self).__init__()
        uic.loadUi('app.ui', self)
        self.__set_handlers()
        self.font = QFont('MS Shell Dlg 2', 14)
        self.ontology = None
        self.setup_table_widget()

    def setup_table_widget(self):
        self.tableWidget.setColumnWidth(0, 500)
        self.tableWidget.setColumnWidth(1, 100)
        header = self.tableWidget.verticalHeader()
        header.setSectionResizeMode(QHeaderView.Fixed)
        header.setDefaultSectionSize(25)

    def get_n_value(self):
        return int(self.nSpinBox.value())

    def get_k_value(self):
        return int(self.kSpinBox.value())

    def get_b_value(self):
        return int(self.bSpinBox.value())

    def __set_handlers(self):
        self.loadOntButton.clicked.connect(self.load_ontology_file)
        self.loadDocsButton.clicked.connect(self.load_docs)
        self.loadedDocsList.itemClicked.connect(self.on_list_item_click)
        self.rankingButton.clicked.connect(self.rank_documents)
        self.tableWidget.clicked.connect(self.open_doc_metric_info)

    def load_ontology_file(self):
        try:
            filepath = QFileDialog.getOpenFileName(
                parent=self,
                caption='Выберите файл онтологии',
                directory='',
                filter='Файл онтологии (*.ont)'
            )[0]
            if filepath:
                self.ontology = Onto.load_from_file(filepath)
                self.set_loaded_ontology_name(os.path.basename(str(filepath)))
                self.process_docs()
                self.tableWidget.setRowCount(0)

        except Exception as e:
            error_dialog = QErrorMessage(parent=self)
            error_dialog.setWindowTitle('Ошибка при загрузке онтологии')
            error_dialog.showMessage(str(e))

    def set_loaded_ontology_name(self, name):
        self.loadedOntFileName.setText(name)

    def load_docs(self):
        filepaths = QFileDialog.getOpenFileNames(self, 'Выберите текстовые файлы документов', '', 'Документ (*.txt)')[0]
        for filepath in filepaths:
            self.add_document_to_listview(Document(filepath))
        if filepaths:
            self.process_docs()

    def add_document_to_listview(self, document: Document):
        index = self.loadedDocsList.count() + 1
        item = QListWidgetItem(f'{index}) {document.filename}')
        item.setFont(self.font)
        item.setData(Qt.UserRole, document)
        self.loadedDocsList.addItem(item)

    def on_list_item_click(self, item: QListWidgetItem):
        if self.ontology is None:
            return
        document = item.data(Qt.UserRole)
        doc_window = DocumentGUI(parent=self, document=document)
        doc_window.show()

    def get_documents(self):
        return [self.loadedDocsList.item(i).data(Qt.UserRole) for i in range(self.loadedDocsList.count())]

    def process_docs(self):
        if self.ontology is None:
            return
        for doc in self.get_documents():
            doc.process_doc(onto=self.ontology)

    def rank_documents(self):
        documents = self.get_documents()

        if self.ontology is None:
            QMessageBox.about(self, 'Ошибка', 'Не выбрана онтология')
            return
        if len(documents) == 0:
            QMessageBox.about(self, 'Ошибка', 'Не загружены документы')
            return

        n = self.get_n_value()
        k = self.get_k_value()
        b = self.get_b_value()

        self.tableWidget.setRowCount(0)

        doc_ranks = [(doc.rank_document(n, k, b), index) for index, doc in enumerate(documents)]

        for doc_rank, doc_index in sorted(doc_ranks, reverse=True):
            doc = documents[doc_index]
            doc_name = doc.filename
            self.__insert_item_to_table(doc_name, doc_rank, doc)

    def __insert_item_to_table(self, doc_name, rank, document):
        row_count = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_count)
        item1 = QTableWidgetItem(str(doc_name))
        item2 = QTableWidgetItem(str(rank))
        item1.setData(Qt.UserRole, document)
        item2.setData(Qt.UserRole, document)
        item1.setFont(self.font)
        item2.setFont(self.font)
        self.tableWidget.setItem(row_count, 0, item1)
        self.tableWidget.setItem(row_count, 1, item2)

    def open_doc_metric_info(self, item):
        document = item.data(Qt.UserRole)
        doc_metric_gui = DocumentMetricsGUI(self, document)
        doc_metric_gui.show()


def main():
    app = QApplication([])
    window = GUI()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
