#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""__init__.py: Basic requirements for the module."""

__license__     = "MIT"
__author__      = "José Fonseca"
__copyright__   = "Copyright (c) 2020 José F. R. Fonseca"


# ======================================================================================================================
# IMPORTS


import pandas as pd
from numpy import asarray, power, subtract

from symbolic_regression.genotype import generate_decoded_genotype, evaluate_decoded_genotype


# ======================================================================================================================
# CREATION


def create_decoded_population(population_size, individual_size, input_size=1):
    return [generate_decoded_genotype(individual_size, input_size) for _ in population_size]


# ======================================================================================================================
# FITNESS


def fitness_decoded_genotype(decoded_genotype, input_array, output_array, fitness_function_name):

    # Compute the output for every input
    observed_outputs = asarray([
        evaluate_decoded_genotype(decoded_genotype, *inp if isinstance(inp, (list, tuple)) else inp)
        for inp in input_array
    ], dtype=float)

    # Compute the fitness function
    if fitness_function_name in {'MSE', 'MSD', 'MEAN_SQUARE_ERROR', 'MEAN_SQUARE_DEVIATION',
                                 'MEAN_SQUARED_ERROR', 'MEAN_SQUARED_DEVIATION'}:
        fitness = power(subtract(output_array, observed_outputs), 2).mean()
    elif fitness_function_name in {'RMSE', 'RMSD', 'ROOT_MEAN_SQUARE_ERROR', 'ROOT_MEAN_SQUARE_DEVIATION',
                                   'ROOT_MEAN_SQUARED_ERROR', 'ROOT_MEAN_SQUARED_DEVIATION'}:
        fitness = power(power(subtract(output_array, observed_outputs), 2).mean(), 1/2)
    else:
        raise TypeError('UNKNOWN FITNESS FUNCTION: {}'.format(fitness_function_name))

    return fitness


# ======================================================================================================================
# SELECTION
