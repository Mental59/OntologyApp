from PyQt5.QtWidgets import *
from PyQt5 import uic


class DocumentTextGUI(QMainWindow):
    def __init__(self, parent, document):
        super(DocumentTextGUI, self).__init__(parent=parent)
        uic.loadUi('doc_text.ui', self)
        self.textWidget.setText(document.text)
