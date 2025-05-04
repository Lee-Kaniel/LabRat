from functools import cached_property

from LabRat.src.data_filters.base_data_filter import BaseDataFilter
from LabRat.src.schemas.contraction import Contraction
from LabRat.src.schemas.filter_flag import FilterFlag
from LabRat.src.schemas.overview import Overview
from LabRat.src.schemas.overview_table import OverviewTable
from LabRat.src.utils.inquirer import receive_integer, receive_boolean


class RelaxationTimeFilter(BaseDataFilter):
    """
    A filter that removes contractions whose relaxation time falls outside acceptable physiological bounds.
    The lower bound depends on the pacing frequency (Hz), while the upper bound is fixed.
    """
    MAX_RELAXATION_TIME = 1200 # Fixed upper limit for relaxation time (in ms)

    def __init__(self, pre_filter_excel_file_name: str = None, post_filter_excel_file_name: str = None):
        super().__init__(
            pre_filter_excel_file_name=pre_filter_excel_file_name,
            post_filter_excel_file_name=post_filter_excel_file_name
        )
        self._hz_frequency = None

    @cached_property
    def relaxation_minimum_limit(self):
        """
        Calculates the minimum acceptable relaxation time based on pacing frequency
        """
        return 200 / self._hz_frequency

    def filter_contraction(self, contraction: Contraction) -> bool:
        """
        Determines whether a contraction should be deleted based on its relaxation time.
        Returns True if outside [min, max] range.
        """
        relaxation_time = contraction.relaxation_time
        if relaxation_time < self.relaxation_minimum_limit or relaxation_time > self.MAX_RELAXATION_TIME:
            return True
        return False

    def filter_overview(self, overview: Overview) -> Overview:
        """
        Applies the relaxation time filter to all contractions in the overview.
        """
        for i in range(len(overview.contraction_list)):
            if overview.contraction_list[i].filter_flag != FilterFlag.DELETE:
                if self.filter_contraction(overview.contraction_list[i]):
                    overview.contraction_list[i].filter_flag = FilterFlag.DELETE
        return overview

    @staticmethod
    def _receive_hz_frequency() -> int:
        """
        Prompts the user to manually enter a Hz value via CLI.
        """
        return receive_integer(message="Please enter the Hz frequency (must be a number)")

    def filter_overview_table(self, overview_table: OverviewTable) -> OverviewTable:
        """
        Applies the filter to the entire overview table.
        Prompts the user for Hz frequency if not provided in the metadata, or confirms if provided.
        """
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

