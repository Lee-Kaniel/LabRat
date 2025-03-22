from functools import cached_property

from LabRat.src.data_filters.base_data_filter import BaseDataFilter
from LabRat.src.schemas.contraction import Contraction
from LabRat.src.schemas.filter_flag import FilterFlag
from LabRat.src.schemas.overview import Overview
from LabRat.src.schemas.overview_table import OverviewTable
from LabRat.src.utils.inquirer import receive_integer, receive_boolean


class RelaxationTimeFilter(BaseDataFilter):
    MAX_RELAXATION_TIME = 1200

    def __init__(self, pre_filter_excel_file_name: str = None, post_filter_excel_file_name: str = None):
        super().__init__(
            pre_filter_excel_file_name=pre_filter_excel_file_name,
            post_filter_excel_file_name=post_filter_excel_file_name
        )
        self._hz_frequency = None

    @cached_property
    def relaxation_minimum_limit(self):
        return 200 / self._hz_frequency

    def filter_contraction(self, contraction: Contraction) -> bool:
        relaxation_time = contraction.relaxation_time
        if relaxation_time < self.relaxation_minimum_limit or relaxation_time > self.MAX_RELAXATION_TIME:
            return True
        return False

    def filter_overview(self, overview: Overview) -> Overview:
        for i in range(len(overview.contraction_list)):
            if overview.contraction_list[i].filter_flag != FilterFlag.DELETE:
                if self.filter_contraction(overview.contraction_list[i]):
                    overview.contraction_list[i].filter_flag = FilterFlag.DELETE
        return overview

    @staticmethod
    def _receive_hz_frequency() -> int:
        return receive_integer(message="Please enter the Hz frequency (must be a number)")

    def filter_overview_table(self, overview_table: OverviewTable) -> OverviewTable:
        print("=== Relaxation Time Filter Form ===")
        if hz_frequency := overview_table.hz_frequency:
            accept_inferred_hz_value = receive_boolean(
                message=f"The Hz value assumed for this filter is - {hz_frequency}. Do you want to continue with this "
                        f"value? "
            )
            self._hz_frequency = hz_frequency if accept_inferred_hz_value else self._receive_hz_frequency()
        else:
            self._hz_frequency = self._receive_hz_frequency()

        overview_table.overview_list = [self.filter_overview(overview) for overview in overview_table.overview_list]
        return overview_table

