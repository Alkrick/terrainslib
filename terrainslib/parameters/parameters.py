from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

class ParameterSpec(ABC):

    @abstractmethod
    def resolve(self, difficulty):
        """Compute the value of this parameter."""
        ...

    def __call__(self, difficulty):
        return self.resolve(difficulty)
    
    @classmethod
    def from_config(cls, value):
        if isinstance(value, cls):
            return value

        if isinstance(value, (tuple, list)):
            return cls(*value)

        return cls(value)

    @classmethod
    def _resolve(cls, value, difficulty):
        """Resolve nested ParameterSpecs recursively."""
        if isinstance(value, ParameterSpec):
            return value.resolve(difficulty)
        return value

class Constant(ParameterSpec):
    def __init__(self, value):
        self.value = value
        
    def resolve(self, difficulty):
        return self._resolve(self.value, difficulty)
    
class Range(ParameterSpec):
    
    def __init__(self, min, max):
        self.min = min
        self.max = max
        
    def resolve(self, difficulty):
        
        min = self._resolve(self.min, difficulty)
        max = self._resolve(self.max, difficulty)

        return min + difficulty * (max - min)
        
        
class Normal(ParameterSpec):

    def __init__(self, mean, std):
        self.mean = mean
        self.std = std

    def resolve(self, difficulty):
        mean = self._resolve(self.mean, difficulty)
        std = self._resolve(self.std, difficulty)

        return np.random.normal(mean, std)
    
class Choice(ParameterSpec):

    def __init__(self, choices, probs=None):
        self.choices = choices

        if probs is None:
            self.probs = np.full(len(choices), 1 / len(choices))
        else:
            self.probs = probs
    
    @classmethod
    def from_config(cls, value):
        return cls(**value)

    def resolve(self, difficulty):
        choice = np.random.choice(self.choices, p=self.probs)
        return self._resolve(choice, difficulty)