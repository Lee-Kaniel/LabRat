from enum import Enum

from openpyxl.styles import PatternFill


class FilterFlag(Enum):
    DELETE = PatternFill(start_color="ff7e75", end_color="FF0000", fill_type="solid")
    UPDATE = PatternFill(start_color="FFFFCC", end_color="FFFFCC", fill_type="solid")
