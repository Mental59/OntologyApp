from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QFont
from .document import Document


class DocumentMetricsGUI(QMainWindow):
    def __init__(self, parent, document: Document):
        super(DocumentMetricsGUI, self).__init__(parent=parent)
        uic.loadUi('doc_metrics.ui', self)
        self.font = QFont('MS Shell Dlg 2', 14)
        self.document = document
        self.setup_table()
        self.fill_table()

    def setup_table(self):
        for i in range(9):
            self.table.setColumnWidth(i, 220)
        header = self.table.verticalHeader()
        header.setSectionResizeMode(QHeaderView.Fixed)
        header.setDefaultSectionSize(25)

    def fill_table(self):
        metrics = self.document.metrics
        if metrics is None:
            return
        for node_id1, node_id2 in metrics.keys():
            name1 = self.document.get_node_name(node_id1)
            name2 = self.document.get_node_name(node_id2)
            metric = metrics[(node_id1, node_id2)]
            self.__insert_item_to_table(
                name1,
                name2,
                round(metric.s_ij, 3),
                round(metric.s_ij_norm, 3),
                round(metric.p_ij, 3),
                round(metric.u_b, 3),
                round(metric.e_ij, 3),
                round(metric.b_i, 3),
                round(metric.b_j, 3)
            )

    def __create_item(self, value):
        item = QTableWidgetItem(str(value))
        item.setFont(self.font)
        return item

    def __insert_item_to_table(self, *args):
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        for index, arg in enumerate(args):
            self.table.setItem(row_count, index, self.__create_item(arg))
