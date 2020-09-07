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
        self._value = (1 if random() > 0.5 else -1) * random() * self._env.numerical_value_max
        return []

    def operation(self, input, *args) -> float:
        return self._value

    def mutation(self) -> list:
        if random() < self._env.mutation_target:
            self._value = self._value * ((1 if random() > 0.5 else -1) * random() * self._env.mutation_constants_factor_max)
        return []

    def __repr__(self):
        return self.symbol.replace('<', '<[{}] '.format(self._position)).replace('>', ' (${}...)>'.format(round(self._value, 3)))



class Sum(Node):

    _symbol = '<SUM>'
    MIN_QUANTITY_OF_TARGETS = 2

    def create(self) -> list:
        quantity = self._env.targets_max
        assert quantity >= 2, 'INVALID max_number_of_targets FOR <SUM>! MUST BE >= 2'
        start = self.position + 1
        end = self._env.individual_size - 1
        return [randint(start, end) for _ in range(min(randint(2, quantity), end-start+1))]

    def operation(self, input, *args) -> float:
        return sum([t.operate(input) for t in self.targets()])
