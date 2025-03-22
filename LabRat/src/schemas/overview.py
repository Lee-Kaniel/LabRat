import re

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

from LabRat.src.schemas.contraction import Contraction
from LabRat.src.schemas.filter_flag import FilterFlag


class Overview(BaseModel):
    group: str = Field(default=None, alias='Group')
    well: str = Field(..., alias='Well')
    average_std: float = Field(default=None, alias='avg/std')
    contraction_list: List[Contraction] = Field(default=[])
    filter_flag: Optional[FilterFlag] = Field(default=None)

    @field_validator('well')
    def extract_well_name_from_folder_name(cls, value):
        pattern = r'Well\s+(\w+)'
        match = re.search(pattern, value)
        if match:
            return match.group(1)
        return value

    @field_validator('group')
    def extract_group_name_from_folder_name(cls, value):
        pattern = r'\bWell\b \w+ (\w+)'
        match = re.search(pattern, value)
        if match:
            return match.group(1)
        return value

    class Config:
        populate_by_name = True


def sort_key(model: Overview):
    # Split the "well" attribute into letters and numbers
    letters = ''.join(filter(str.isalpha, model.well))
    numbers = int(''.join(filter(str.isdigit, model.well)))
    return letters, numbers
