#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""__init__.py: Basic requirements for the module."""

__license__     = "MIT"
__author__      = "José Fonseca"
__copyright__   = "Copyright (c) 2020 José F. R. Fonseca"


# ======================================================================================================================
# IMPORTS


import abc
from copy import deepcopy
from random import randint

from numpy import random


# ======================================================================================================================
# PAYLOAD - NODE


class Node(abc.ABC):

    _symbol = '<>'
    _value = None
    MIN_QUANTITY_OF_TARGETS = 0

    def __init__(self, individual, position):
        self._chromo = individual
        self._env = individual._env
        self._position = position
        self._targets = self.create()

    @abc.abstractmethod
    def create(self) -> list: return []

    @abc.abstractmethod
    def operation(self, *args) -> float: return 0.0

    def mutation(self) -> list:
        new_targets = []
        for target in self._targets:
            if random.random() < self._env.mutation_target:
                new_targets.append(randint(self._position+1, self._env.individual_size-1))
            else:
                new_targets.append(target)
        return new_targets

    def mutate(self):
        self._targets = self.mutation()

    def targets(self):
        for target_position in self._targets:
            yield self._chromo[target_position]

    def operate(self, input) -> float:
        return self.operation(input, *[t.operate(input) for t in self.targets()])

    def is_valid(self) -> bool:
        return all([t.symbol not in {'<>', '<EMPTY>'} for t in self.targets()])

    @property
    def position(self) -> int: return self._position
    @property
    def symbol(self) -> str: return self._symbol

    def copy(self):
        other = self.__class__(self._chromo, self._position)
        other._targets = deepcopy(self._targets)
        other._value = self._value
        return other

    def __repr__(self):
        return (self.symbol
                .replace('<', '<[{}] '.format(self._position))
                .replace('>', ' ({})>'.format(','.join([str(t) for t in self._targets]))))


class EmptyOperationError(Exception): pass


class Empty(Node):

    _symbol = '<EMPTY>'
    MIN_QUANTITY_OF_TARGETS = 0

    def create(self) -> list: return []
    def operation(self, input, *args) -> float: raise EmptyOperationError(str(self))
    def __repr__(self): return self.symbol.replace('<', '<[{}] '.format(self._position))


class Input(Node):

    _symbol = '<INPUT>'
    MIN_QUANTITY_OF_TARGETS = 0

    def create(self) -> list: return []
    def operation(self, input, *args) -> float: return input
    def __repr__(self): return self.symbol.replace('<', '<[{}] '.format(self._position))
