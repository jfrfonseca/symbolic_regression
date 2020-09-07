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
from hashlib import sha1
from copy import deepcopy
from random import shuffle, choice

from pandas import DataFrame
from scipy.stats import kurtosis, skew as skewness
from numpy import array, float64, nan, subtract, power, sum, random, max, min, mean, std, percentile

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

        self._statistics = []

    def parse_configuration(self, configuration):
        if isinstance(configuration, str):
            if os.path.exists(configuration):
                configuration = json.load(open(configuration, 'r'))
            else:
                configuration = json.loads(configuration)

        self.population_size = int(configuration['population_size'])
        self.validity_attempts = int(configuration['validity_attempts'])
        self.individual_size = int(configuration['individual_size'])
        self.numerical_value_max = float(configuration['numerical_value_max'])
        self.targets_max = int(configuration['targets_max'])
        self.fitness_function_name = str(configuration['fitness_function']).upper().strip().replace(' ', '_')
        self.selection_function_name = str(configuration['selection_function']).upper().strip().replace(' ', '_')
        self.selection_group_size = int(configuration['selection_group_size'])
        self.selection_population_size = int(configuration['selection_population_size'])  # "selection", not "selected". Stay in pattern.
        self.elitism_size = int(configuration['elitism_size'])
        self.crossover_function_name = str(configuration['crossover_function']).upper().strip().replace(' ', '_')
        self.mutation_target = float(configuration['mutation_target_probability'])
        self.mutation_type = float(configuration['mutation_type_probability'])
        self.mutation_constants_factor_max = float(configuration['mutation_constants_factor_max'])

    # Fitness function -------------------------------------------------------------------------------------------------

    def fit(self, inputs:list, outputs:list):
        assert isinstance(inputs, (list, tuple)), 'INPUTS MUST BE AN ORDER-PRESERVING LIST!'
        assert isinstance(outputs, (list, tuple)), 'OUTPUTS MUST BE AN ORDER-PRESERVING LIST!'
        assert len(inputs) == len(outputs), 'INPUTS MUST BE OF SAME LENGTH AS OUTPUTS'
        inputs = array([float64(value) for value in inputs])
        outputs = array([float64(value) for value in outputs])

        # Compute the fitness of each individual in each input
        fitness = DataFrame([deepcopy([chromo.output(inpu) for chromo in self.population]) for inpu in inputs])

        # Here, the fitness is a dataframe with ONE COLUMN PER INDIVIDUAL/CHROMOSSOME and ONE ROW PER INPUT
        if self.fitness_function_name in {'MSE', 'MSD', 'MEAN_SQUARE_ERROR', 'MEAN_SQUARE_DEVIATION',
                                          'MEAN_SQUARED_ERROR', 'MEAN_SQUARED_DEVIATION'}:
            fitness = fitness.apply(lambda col: power(subtract(outputs, col), 2).mean())  # evaluate each column
        elif self.fitness_function_name in {'RMSE', 'RMSD', 'ROOT_MEAN_SQUARE_ERROR', 'ROOT_MEAN_SQUARE_DEVIATION',
                                            'ROOT_MEAN_SQUARED_ERROR', 'ROOT_MEAN_SQUARED_DEVIATION'}:
            fitness = fitness.apply(lambda col: power(power(subtract(outputs, col), 2).mean(), 1/2))  # evaluate each column
        else:
            raise TypeError('UNKNOWN FITNESS FUNCTION: {}'.format(self.fitness_function_name))

        # Here, the fitness is an 1D array with the fitness of each individual/chromossome, in birth order
        return fitness

    # Selection --------------------------------------------------------------------------------------------------------

    def roulette_selection(self, fitness: list, group: list) -> int:
        """
        The Roulette selection method privileges chromossomes with LARGER
        fitness values. Our fitness is an ERROR function, in which better-fit
        individuals have SMALLER fitness values. Thus, we must compute the
        COMPLEMENT of each fitness value, making smaller values larger and vice-
        -versa. The proportion of each value must be preserved as much as possible,
        so we compute the complete-value (sum of the largest and smaller values),
        and convert each value to its complement in the over-value range.
        :param fitness:
        :param group:
        :return:
        """

        # Get only the fitnesses of the individuals in the group, find the max and min values, and sum those two
        selected_fitnesses = [fitness[chromo_pos] for chromo_pos in group]
        over_value = max(selected_fitnesses) + min(selected_fitnesses)
        complemented_fitnesses = subtract(over_value, selected_fitnesses)

        # Choose a random value between 0 and the sum of the complemented fitnesses
        roulette_stop = random.random() * sum(complemented_fitnesses)

        # Sum the values of the complemented fitness of each chromo in the group, returning the number of the chromo
        # that reaches the roulette stop
        total_fitness = 0.0
        for chromo_pos, chromo_complemented_fitness in zip(group, complemented_fitnesses):
            total_fitness += chromo_complemented_fitness
            if total_fitness >= roulette_stop:
                return chromo_pos

    def tournament_selection(self, fitness: list, group: list) -> int:

        # Sort the elements by their fitness and return the first one (smaller error, best fit!)
        return sorted(zip([fitness[chromo_pos] for chromo_pos in group], group))[0][1]

    def apply_selection(self, fitness:list):

        # Get the chosen selection function
        if self.selection_function_name in {'ROULETTE', 'ROULETTE_SELECTION'}:
            selection_function = self.roulette_selection
        elif self.selection_function_name in {'TOURNAMENT', 'TOURNAMENT_SELECTION'}:
            selection_function = self.tournament_selection
        else:
            raise TypeError('UNKNOWN SELECTION FUNCTION: {}'.format(self.selection_function_name))

        # Generate a random sequence of all individuals in the population, with at least the required size elements
        sequence_required_size = self.selection_group_size * self.selection_population_size
        sequence = list(range(len(self.population)))
        while len(sequence) < sequence_required_size:
            sequence += sequence
        shuffle(sequence)

        # Iterate blocks of individuals performing the selection
        selected_population = [
            selection_function(
                fitness,
                sequence[int(block * self.selection_group_size) : int((block + 1) * self.selection_group_size)]
            )
            for block in range(self.selection_population_size)
        ]

        # Return the selected population as an array of POSITIONS of nodes
        return selected_population

    # Crossover --------------------------------------------------------------------------------------------------------

    def random_reprodution_crossover(self, crossing_population: list, target_population_size: int):
        return [self.population[choice(crossing_population)].copy() for _ in range(target_population_size)]

    def single_point_crossover(self, crossing_population: list, target_population_size: int):
        raise NotImplementedError('TODO')

    def uniform_crossover(self, crossing_population: list, target_population_size: int):
        raise NotImplementedError('TODO')

    def apply_crossover(self, crossing_population: list, target_population_size: int):

        # Get the chosen selection function
        if self.crossover_function_name in {
            'RANDOM_REPRODUCTION', 'RANDOM', 'REPRODUCTION',
            'RANDOM_REPRODUCTION_CROSSOVER', 'RANDOM_CROSSOVER', 'REPRODUCTION_CROSSOVER'
        }:
            crossover_function = self.random_reprodution_crossover
        elif self.crossover_function_name in {'SINGLE_POINT', 'SINGLE_POINT_CROSSOVER'}:
            crossover_function = self.single_point_crossover
        elif self.crossover_function_name in {'UNIFORM', 'UNIFORM_CROSSOVER'}:
            crossover_function = self.uniform_crossover
        else:
            raise TypeError('UNKNOWN CROSSOVER FUNCTION: {}'.format(self.crossover_function_name))

        return crossover_function(crossing_population, target_population_size)

    # Mutation ---------------------------------------------------------------------------------------------------------

    def apply_mutation(self, mutating_population: list):

        for chromo in mutating_population:
            if random.random() < self.mutation_type:
                chromo.mutate_type()
            elif random.random() < self.mutation_target:
                chromo.mutate_target()

        return mutating_population

    # Iteration --------------------------------------------------------------------------------------------------------

    def elitism(self, fitness: list):

        # Sort the elements by their fitness and return the fist few (smaller error, best fit!)
        return [self.population[el[1]].copy()
                for el in sorted(zip(fitness, range(len(self.population))))[:self.elitism_size]]

    def epoch(self, inputs, outputs, inplace=False):

        # Apply the fitness function and compute the selected population as an array of POSITIONS of elements
        fitness = self.fit(inputs, outputs)
        new_population_pointers = self.apply_selection(fitness)

        # Apply crossover on the selected population until we have a whole new population (applying elitism as needed)
        # Here, the selected population is an array of INTEGERS, representing the POSITIONS of each Individual object
        # in the popullation array
        new_population_objects = self.apply_crossover(new_population_pointers, self.population_size - self.elitism_size)

        # Apply mutation to the new population. Here, the new population is an array of new Individual objects
        new_population_objects = self.apply_mutation(new_population_objects)

        # Apply elitism to the new population
        new_population_objects += self.elitism(fitness)

        # Set the new population
        if inplace:
            self.update_statistics(fitness)
            self.population = new_population_objects
        else:
            return new_population_objects

    def update_statistics(self, fitness):
        self._statistics.append({
            'min': min(fitness), 'max': max(fitness), 'mean': mean(fitness), 'std': std(fitness),
            'skewness': skewness(fitness), 'kurtosis': kurtosis(fitness),
            # 'histogram_5': [percentile(fitness, percent/100) for percent in range(5, 100, 5)],
            # 'population_id': sha1('; '.join(sorted([ind.id for ind in self.population])).encode('utf-8')).hexdigest(),
            # 'population': [(self.population[pos].id, fit) for fit, pos in sorted(zip(fitness, range(len(self.population))))]
        })

    @property
    def statistics(self): return DataFrame(self._statistics)
