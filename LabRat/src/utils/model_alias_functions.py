from pydantic import BaseModel
from typing import List

from pydantic.fields import FieldInfo
from typing_extensions import Type


def model_alias_count(model_class: Type[BaseModel]) -> int:
    """
        The function returns the number of fields with aliases a certain Pydantic class has.

        :param model_class: A class that inherits from Pydantic BaseModel
        :return: int
    """
    return sum(1 for field in model_class.__fields__.values() if field.alias)


def model_aliases(model_class: Type[BaseModel]) -> List[str]:
    """
        The function returns a list of all aliases a certain Pydantic class has.

        :param model_class: A class that inherits from Pydantic BaseModel
        :return: List of field alias names
    """
    return [field.alias for field in model_class.__fields__.values() if field.alias is not None]


def get_fields_with_aliases(model_class: Type[BaseModel]) -> List[str]:
    """
        The function returns a list of all fields with aliases a certain Pydantic class has.

        :param model_class: A class that inherits from Pydantic BaseModel
        :return: List of field names
    """
    return [field_name for field_name, field_info in model_class.__fields__.items() if field_info.alias]


def get_fields_without_aliases(model_class: Type[BaseModel]) -> List[str]:
    """
        The function returns a list of all fields without aliases a certain Pydantic class has.

        :param model_class: A class that inherits from Pydantic BaseModel
        :return: List of field names
    """
    return [field_name for field_name, field_info in model_class.__fields__.items() if not field_info.alias]
