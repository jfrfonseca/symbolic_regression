#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""__init__.py: Basic requirements for the module."""

__license__     = "MIT"
__author__      = "José Fonseca"
__copyright__   = "Copyright (c) 2020 José F. R. Fonseca"


# ======================================================================================================================
# IMPORTS


import os
import json
from copy import deepcopy

from pandas import DataFrame
from numpy import array, float64, nan, subtract, power

from symbolic_regression import Individual


# ======================================================================================================================
# PAYLOAD


class Environment(object):

    def __init__(self, configuration, starter_population=None):
        self.parse_configuration(configuration)

        self.input = nan
        self.output = nan

        self.population = (
            starter_population
            if starter_population is not None
            else [Individual(self) for _ in range(self.population_size)]
        )

    def fit(self, inputs:list, outputs:list):
        assert isinstance(inputs, (list, tuple)), 'INPUTS MUST BE AN ORDER-PRESERVING LIST!'
        assert isinstance(outputs, (list, tuple)), 'OUTPUTS MUST BE AN ORDER-PRESERVING LIST!'
        assert len(inputs) == len(outputs), 'INPUTS MUST BE OF SAME LENGTH AS OUTPUTS'
        inputs = array([float64(value) for value in inputs])
        outputs = array([float64(value) for value in outputs])

        # Compute the AVERAGE FITNESS of each individual
        fitness = []
        for inp, out in zip(inputs, outputs):
            self.input = inp
            self.output = out
            fitness.append(deepcopy([chromo.reset_values().output() for chromo in self.population]))
        fitness = DataFrame(fitness)
        # Here, the fitness is a dataframe with ONE COLUMN PER INDIVIDUAL/CHROMOSSOME and ONE ROW PER INPUT
        if self.fitness_function_name in {'MSE', 'MSD', 'MEAN_SQUARE_ERROR', 'MEAN_SQUARE_DEVIATION',
                                          'MEAN_SQUARED_ERROR', 'MEAN_SQUARED_DEVIATION'}:
            fitness = fitness.apply(lambda col: power(subtract(outputs, col), 2).mean())  # evaluate each column
        else:
            raise TypeError('UNKNOWN FITNESS FUNCTION: {}'.format(self.fitness_function_name))

        # Here, the fitness is an 1D dataframe with the fitness of each individual/chromossome, in birth order
        return fitness

    def train(self, inputs, outputs): return self.fit(inputs, outputs)

    def parse_configuration(self, configuration):
        if isinstance(configuration, str):
            if os.path.exists(configuration):
                configuration = json.load(open(configuration, 'r'))
            else:
                configuration = json.loads(configuration)

        self.population_size = int(configuration['population_size'])
        self.max_validity_attempts = int(configuration['max_validity_attempts'])
        self.max_size = int(configuration['max_individual_size'])
        self.max_value = float(configuration['max_value'])
        self.max_number_of_targets = int(configuration['max_number_of_targets'])
        self.precision = int(configuration['precision'])
        self.fitness_function_name = str(configuration['fitness_function']).upper().strip().replace(' ', '_')

    def crossover(self, ind_a, ind_b):
        raise NotImplementedError('TO DO CROSSOVER')
