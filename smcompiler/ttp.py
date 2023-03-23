"""
Trusted parameters generator.

MODIFY THIS FILE.
"""
import math
import random
from typing import (
    Set,
    Tuple,
)

from secret_sharing import (
    Share, share_secret,
)


# Feel free to add as many imports as you want.


def get_share(triplet: Tuple, idx: int) -> Tuple:
    return triplet[0][idx], triplet[1][idx], triplet[2][idx]


class TrustedParamGenerator:
    """
    A trusted third party that generates random values for the Beaver triplet multiplication scheme.
    """

    def __init__(self):
        self.participant_ids: Set[str] = set()
        # k: Bob  v: 1
        self.participant_dict = dict()
        # k: op_id  v: tuple
        self.triplet_dict = dict()

    def add_participant(self, participant_id: str) -> None:
        """
        Add a participant.
        """
        self.participant_ids.add(participant_id)
        idx = len(self.participant_dict)
        self.participant_dict[participant_id] = idx

    def retrieve_share(self, client_id: str, op_id: str) -> Tuple[Share, Share, Share]:
        """
        Retrieve a triplet of shares for a given client_id.
        see pdf-1.6 and ppt
        """
        idx = self.participant_dict[client_id]
        if op_id in self.triplet_dict:
            return get_share(self.triplet_dict[op_id], idx)

        # fresh Beaver Triplet(a, b, c)
        # 生成a, b, c 其中 a * b = c
        a, b = random.sample(range(0, int(math.floor(math.sqrt(Share.F_P)))), 2)
        # a, b = random.sample(range(0, Share.F_P), 2)
        c = a * b
        a_share = share_secret(a, len(self.participant_ids))
        b_share = share_secret(b, len(self.participant_ids))
        c_share = share_secret(c, len(self.participant_ids))

        triplet = (a_share, b_share, c_share)
        # 保存该expr.id对应的三元组
        self.triplet_dict[op_id] = triplet
        return get_share(triplet, idx)

    # Feel free to add as many methods as you want.

