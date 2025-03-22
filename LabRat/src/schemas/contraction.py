from typing import Optional, Dict, Any

from pydantic import BaseModel, Field

from LabRat.src.schemas.filter_flag import FilterFlag


class Contraction(BaseModel):
    contraction_duration: int = Field(..., alias='Contraction duration [10% above baseline] (ms)')
    time_to_peak: int = Field(..., alias='Time to peak (ms)')
    relaxation_time: int = Field(..., alias='Relaxation time (ms)')
    ninety_to_ninety_transient: int = Field(..., alias='90 to 90 transient (ms)')
    fifty_to_fifty_transient: int = Field(..., alias='50 to 50 transient')
    ten_to_ten_transient: int = Field(..., alias='10 to 10 transient')
    baseline_value: float = Field(..., alias='Baseline value')
    peak_amplitude: float = Field(..., alias='Peak amplitude')
    contraction_amplitude: float = Field(..., alias='Contraction amplitude')
    peak_to_peak_time: Optional[int] = Field(..., alias='Peak to peak time')
    filter_flag: Optional[FilterFlag] = Field(default=None)
    fields_for_update: Dict[str, Any] = Field(default={})

    class Config:
        populate_by_name = True
