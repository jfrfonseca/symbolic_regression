#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""__init__.py: Basic requirements for the module."""

__license__     = "MIT"
__author__      = "José Fonseca"
__copyright__   = "Copyright (c) 2020 José F. R. Fonseca"


# ======================================================================================================================
# IMPORTS


from random import random, randint, choice


from symbolic_regression.node import Node


# ======================================================================================================================
# PAYLOAD


class Constant(Node):

    _symbol = '<CONST>'
    MIN_QUANTITY_OF_TARGETS = 0

    def create(self) -> list:
        self._value = (1 if random() > 0.5 else -1) * random() * self._env.max_value
        return []

    def reset_value(self):
        return self

    def operation(self, *args) -> float:
        return self._value

    def mutation(self) -> (list, float):
        return [], self._value + ((1 if random() > 0.5 else -1) * random() * self._env.max_mutation_value)

    def __repr__(self):
        return self.symbol.replace('<', '<[{}] '.format(self._position)).replace('>', ' (${})>'.format(round(self._value, self._env.precision)))



class Sum(Node):

    _symbol = '<SUM>'
    MIN_QUANTITY_OF_TARGETS = 2

    def create(self) -> list:
        quantity = self._env.max_number_of_targets
        assert quantity >= 2, 'INVALID max_number_of_targets FOR <SUM>! MUST BE >= 2'
        start = self.position + 1
        end = self._env.max_size - 1
        return [randint(start, end) for _ in range(min(randint(2, quantity), end-start+1))]

    def operation(self, *args) -> float:
        if self._value is None:
            self._value = sum([t.operate() for t in self.targets()])
        return self._value

    def mutation(self) -> (list, float):
        new_targets = self._targets.copy()
        new_targets[choice(list(range(len(self._targets))))] = randint(self.position+1, self._env.max_size+1)
        return new_targets.copy(), None
