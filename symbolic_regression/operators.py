#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""__init__.py: Basic requirements for the module."""

__license__     = "MIT"
__author__      = "José Fonseca"
__copyright__   = "Copyright (c) 2020 José F. R. Fonseca"


# ======================================================================================================================
# IMPORTS


import re
import numpy as np

from symbolic_regression import MIN_VALUE, MAX_VALUE


# ======================================================================================================================
# GENES


# Single-argument
def INVERSE(arg): return -1.0 * arg
def EXPONENTIAL(arg): return np.exp(arg)
# def LN(arg): return np.ln(arg)
def SIN(arg): return np.sin(arg * np.pi * 2.0)
def COSIN(arg): return np.cos(arg * np.pi * 2.0)
def TANGENT(arg): return np.tan(arg * np.pi * 2.0)
def SQUARE(arg): return np.power(arg, 2)
def CUBE(arg): return np.power(arg, 3)
def SQRT(arg): return np.sqrt(arg)
def MODULO(arg): return np.abs(arg)
def PASS(arg): return arg

# Dual-Argument (simple)
def ADD(arg_a, arg_b): return arg_a + arg_b
def SUBTRACT(arg_a, arg_b): return arg_a - arg_b
def MULTIPLY(arg_a, arg_b): return arg_a * arg_b
def DIVIDE(arg_a, arg_b): return (arg_a / arg_b) if (arg_b != 0) else arg_a

# Dual-Argument
def POWER(arg_a, arg_b): return np.power(arg_a, arg_b)
def ROOT(arg_a, arg_b): return np.power(arg_a, 1.0/arg_b)
def LOG(arg_a, arg_b): return np.log(arg_a, arg_b)
def MOD(arg_a, arg_b): return (arg_a % arg_b) if (arg_b != 0) else arg_a

# Terminals
INPUT = ['INPUT']
TERMINAL = [
    'CONSTANT'
] + INPUT

# Single-argument
PLUS_ONE = [
    'INVERSE',
    # 'EXPONENTIAL',
    # 'LN',
    'SIN',
    'COSIN',
    'TANGENT',
    'SQUARE',
    'CUBE',
    'SQRT',
    'MODULO',
    'PASS'
]

# Dual argument
PLUS_TWO_LIGHT = [
    'ADD',
    'SUBTRACT',
    'MULTIPLY',
    'DIVIDE'
]
PLUS_TWO = [
    # 'POWER',
    # 'ROOT',
    # 'LOG',
    'MOD'
] + PLUS_TWO_LIGHT

OPERATORS = PLUS_ONE + PLUS_TWO


# Grammar
def GRAMMAR(individual_size:int):
    if individual_size <= 1:
        return 'TERMINAL'
    elif individual_size == 2:
        return 'PLUS_ONE|TERMINAL;TERMINAL'
    elif individual_size < 6:
        return 'PLUS_TWO|PLUS_ONE|TERMINAL;'*(individual_size-2) + 'PLUS_ONE|TERMINAL;TERMINAL'
    else:
        return ('PLUS_TWO|PLUS_TWO_LIGHT|PLUS_TWO_LIGHT|PLUS_ONE|PLUS_ONE|TERMINAL;'*(individual_size-2)
                 + 'PLUS_ONE|TERMINAL|INPUT;TERMINAL|INPUT')


# ======================================================================================================================
# ENCODE/DECODE


def encode_value(value: float) -> str:
    if value > MAX_VALUE:  # Space limitarion
        value = MAX_VALUE
    if value < MIN_VALUE:
        value = MIN_VALUE
    value = int((value * 1e6) + MAX_VALUE)  # Now the value is a positive integer between 0 and 2*MAX_VALUE
    value = bin(value ^ (value >> 1))[2:]  # Gray code
    value = '0'*(64-len(value))+value  # 0-padding
    # Shuffle the string to improve locality
    fist_half = list(value[:32])
    second_half = list(value[32:])
    second_half.reverse()
    return ''.join([a+b for a, b in zip(second_half, fist_half)])


def decode_value(encoded_value:str) -> float:
    # Un-shuffle the string
    value = list(encoded_value)
    second_half = value[0::2]
    second_half.reverse()
    first_half = value[1::2]
    value = ''.join(first_half+second_half)
    value = int(value, 2)  # Decoded the binary string
    inv = 0
    while(value):
        inv = inv ^ value
        value = value >> 1  # Decoded the gray code
    value = inv
    return (value - MAX_VALUE) / 1e6  # Decoded the space limitation


class Xlator(dict):
    """ All-in-one multiple-string-substitution class
    Source: https://www.oreilly.com/library/view/python-cookbook/0596001673/ch03s15.html
    """

    def _make_regex(self):
        """ Build re object based on the keys of the current dictionary """
        return re.compile("|".join(map(re.escape, self.keys(  ))))

    def __call__(self, match):
        """ Handler invoked for each regex match """
        return self[match.group(0)]

    def xlat(self, text):
        """ Translate text, returns the modified text. """
        return self._make_regex(  ).sub(self, text)


# Encoding
ENCODING_OPERATORS = {
    operator: encode_value(position)
    for position, operator in enumerate(OPERATORS+[f'INPUT_{i}' for i in range(10)])
}
DECODING_OPERATORS = {value: operator for operator, value in ENCODING_OPERATORS.items()}


def encode_genotype(genotype):

    # Replace the operators
    genotype = Xlator(ENCODING_OPERATORS).xlat(genotype).split(';')

    # Replace the constants and encode as binary
    return ''.join([
        (encode_value(float(gene[1:-1])) if gene.startswith('<') else gene)
        for gene in genotype
    ])


def decode_genotype(genotype):
    genotype = Xlator(DECODING_OPERATORS).xlat(
        ';'.join([genotype[64*i:64*(i+1)] for i in range(int(len(genotype)/64))])
    )
    return ';'.join([(f'<{decode_value(gen)}>' if gen[0] in '01' else gen) for gen in genotype.split(';')])
