from typing import List, Optional, Any

from pydantic import BaseModel


def safe_get(index: int, lst: List) -> Optional[Any]:
    """
        Returns the specified index in the list, or None if it does not exist.
    """
    try:
        return lst[index]
    except IndexError:
        return None


def get_field_or_updated(model: BaseModel, field_name: str, default_value: Any = None) -> Any:
    if updated_value := model.fields_for_update.get(field_name):
        return updated_value
    if model_value := model.__getattribute__(field_name):
        return model_value
    return default_value
