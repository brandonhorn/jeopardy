from dataclasses import dataclass


@dataclass
class Clue:
    Id: int
    Category: str
    Question: str
    Value: int
    Answer: str