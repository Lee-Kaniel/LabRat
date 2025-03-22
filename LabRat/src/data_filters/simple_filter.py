from LabRat.src.data_filters.base_data_filter import BaseDataFilter
from LabRat.src.schemas.contraction import Contraction
from LabRat.src.schemas.filter_flag import FilterFlag
from LabRat.src.schemas.overview import Overview
from LabRat.src.utils.model_alias_functions import get_fields_without_aliases


class SimpleFilter(BaseDataFilter):
    @staticmethod
    def filter_contraction(contraction: Contraction) -> bool:
        if any(x == 0 for x in
               contraction.dict(exclude=get_fields_without_aliases(Contraction)+["peak_to_peak_time"]).values()):
            return True
        return False

    def filter_overview(self, overview: Overview) -> Overview:
        for i in range(len(overview.contraction_list)):
            if overview.contraction_list[i].filter_flag != FilterFlag.DELETE:
                if self.filter_contraction(overview.contraction_list[i]):
                    overview.contraction_list[i].filter_flag = FilterFlag.DELETE
        return overview
