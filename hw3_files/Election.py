from dataclasses import dataclass
from typing import List

@dataclass
class Election:
    election_id: int
    parties: list
    votes_per_party: dict
    total_votes: int
    surplus_pairs: List[tuple[any, any]]
    electoral_threshold: float