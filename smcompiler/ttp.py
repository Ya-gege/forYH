"""
Trusted parameters generator.

MODIFY THIS FILE.
"""

from typing import (
    Set,
    Tuple,
)

from secret_sharing import (
    Share,
)


# Feel free to add as many imports as you want.


class TrustedParamGenerator:
    """
    A trusted third party that generates random values for the Beaver triplet multiplication scheme.
    """

    def __init__(self):
        self.participant_ids: Set[str] = set()


    def add_participant(self, participant_id: str) -> None:
        """
        Add a participant.
        """
        self.participant_ids.add(participant_id)

    def retrieve_share(self, client_id: str, op_id: str) -> Tuple[Share, Share, Share]:
        """
        Retrieve a triplet of shares for a given client_id.
        """
        raise NotImplementedError("You need to implement this method.")

    # Feel free to add as many methods as you want.
