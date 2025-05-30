import numpy as np

from LabRat.src.data_filters.base_data_filter import BaseDataFilter
from LabRat.src.schemas.contraction import Contraction
from LabRat.src.schemas.filter_flag import FilterFlag
from LabRat.src.schemas.overview import Overview
from LabRat.src.utils.model_alias_functions import get_fields_with_aliases
from LabRat.src.utils.safe_get import get_field_or_updated


class ContractionOutlierFilter(BaseDataFilter):
    """
    This filter identifies outliers in contraction data fields and marks them either for deletion
    or replacement with a placeholder ("Outlier") depending on the field.
    """
    @staticmethod
    def _field_outlier_action(field_name: str, contraction: Contraction) -> None:
        """
        Determines the action to take for a given outlier field:
        - Deletes the contraction if it's a critical feature (amplitude, duration, time to peak)
        - Otherwise, flags the specific field as "Outlier" (e.g., for timing metrics)
        """
        if field_name in ["contraction_duration", "contraction_amplitude", "time_to_peak"]:
            contraction.fields_for_update["filter_flag"] = FilterFlag.DELETE
        else:
            contraction.fields_for_update[field_name] = "Outlier"
            # Because this filter updates integer fields to string, the placement of this filter is crucial!
            # No filter after it should use the updated_fields without checking for this case.

    def _set_contraction_field_outliers(self, field_name: str, overview: Overview) -> None:
        """
        Applies IQR-based outlier detection for a given field across all contractions in the overview.
        Outliers are flagged using _field_outlier_action.
        """
        data = [
            get_field_or_updated(contraction, field_name, 0) for contraction in overview.contraction_list
            if contraction.filter_flag != FilterFlag.DELETE
        ]
        if not data:
            return

        data = np.array(data)

        # Calculate interquartile range (IQR) for detecting outliers
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1

        for contraction in overview.contraction_list:
            if contraction.filter_flag == FilterFlag.DELETE:
                continue # Skip contractions already marked for deletion

            contraction_field_value = get_field_or_updated(contraction, field_name, 0)
            # Check for outlier based on 1.5*IQR rule
            if contraction_field_value > 1.5 * iqr + q3 or contraction_field_value < q1 - 1.5 * iqr:
                self._field_outlier_action(field_name=field_name, contraction=contraction)

    def filter_overview(self, overview: Overview) -> Overview:
        """
        Main entry point for filtering. Applies outlier detection across all contraction fields
        using get_fields_with_aliases (retrieves all defined contraction attributes).
        """
        for field_name in get_fields_with_aliases(Contraction):
            self._set_contraction_field_outliers(field_name=field_name, overview=overview)

        overview.contraction_list = [
            contraction.model_copy(
                update={k: v for k, v in contraction.fields_for_update.items() if k == "filter_flag"})
            for contraction in overview.contraction_list
        ]
        return overview
