import warnings
from typing import List

from LabRat.src.data_filters.base_data_filter import BaseDataFilter
from LabRat.src.schemas.contraction import Contraction
from LabRat.src.schemas.filter_flag import FilterFlag
from LabRat.src.schemas.overview import Overview
from LabRat.src.schemas.overview_table import OverviewTable
from LabRat.src.services.downloader import Downloader


class Filter:
    """
        Class responsible for filtering the processed data.
    """

    def __init__(self, filter_list: List[BaseDataFilter] = None) -> None:
        self.filter_list = filter_list if filter_list else []
        self._downloader = Downloader()

    @staticmethod
    def commit_changes_to_data(overview_table: OverviewTable) -> None:
        warnings.filterwarnings("ignore", category=UserWarning)
        updated_overview_list: List[Overview] = []
        for overview in overview_table.overview_list:
            if overview.filter_flag != FilterFlag.DELETE:

                updated_contraction_list: List[Contraction] = []
                for contraction in overview.contraction_list:
                    if contraction.filter_flag != FilterFlag.DELETE:
                        updated_contraction = contraction.model_copy(update=contraction.fields_for_update)
                        updated_contraction.filter_flag = None
                        updated_contraction_list.append(updated_contraction)
                overview.contraction_list = updated_contraction_list

                updated_overview_list.append(overview)
        overview_table.overview_list = updated_overview_list

    def _write_intermediate_excel_file(
            self, overview_table: OverviewTable, root_directory: str, excel_file_name: str
    ) -> None:
        self._downloader.write_to_excel(
            data=overview_table, folder_path=root_directory, show_filtered=True,
            excel_file_name=f"{excel_file_name}.xlsx"
        )
        self._downloader.write_to_excel(
            data=overview_table, folder_path=root_directory, show_filtered=False,
            excel_file_name=f"{excel_file_name}_filtered.xlsx"
        )
        self.commit_changes_to_data(overview_table)

    def add_filter(self, data_filter: BaseDataFilter) -> None:
        self.filter_list.append(data_filter)

    def filter_overview_table(self, overview_table: OverviewTable, root_directory: str) -> OverviewTable:
        for data_filter in self.filter_list:
            # Create pre-filter excel file if data_filter.pre_filter_excel_file_name is set
            if pre_filter_excel_name := data_filter.pre_filter_excel_file_name:
                self._write_intermediate_excel_file(
                    overview_table=overview_table, root_directory=root_directory, excel_file_name=pre_filter_excel_name
                )

            # Filter overview_table by specific data filter
            overview_table = data_filter.filter_overview_table(overview_table=overview_table)

            # Create post-filter excel file if data_filter.post_filter_excel_file_name is set
            if post_filter_excel_name := data_filter.post_filter_excel_file_name:
                self._write_intermediate_excel_file(
                    overview_table=overview_table, root_directory=root_directory, excel_file_name=post_filter_excel_name
                )

        return overview_table
