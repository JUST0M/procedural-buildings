from random import uniform, randint
from interval import interval

# The interval class implements interval arithmetic
# We just extend it to create a range from which
# we can uniformly choose a random value
class RandRange(interval):

    # Choose a random value from this range
    def evaluate(self):
        return uniform(self.extrema[0][0], self.extrema[-1][0])

    def __str__(self):
        return f"rand({self.extrema[0][0]}, {self.extrema[-1][0]})"

    def __repr__(self):
        return str(self)

# As above but only generates integers
class RandIntRange(interval):

    def evaluate(self):
        return randint(self.extrema[0][0], self.extrema[-1][0])

    def __str__(self):
        return f"randint({self.extrema[0][0]}, {self.extrema[-1][0]})"

    def __repr__(self):
        return str(self)
