#!/usr/bin/env python

import random


class Rando(object):
    def __init__(self, weights, rng=random.random):
        """Initialize the Rando class.

        :param weights: A sequence of (Item, Weight) tuples. Items of equal weight are
            selected in ascending order.
        :type weights: Sequence[Tuple[Any, Union[int, float]]]
        :param rng: A callable that takes zero arguments and returns a float between 0
            (inclusive) and 1 (exclusive). The default uses the Python Standard Library
            generator. If the generator needs a seed, it should be set prior to
            invoking this object.
        :type rng: Callable[[], float]
        """
        self.rng = rng

        # convert the sequence into a list
        # in case a generator or other singlely enumerable item is provided
        weights = list(weights)
        total_weight = sum(float(w) for (_, w) in weights)

        self.weights = [
            (item, float(weight) / total_weight) for (item, weight) in weights
        ]

    def __repr__(self):
        rng = self.rng
        if self.rng is random.random:
            rng = "random.random"
        else:
            rng = repr(rng)

        return "Rando({!r}, {})".format(self.weights, rng)

    def __iter__(self):
        return self

    def __next__(self):
        rng = self.rng()
        for item, weight in self.weights:
            rng -= weight
            if rng < 0:
                return item

        raise RuntimeError("rng value greater than the sum of all weights")

    # py2 compatibility
    next = __next__
