import numpy
from typing import List, Union

from LabRat.src.data_filters.base_data_filter import BaseDataFilter
from LabRat.src.schemas.filter_flag import FilterFlag

from LabRat.src.schemas.overview import Overview
from LabRat.src.utils.safe_get import get_field_or_updated


class AmplitudeFilter(BaseDataFilter):
    STD_FROM_AMPLITUDE = 2 # Min amplitude must be within 2 SDs of the mean
    PARTIAL_AMPLITUDE = 0.25 # Min amplitude must be ≥ 25% of max amplitude
    STD_FROM_PEAK_TO_PEAK = 0.25  # Threshold to consider deviation in timing as noise

    @staticmethod
    def find_closest_real_peak_to_peak(
            index: int, absolute_peak_to_peak_list: List[int], real_peak_to_peak_list: List[int],
            above: bool = True
    ) -> Union[int, None]:
        """
            A function to find the closest real peak to peak from a certain index in a dictionary.
        """
        list_range = range(index + 1, len(absolute_peak_to_peak_list)) if above else range(index - 1, -1, -1)
        for i in list_range:
            absolute_peak_to_peak = absolute_peak_to_peak_list[i]
            if absolute_peak_to_peak in real_peak_to_peak_list:
                return absolute_peak_to_peak
        return None

    def adjust_overview_by_noise(self, overview: Overview) -> Overview:
        """
        updates the peak to peak times after taking into account the peaks deleted for being noise errors
        if a peak was deleted the time to peak of the following peak is updated to the corrected value
        """
        absolute_peak_to_peak_list = []
        real_peak_to_peak_list = []
        backlog_peak_to_peak_time = 0
        
        # Construct cumulative timing lists for all contractions
        for i in range(len(overview.contraction_list)):
            peak_to_peak = get_field_or_updated(overview.contraction_list[i], "peak_to_peak_time", 0)
            absolute_peak_time = peak_to_peak + backlog_peak_to_peak_time
            absolute_peak_to_peak_list.append(absolute_peak_time)
            backlog_peak_to_peak_time += peak_to_peak
            if overview.contraction_list[i].filter_flag != FilterFlag.DELETE:
                real_peak_to_peak_list.append(absolute_peak_time)

        # If there aren't enough real contractions to define, return unchanged
        if len(real_peak_to_peak_list) < 2 or not absolute_peak_to_peak_list:
            return overview

        # Compute median and standard deviation of timing differences between real contractions
        differences_real_peak_to_peak_list = []
        for i in range(len(real_peak_to_peak_list) - 1):
            difference = real_peak_to_peak_list[i + 1] - real_peak_to_peak_list[i]
            differences_real_peak_to_peak_list.append(difference)

        median_peak_to_peak = numpy.median(differences_real_peak_to_peak_list)
        std_peak_to_peak = numpy.std(differences_real_peak_to_peak_list)

        # checks if the deleted peak is a noise error or a different type of error through peak to peak time misalignment
        for i in range(len(overview.contraction_list)):
            if overview.contraction_list[i].filter_flag == FilterFlag.DELETE:
                update_flag = False
                for condition in (True, False): # Try both forward and backward search
                    if closest_peak := self.find_closest_real_peak_to_peak(
                            index=i, absolute_peak_to_peak_list=absolute_peak_to_peak_list,
                            real_peak_to_peak_list=real_peak_to_peak_list, above=condition
                    ):
                        if abs(closest_peak - absolute_peak_to_peak_list[i]) < median_peak_to_peak - \
                                std_peak_to_peak * self.STD_FROM_PEAK_TO_PEAK:
                            update_flag = True
                            break
                if update_flag:
                    try:
                        # Updates the timing of the *next* contraction if deleted peak was found to be a noise error
                        peak_to_peak = get_field_or_updated(
                            overview.contraction_list[i], "peak_to_peak_time", 0
                        )
                        next_peak_to_peak = get_field_or_updated(
                            overview.contraction_list[i + 1], "peak_to_peak_time", 0
                        )
                        overview.contraction_list[i + 1].fields_for_update["peak_to_peak_time"] = \
                            peak_to_peak + next_peak_to_peak
                        if overview.contraction_list[i + 1].filter_flag != FilterFlag.DELETE:
                            overview.contraction_list[i + 1].filter_flag = FilterFlag.UPDATE
                    except IndexError:
                        pass
        return overview

    def filter_overview_by_contraction_amplitude(self, overview: Overview) -> Overview:
        """
        Flags contractions for deletion if their amplitude is too low:
        - Either < (mean - 2*SD)
        - Or < 25% of the maximum contraction amplitude.
        """
        amplitude_length_list = [contraction.contraction_amplitude for contraction in overview.contraction_list]

        if not amplitude_length_list:
            return overview

        average_length = numpy.average(amplitude_length_list)
        std_length = numpy.std(amplitude_length_list)
        max_length = max(amplitude_length_list)

        # Filter contractions
        for i in range(len(overview.contraction_list)):
            contraction_length = overview.contraction_list[i].contraction_amplitude
            if contraction_length < average_length - self.STD_FROM_AMPLITUDE * std_length or \
                    contraction_length < self.PARTIAL_AMPLITUDE * max_length:
                overview.contraction_list[i].filter_flag = FilterFlag.DELETE

        return overview

    def filter_overview(self, overview: Overview) -> Overview:
        """
        Main entry point:
        - Filters by amplitude first.
        - Then checks peak to peak time misalignment. if found the error was noise error.
        - If noise error time to peak of next peak is updated
        """
        try:
            amplitude_filtered_overview = self.filter_overview_by_contraction_amplitude(overview=overview)
            return self.adjust_overview_by_noise(amplitude_filtered_overview)
        except Exception as e:
            print(f"Amplitide Filter Exception in well {overview.well}: {e}")
            return overview

