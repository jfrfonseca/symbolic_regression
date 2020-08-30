#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""__init__.py: Basic requirements for the module."""

__license__     = "MIT"
__author__      = "José Fonseca"
__copyright__   = "Copyright (c) 2020 José F. R. Fonseca"


# ======================================================================================================================
# IMPORTS


from hashlib import sha1
from random import choice, randint

from symbolic_regression.node import Node, Empty, Input
from symbolic_regression.basic import Constant, Sum

NODES_LIST = [
    Empty,
    Input,
    Constant,
    Sum
]


OPERATION_NODES = [
    Sum
]


# ======================================================================================================================
# PAYLOAD


class Individual(object):

    def __init__(self, environment):
        self._env = environment
        max_validity_attempts = self._env.max_validity_attempts
        self.validity_attempts = 0
        if max_validity_attempts < 1:
            self._chromossome = self.create()
        else:
            for validity_attempt in range(self._env.max_validity_attempts):
                self._chromossome = self.create()
                self.validity_attempts += 1
                if self.is_valid(): break
            assert self.is_valid(), 'UNABLE TO CREATE VALID INDIVIDUAL IN {} ATTEMPTS!'.format(self.validity_attempts)

    def available_nodes(self, position):
        return [
            node_class for node_class in NODES_LIST
            if position+node_class.MIN_QUANTITY_OF_TARGETS < self._env.max_size
        ]

    def create(self) -> list:

        # Created a chromo with random types of nodes.
        chromo = [choice(self.available_nodes(position))(self, position) for position in range(self._env.max_size)]

        # If the chromo does not have at least one input node, we add one
        if not any([gene.symbol == '<INPUT>' for gene in chromo]):
            position = randint(0, len(chromo)-1)
            chromo[position] = Input(self, position)
        return chromo

    def _visit_gene(self, gene):
        yield gene
        for target in gene.targets():
            for sub_gene in self._visit_gene(target):
                yield sub_gene

    def tree(self):
        for gene in self._chromossome:
            if isinstance(gene, tuple(OPERATION_NODES)):
                for gene in self._visit_gene(gene):
                    yield gene
                break

    def is_valid(self):
        input_reached = False
        for pos, gene in enumerate(self.tree()):
            if not gene.is_valid():
                return False
            if (pos > 0) and (gene.symbol == '<INPUT>'):
                input_reached = True
        return input_reached

    def output(self) -> float:
        return next(self.tree()).operate()

    def print(self, validity_attempts=False, genotype=True, chromossome=True) -> str:
        if genotype:
            result = '; '.join([str(gene) for gene in self])
        else:
            result = [str(gene) for gene in self.tree()]
            result = '; '.join(['[FENOTYPE |{}| (^{}) (~{}) (v{})]'.format(
                                    len(result),
                                    round(self.output(), self._env.precision),
                                    round((self._env.output - self.output())**2, self._env.precision),
                                    self._env.output
                               )] + result if chromossome else [])

            if validity_attempts:
                result = '[ValidityAttempts {}]; '.format(self.validity_attempts) + result

        return result

    @property
    def id(self) -> str:
        return str(sha1(self.print().encode('utf-8')).hexdigest())

    def __iter__(self):
        for gene in self._chromossome:
            yield gene

    def reset_values(self):
        self._chromossome = [gene.reset_value() for gene in self._chromossome]
        return self

    def __repr__(self): return '<Individual {}>'.format(self.id)
    def __getitem__(self, item) -> Node: return self._chromossome[item]
    def __setitem__(self, key, value) -> None: self._chromossome[key] = value
    def __sizeof__(self) -> int: return len(self._chromossome)
