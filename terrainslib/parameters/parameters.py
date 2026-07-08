from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

class ParamterSpec(ABC):

    @abstractmethod
    def resolve(self, context):
        ...

class Constant(ParamterSpec):
    def __init__(self, value):
        self.value = value
        
    def resolve(self, context):
        return self.value
    
class Range(ParamterSpec):
    
    def __init__(self, min, max):
        self.min = min
        self.max = max
        
    def resolve(self, context):
        s = context.difficulty
        return self.min + s * (self.max - self.min)
        
        
class Uniform(ParamterSpec):

    def __init__(self, low, high):
        self.low = low
        self.high = high

    def resolve(self, context):
        return context.rng.uniform(self.low, self.high)
    
class Choice(ParamterSpec):
    
    def __init__(self, choices:list, props=None):
        
        self.ch = choices
        if props is None:
            prop = 1/len(choices)
            self.props = np.full_like(choices, prop)
        else:
            self.props = props
    
    def resolve(self, context):
        return np.random.choice(self.ch, p=self.props)
        
        