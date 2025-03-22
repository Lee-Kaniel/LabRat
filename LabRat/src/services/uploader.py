import glob
import os

from LabRat.src.configuration import OVERVIEW_FILE_NAME
from LabRat.src.schemas.contraction import Contraction
from LabRat.src.schemas.overview import Overview
from LabRat.src.schemas.overview_table import OverviewTable
from LabRat.src.utils.read_from_file import read_fields_from_file
from LabRat.src.utils.safe_get import safe_get


class Uploader:
    """
        Class responsible for uploading raw data into the program from text files.
    """

    @staticmethod
    def _load_overview(file_path: str) -> Overview:
        folder_path = os.path.dirname(file_path)
        data = read_fields_from_file(file_path)
        folder_name = os.path.basename(folder_path)
        return Overview(
            group=folder_name,
            well=folder_name,
            contraction_list=[
                Contraction(
                    contraction_duration=safe_get(0, line),
                    time_to_peak=safe_get(1, line),
                    relaxation_time=safe_get(2, line),
                    ninety_to_ninety_transient=safe_get(3, line),
                    fifty_to_fifty_transient=safe_get(4, line),
                    ten_to_ten_transient=safe_get(5, line),
                    baseline_value=safe_get(6, line),
                    peak_amplitude=safe_get(7, line),
                    contraction_amplitude=safe_get(8, line),
                    peak_to_peak_time=safe_get(9, line)
                ) for line in data
            ])

    def load_overview_table(self, folder_path: str) -> OverviewTable:
        pattern = os.path.join(folder_path, '**', OVERVIEW_FILE_NAME)
        overview_file_paths = glob.glob(pattern, recursive=True)
        return OverviewTable(
            name=os.path.basename(folder_path),
            overview_list=[self._load_overview(file_path) for file_path in overview_file_paths]
        )
