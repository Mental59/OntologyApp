import os
import nltk
from math import sqrt
from functools import cache
from utils import remove_punctuation, stem_word, count_in_text
from parser import Onto
from dataclasses import dataclass, field
from collections import Counter


@dataclass
class Sentence:
    index: int
    source_sentence: list[str]
    normalized_sentence: list[str]
    attached_nodes: list = field(default_factory=list)


@dataclass
class Metrics:
    p_ij: float = field(default=0)
    e_ij: float = field(default=0)
    b_i: float = field(default=0)
    b_j: float = field(default=0)
    u_b: float = field(default=0)
    p_ij_sqrt: float = field(default=0)
    s_ij: float = field(default=0)
    s_ij_norm: float = field(default=0)


class Document:
    def __init__(self, path: str) -> None:
        self.text = open(path, encoding='utf-8').read()
        self.filepath = path
        self.filename = os.path.basename(path)
        self.node_counts = None
        self.attached_nodes = None
        self.onto = None
        self.metrics = None
        self.rank = None
        self.e = None

        source_sents = nltk.sent_tokenize(self.text)
        processed_sents = [[stem_word(word) for word in nltk.word_tokenize(remove_punctuation(sent))]
                           for sent in source_sents]
        source_sents = [sent.split() for sent in source_sents]

        self.sentences = [Sentence(source_sentence=source_sent, normalized_sentence=processed_sent, index=index)
                          for index, (source_sent, processed_sent) in enumerate(zip(source_sents, processed_sents))]

    def __str__(self):
        return f'Document(filename="{self.filename}")'

    def get_original_text(self) -> str:
        return self.text

    def get_normalized_text(self) -> str:
        sentences = [' '.join(sent.normalized_sentence) for sent in self.sentences]
        return '. '.join(sentences) + '.'

    def process_doc(self, onto: Onto):
        self.onto = onto
        node_counts = Counter()
        for sentence in self.sentences:
            for node in onto.nodes():
                count = count_in_text(s=node['name'], sentence=' '.join(sentence.normalized_sentence))
                if count:
                    node_counts[node['id']] += count
                    sentence.attached_nodes.append(node)
        self.node_counts = node_counts
        self.attached_nodes = [onto.node_dict[node_id] for node_id in node_counts.keys()]

    def get_ont_fragment(self):
        if self.onto is None:
            raise ValueError('onto is not set')

        node_ids = [node['id'] for node in self.attached_nodes]
        onto_fragment = self.onto.get_sub_onto(node_ids)
        return onto_fragment

    def get_node_name(self, node_id):
        if self.onto is None:
            raise ValueError('onto is not set')
        return self.onto.get_node_name(node_id)

    def rank_document(self, n: int, k: int, b: int):
        if self.onto is None:
            raise ValueError('onto is not set')

        self.metrics = self.calc_metrics(n, k, b)
        if len(self.metrics) == 0:
            return 0

        S = [metric.s_ij for metric in self.metrics.values()]
        min_S, max_S = min(S), max(S)

        for metric in self.metrics.values():
            metric.s_ij_norm = (metric.s_ij - min_S) / max_S if max_S != 0 else 0

        r = sum([metric.s_ij_norm for metric in self.metrics.values()]) / len(self.metrics)
        self.rank = r
        return round(r, 3) if r != 0 else 0

    def calc_metrics(self, n: int, k: int, b: int):
        metrics = dict()
        self.e = self.calculate_e()

        for node1 in self.attached_nodes:
            for node2 in self.attached_nodes:
                node_id1 = node1['id']
                node_id2 = node2['id']
                if node_id1 == node_id2: continue

                p_ij = self.onto.get_number_of_paths(node_id1, node_id2, n)
                e_ij = self.e[(node_id1, node_id2)]
                b_i = self.calculate_bi(node_id1, b)
                b_j = self.calculate_bj(node_id2, b)
                u_b = self.calculate_u_b(b)

                p_ij_sqrt = sqrt(p_ij) if p_ij > 0 else 0
                s_ij = p_ij_sqrt * (2 * u_b * e_ij) / (b_i + b_j) if b_i + b_j != 0 else 0

                metrics[(node_id1, node_id2)] = Metrics(
                    p_ij=p_ij,
                    e_ij=e_ij,
                    b_i=b_i,
                    b_j=b_j,
                    u_b=u_b,
                    p_ij_sqrt=p_ij_sqrt,
                    s_ij=s_ij
                )
        return metrics

    @cache
    def calculate_e(self):
        e = dict()
        for node1 in self.attached_nodes:
            for node2 in self.attached_nodes:
                node_id1 = node1['id']
                node_id2 = node2['id']
                if node_id1 == node_id2: continue
                e[(node_id1, node_id2)] = self.calculate_eij(node_id1, node_id2)
        return e

    @cache
    def calculate_eij(self, node_id1, node_id2):
        res = 0
        for sent in self.sentences:
            node_ids = [node['id'] for node in sent.attached_nodes]
            if node_id1 in node_ids and node_id2 in node_ids:
                res += 1
        return res

    @cache
    def calculate_bi(self, node_id, b):
        node_ids = [node['id'] for node in self.attached_nodes if node['id'] != node_id]
        res = sum([1 for node_id2 in node_ids if self.e[(node_id, node_id2)] >= b])
        return res

    @cache
    def calculate_bj(self, node_id, b):
        node_ids = [node['id'] for node in self.attached_nodes if node['id'] != node_id]
        res = sum([1 for node_id1 in node_ids if self.e[(node_id1, node_id)] >= b])
        return res

    @cache
    def calculate_u_b(self, b):
        node_ids = [node['id'] for node in self.attached_nodes]
        results = [self.calculate_bi(node_id, b) for node_id in node_ids]
        return sum(results) / len(results) if len(results) > 0 else 0
