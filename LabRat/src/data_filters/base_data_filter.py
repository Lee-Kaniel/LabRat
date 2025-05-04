from abc import ABC, abstractmethod

from LabRat.src.schemas.overview import Overview
from LabRat.src.schemas.overview_table import OverviewTable


class BaseDataFilter(ABC):
    """
    Abstract base class for all data filters. Defines the required interface for any filter class
    that processes contraction data (e.g., amplitude-based or rhythm-based filters).
    """
    def __init__(self, pre_filter_excel_file_name: str = None, post_filter_excel_file_name: str = None):
        self.pre_filter_excel_file_name = pre_filter_excel_file_name
        self.post_filter_excel_file_name = post_filter_excel_file_name

    @abstractmethod
    def filter_overview(self, overview: Overview) -> Overview:
        """
            The function receives an Overview and returns a filtered instance of the Overview
        """
        raise NotImplementedError

    def filter_overview_table(self, overview_table: OverviewTable) -> OverviewTable:
        """
            The function receives an OverviewTable and filters its overview_list values using the class filter_overview
            function. The function returns the updated OverviewTable object.
        """
        overview_table.overview_list = [self.filter_overview(overview) for overview in overview_table.overview_list]
        return overview_table
