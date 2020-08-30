#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""__init__.py: Basic requirements for the module."""

__license__     = "MIT"
__author__      = "José Fonseca"
__copyright__   = "Copyright (c) 2020 José F. R. Fonseca"


# ======================================================================================================================
# IMPORTS


import abc


# ======================================================================================================================
# PAYLOAD - NODE


class Node(abc.ABC):

    _symbol = '<>'
    _mutable = True
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

    @abc.abstractmethod
    def mutation(self) -> ([], float): return [], None

    def mutate(self):
        self._targets, self._value = self.mutation()

    def targets(self):
        for target_position in self._targets:
            yield self._chromo[target_position]

    def operate(self) -> float:
        if self._value is None:
            self._value = self.operation(*[t.operate() for t in self.targets()])
        return self._value

    def is_valid(self) -> bool:
        return all([t.symbol not in {'<>', '<EMPTY>'} for t in self.targets()])

    @property
    def position(self) -> int: return self._position
    @property
    def symbol(self) -> str: return self._symbol
    @property
    def mutable(self) -> bool: return self._mutable

    def reset_value(self):
        self._value = None
        return self

    def __repr__(self):
        return (self.symbol
                .replace('<', '<[{}] '.format(self._position))
                .replace('>', ' ({})>'.format(','.join([str(t) for t in self._targets]))))


class EmptyOperationError(Exception): pass


class Empty(Node):

    _symbol = '<EMPTY>'
    _mutable = False
    MIN_QUANTITY_OF_TARGETS = 0

    def create(self) -> list:
        return []

    def operation(self, *args) -> float:
        raise EmptyOperationError(str(self))

    def mutation(self) -> (list, float): return [], None

    def __repr__(self):
        return self.symbol.replace('<', '<[{}] '.format(self._position))


class Input(Node):

    _symbol = '<INPUT>'
    _mutable = False
    MIN_QUANTITY_OF_TARGETS = 0

    def create(self) -> list:
        return []

    def operation(self, *args) -> float:
        return self._env.input

    def mutation(self) -> (list, float):
        return [], None

    def __repr__(self):
        return self.symbol.replace('<', '<[{}] '.format(self._position)).replace('>', ' (@{})>'.format(self._env.input))
