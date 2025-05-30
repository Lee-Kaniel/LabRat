from collections import defaultdict
from typing import Optional, List

import numpy as np

from LabRat.src.data_filters.base_data_filter import BaseDataFilter
from LabRat.src.schemas.filter_flag import FilterFlag
from LabRat.src.schemas.overview import Overview
from LabRat.src.schemas.overview_table import OverviewTable
from LabRat.src.utils.safe_get import get_field_or_updated


class OverviewOutlierFilter(BaseDataFilter):
    """
    This filter detects and removes entire overviews (wells) whose *average values* for selected fields
    are outliers compared to the distribution of values in other overviews within the same group.
    """
    @staticmethod
    def _get_average_overview_field(field_name: str, overview: Overview) -> Optional[float]:
        """
        Computes the average of a specific field across all non-deleted contractions in a given overview.
        If no valid numeric values are found, the overview is marked for deletion.
        """
        overview_field_values = []
        for contraction in overview.contraction_list:
            if contraction.filter_flag != FilterFlag.DELETE:
                contraction_field_value = get_field_or_updated(contraction, field_name, 0)
                if not isinstance(contraction_field_value, str): # Ignore marked outliers
                    overview_field_values.append(contraction_field_value)
        if not overview_field_values:
            overview.filter_flag = FilterFlag.DELETE
            return
        return np.mean(overview_field_values)

    def _set_overview_outliers(self, field_name: str, overview_list: List[Overview]) -> None:
        """
        Identifies and deletes outlier overviews based on interquartile range (IQR) of the averages for a given field.
        """
        overview_field_averages = []
        for overview in overview_list:
            overview_field_average = self._get_average_overview_field(field_name=field_name, overview=overview)
            if overview_field_average:
                overview_field_averages.append(overview_field_average)

        if not overview_field_averages:
            return

        data = np.array(overview_field_averages)

        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1

        # Flag overviews as outliers if their average falls outside [Q1 - 1.5*IQR, Q3 + 1.5*IQR]
        for overview in overview_list:
            if overview.filter_flag == FilterFlag.DELETE:
                continue
            overview_field_average = self._get_average_overview_field(field_name=field_name, overview=overview)
            if overview_field_average > 1.5 * iqr + q3 or overview_field_average < q1 - 1.5 * iqr:
                overview.filter_flag = FilterFlag.DELETE

    def filter_overview(self, overview: Overview) -> Overview:
        pass

    def _filter_overview_table_by_group(self, field_name: str, overview_table: OverviewTable) -> None:
        """
        Applies outlier filtering separately to each group of overviews.
        """
        sort_by_group = defaultdict(list)
        for overview in overview_table.overview_list:
            if overview.filter_flag != FilterFlag.DELETE:
                sort_by_group[overview.group].append(overview)

        for _, overview_group in sort_by_group.items():
            self._set_overview_outliers(field_name=field_name, overview_list=overview_group)

    def filter_overview_table(self, overview_table: OverviewTable) -> OverviewTable:
        """
        Iterates through relevant fields and applies outlier filtering within each group of overviews.
        """
        for field_name in ["contraction_duration", "contraction_amplitude", "time_to_peak"]:
            self._filter_overview_table_by_group(field_name=field_name, overview_table=overview_table)
        return overview_table
