#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""__init__.py: Basic requirements for the module."""

__license__     = "MIT"
__author__      = "José Fonseca"
__copyright__   = "Copyright (c) 2020 José F. R. Fonseca"


# ======================================================================================================================
# IMPORTS


import random
from functools import lru_cache

from numpy import cos, pi
from symbolic_regression import operators, MAX_VALUE, PRECISION


# ======================================================================================================================
# PAYLOAD


def random_gene(family, input_size):
    if family == 'TERMINAL':
        family = random.choice(operators.TERMINAL)
    elif family == 'PLUS_ONE':
        family = random.choice(operators.PLUS_ONE)
    elif family == 'PLUS_TWO':
        family = random.choice(operators.PLUS_TWO)
    elif family == 'PLUS_TWO_LIGHT':
        family = random.choice(operators.PLUS_TWO_LIGHT)

    if family == 'INPUT':
        return 'INPUT_{};'.format(random.randint(0, input_size-1))
    elif family == 'CONSTANT':
        return '<{}>;'.format(round(cos(random.random() * pi * 2.0) * MAX_VALUE/1e6, PRECISION))
    else:
        return f"{family};"


def generate_decoded_genotype(individual_size, input_size=1):

    genotype = ''
    for level in operators.GRAMMAR(individual_size).split(';'):
        family = random.choice(level.split('|'))
        genotype += random_gene(family, input_size)

    return genotype[:-1]


@lru_cache(1024)
def evaluate_operator(name, *args):
    return getattr(operators, name)(*args)


def evaluate_decoded_genotype(decoded_genotype, *args):
    gene = decoded_genotype.split(';', 1)
    if len(gene) > 1:
        gene, decoded_genotype = gene
    else:
        gene = gene[0]
        decoded_genotype = ''

    if gene.startswith('INPUT_'):
        return args[int(gene.replace('INPUT_', ''))]
    elif gene.startswith('<'):
        return float(gene[1:-1])
    elif gene in operators.PLUS_ONE:
        return evaluate_operator(gene, evaluate_decoded_genotype(decoded_genotype, *args))
    elif gene in operators.PLUS_TWO:
        return evaluate_operator(gene,
            evaluate_decoded_genotype(decoded_genotype, *args),
            evaluate_decoded_genotype(decoded_genotype.split(';', 1)[1], *args)
        )
    else:
        raise TypeError('UNKNOWN GENE {}'.format(gene))


def mutate_decoded_genotype(decoded_genotype, input_size=1, constant_mutation_factor_max=1.0):

    # Select the gene to mutate
    chromossome = decoded_genotype.split(';')
    mutated_position = random.randint(0, len(chromossome)-1)
    original_gene = chromossome[mutated_position]

    # If the original gene is an input and we only have one input, we select another gene to mutate
    while (input_size == 1) and (original_gene.startswith('INPUT_')):
        mutated_position = random.randint(0, len(chromossome)-1)
        original_gene = chromossome[mutated_position]

    # If the original gene is an input and we have more than one input, we mutate the input
    if (input_size > 1) and (original_gene.startswith('INPUT_')):
        new_gene = f'INPUT_{random.randint(0, input_size-1)}'

    # If the original gene is a constant, we mutate it by a limited factor
    elif original_gene.startswith('<'):
        new_gene = '<{}>'.format(float(original_gene[1:-1]) * random.random() * constant_mutation_factor_max)

    else:
        # Select a random family for the chromo from the available families for the position in the grammar
        family = random.choice((operators.GRAMMAR(len(chromossome)).split(';')[mutated_position]).split('|'))
        new_gene = random_gene(family, input_size)[:-1]

    # Alter the gene and return
    chromossome[mutated_position] = new_gene
    return ';'.join(chromossome)

