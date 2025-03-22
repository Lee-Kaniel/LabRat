import re

from pydantic import BaseModel, field_validator
from typing import List, Optional

from LabRat.src.schemas.overview import Overview


class OverviewTable(BaseModel):
    name: str
    overview_list: List[Overview]

    @property
    def hz_frequency(self):
        # Regex to capture the third word
        match = re.search(r'\b\w+\b\s+\b\w+\b\s+\b(\w+)\b', self.name)

        if not match:
            return None  # If there are fewer than 3 words, return None

        third_word = match.group(1)

        # Special case for "stone"
        if third_word.lower() == "spont":
            return 1

        # Regex to find the number before "Hz" in the third word
        hz_match = re.search(r'(\d+)Hz', third_word)
        if hz_match:
            try:
                return int(hz_match.group(1))
            except ValueError:
                pass

        return None
