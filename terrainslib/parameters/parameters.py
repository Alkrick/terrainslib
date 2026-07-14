from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import field, dataclass
from copy import deepcopy
from typing import Union, Any
import numpy as np

# def parameter(default):
#     return field(default=default)


def parameter(spec):
    return field(default_factory=lambda: deepcopy(spec))

class ParameterSpec(ABC):

    @abstractmethod
    def resolve(self, difficulty=0):
        ...

    def __call__(self, difficulty=0):
        return self.resolve(difficulty)

    @classmethod
    def from_config(cls, value):

        if isinstance(value, ParameterSpec):
            return value

        if isinstance(value, (tuple, list)):
            return cls(
                *[
                    cls.from_config(v)
                    for v in value
                ]
            )

        return cls(value)

    @classmethod
    def convert(cls, value):

        if isinstance(value, ParameterSpec):
            return value

        if isinstance(value, dict):
            return {
                k: cls.convert(v)
                for k, v in value.items()
            }

        if isinstance(value, (list, tuple)):
            return [
                cls.convert(v)
                for v in value
            ]

        return value

    @classmethod
    def resolve_value(cls, value, difficulty=0):
        """Resolve nested ParameterSpecs recursively."""
        if isinstance(value, ParameterSpec):
            return value.resolve(difficulty)
        return value

ParameterValue = Union[
    float,
    int,
    bool,
    ParameterSpec
]
@dataclass
class Constant(ParameterSpec):
    
    value: Any
    
    def __init__(self, value):
        self.value = value
        
    def resolve(self, difficulty=0):
        return self.resolve_value(self.value, difficulty)
    
@dataclass
class Range(ParameterSpec):
    
    low: Any
    high: Any
    
    def __init__(self, low, high):
        self.low = ParameterSpec.convert(low)
        self.high = ParameterSpec.convert(high)
        
    def resolve(self, difficulty=0):
        
        low = self.resolve_value(self.low, difficulty)
        high = self.resolve_value(self.high, difficulty)

        return low + difficulty * (high - low)
    
    def mid(self, difficulty):
        low = self.resolve_value(self.low, difficulty)
        high = self.resolve_value(self.high, difficulty)
        
        return (high+low)/2

@dataclass 
class Uniform(ParameterSpec):
    
    min: Any
    max: Any
    
    def __init__(self, min, max):
        self.min = ParameterSpec.convert(min)
        self.max = ParameterSpec.convert(max)
    
    def resolve(self, difficulty=0):
        
        min = self.resolve_value(self.min, difficulty)
        max = self.resolve_value(self.max, difficulty)
        
        return np.random.uniform(min, max)
    
    def mid(self, difficulty):
        
        min = self.resolve_value(self.min, difficulty)
        max = self.resolve_value(self.max, difficulty)
        
        return (max+min)/2
    
@dataclass
class Normal(ParameterSpec):
    
    mean: Any
    std: Any

    def __init__(self, mean, std):
        self.mean = ParameterSpec.convert(mean)
        self.std =  ParameterSpec.convert(std)

    def resolve(self, difficulty=0):
        mean = self.resolve_value(self.mean, difficulty)
        std = self.resolve_value(self.std, difficulty)

        return np.random.normal(mean, std)
@dataclass
class Choice(ParameterSpec):
    
    choices: list
    probs: list

    def __init__(self, choices, probs=None):
        self.choices = [
            ParameterSpec.convert(c) for c in choices
        ]

        self.probs = probs
        if probs is None:
            self.probs = np.full(len(choices), 1 / len(choices))
    
    @classmethod
    def from_config(cls, value):
        return cls(**value)

    def resolve(self, difficulty=0):
        choice = np.random.choice(self.choices, p=self.probs)
        return self.resolve_value(choice, difficulty)