import re

from PyQt5.QtGui import QSyntaxHighlighter, QColor

from .document import Document
from utils import random_hex_color, extract_ngrams, stem_word


class Highlighter(QSyntaxHighlighter):
    def __init__(self, document: Document, parent=None):
        super(Highlighter, self).__init__(parent)
        self.ontoDocument = document
        self.sorted_nodes = sorted(
            self.ontoDocument.attached_nodes,
            key=lambda node: len(node['original_name']),
            reverse=True
        )
        self.colors = [QColor(random_hex_color()) for _ in range(len(self.sorted_nodes))]

    def highlightBlock(self, text: str) -> None:
        for node, current_color in zip(self.sorted_nodes, self.colors):
            n = len(node['name'].split())
            for n_gram in extract_ngrams(text, n):
                normalized_text = ' '.join(stem_word(word) for word in n_gram.split())
                if normalized_text == node['name']:
                    for match in re.finditer(n_gram, text):
                        start, end = match.span()
                        self.setFormat(start, end-start, current_color)
