from random import uniform, randint

# Represents a range from which
# we can uniformly choose a random value
class RandRange:

    def __init__(self, x, y):
        if x < y:
            self.low = x
            self.high = y
        else:
            self.low = y
            self.high = x
    
    # Choose a random value from this range
    def evaluate(self):
        return uniform(self.low, self.high)

    def __str__(self):
        return f"rand({self.low}, {self.high})"

    def __repr__(self):
        return str(self)
        
    def __add__(self, other):
        if issubclass(type(other), RandRange):
            return RandRange(self.low + other.low, self.high + other.high)
        else:
            return RandRange(self.low + other, self.high + other)
    
    def __sub__(self, other):
        if issubclass(type(other), RandRange):
            return RandRange(self.low - other.high, self.high - other.low)
        else:
            return RandRange(self.low - other, self.high - other)
    
    def __mul__(self, other):
        if issubclass(type(other), RandRange):
            return RandRange(self.low * other.low, self.high * other.high)
        else:
            return RandRange(self.low * other, self.high * other)
    
    def __truediv__(self, other):
        if issubclass(type(other), RandRange):
            return RandRange(self.low / other.high, self.high / other.low)
        else:
            return RandRange(self.low / other, self.high / other)
    
    def __radd__(self, other):
        return self + other
    
    def __rsub__(self, other):
        return self - other
    
    def __rmul__(self, other):
        return self * other
    
    def __rtruediv__(self, other):
        return self / other
    
    def __neg__(self):
        return 0 - self
        
    def union(self, other):
        return RandRange(min(self.low, other.low), max(self.high, other.high))

# As above but only generates integers
class RandIntRange(RandRange):

    def evaluate(self):
        return randint(self.low, self.high)

    def __str__(self):
        return f"randint({self.low}, {self.high})"

