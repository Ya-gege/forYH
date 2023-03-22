"""
Secret sharing scheme.
"""

from __future__ import annotations
import random
from typing import List


class Share:
    """
    A secret share in a finite field.
    """
    FIELD_Q = 3525679

    def __init__(self, val, *args, **kwargs):
        # Adapt constructor arguments as you wish
        self.val = val

    def __repr__(self):
        # Helps with debugging.
        raise NotImplementedError("You need to implement this method.")

    def __add__(self, other):
        if not isinstance(other, Share):
            raise TypeError("Only add for Share")
        return Share((self.val + other.val) % self.FIELD_Q)

    def __sub__(self, other):
        if not isinstance(other, Share):
            raise TypeError("Only sub for Share")
        return Share((self.val - other.val) % self.FIELD_Q)

    def __mul__(self, other):
        raise NotImplementedError("You need to implement this method.")

    def serialize(self):
        """Generate a representation suitable for passing in a message."""
        raise NotImplementedError("You need to implement this method.")

    @staticmethod
    def deserialize(serialized) -> Share:
        """Restore object from its serialized representation."""
        raise NotImplementedError("You need to implement this method.")


def share_secret(secret: int, num_shares: int) -> List[Share]:
    """Generate secret shares."""
    FIELD_Q = Share.FIELD_Q
    shares_values = random.sample(range(0, FIELD_Q), num_shares - 1)

    share_0 = secret - (sum(shares_values) % FIELD_Q)

    shares_values = [share_0] + shares_values

    return [Share(val) for val in shares_values]


def reconstruct_secret(shares: List[Share]) -> int:
    """Reconstruct the secret from shares."""
    return sum(shares, start=Share(0)).val


# Feel free to add as many methods as you want.
