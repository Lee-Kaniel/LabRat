import os
import inquirer

from LabRat.src.configuration import OVERVIEW_FILE_NAME, OVERVIEW_FORMULAS
from LabRat.src.data_filters.amplitude_filter import AmplitudeFilter
from LabRat.src.data_filters.contraction_outlier_filter import ContractionOutlierFilter
from LabRat.src.data_filters.overview_outlier_filter import OverviewOutlierFilter
from LabRat.src.data_filters.relaxation_time_filter import RelaxationTimeFilter

from LabRat.src.data_filters.simple_filter import SimpleFilter
from LabRat.src.schemas.overview_table import OverviewTable
from LabRat.src.services.downloader import Downloader
from LabRat.src.services.filter import Filter
from LabRat.src.services.uploader import Uploader

BOLD = '\033[1m'
RESET = '\033[0m'
DARK_YELLOW = '\033[38;5;94m'
RED = '\033[91m'


def print_help() -> None:
    """
    Prints a comprehensive help menu that explains:
    - The usage of the application
    - Expected file structure
    - Outputs generated
    - Customization options for filters and formulas
    """
    print(BOLD + DARK_YELLOW + "----------------------------------------------" + RESET)
    print(BOLD + DARK_YELLOW + "--- LabRat Usage" + RESET)
    print(f"The 'Run LabRat' option will prompt the user for a folder path.")
    print(f"The application will then process all '{OVERVIEW_FILE_NAME}' files that are located under the folder "
          f"path provided, and will create the relevant \nExcel files.")
    print("The folder path should correspond to the name of the output Excel file")
    print(BOLD + DARK_YELLOW + "\n--- File Layout" + RESET)
    print(f"""
       Folder Path (Excel File Name)
       │
       ├── Well_1 (Well Folder)
       │   └── {OVERVIEW_FILE_NAME}
       │
       ├── Well_2
       │   └── {OVERVIEW_FILE_NAME}
       │
       └── Well_3
           └── {OVERVIEW_FILE_NAME}

       Each Well folder should abide to this naming rule: After the Word 'Well' there should be a white space, then
       the well name, another whitespace, and then the group name. 
       For example: '1Week MTs Cochr Plate B spont 04052024 Well B1 MM current001-Contr-Results' - Corresponds to Well 
       B1 and Group MM
       """)
    print(BOLD + DARK_YELLOW + "\n--- Output" + RESET)
    print("The application will create two Excel files in the folder path provided:")
    print("1) <folder_path>.xlsx will visualize the original data, and highlight in red the data points that are "
          "marked for deletion, \n and in yellow data points that are marked for update.\nIMPORTANT: This Excel file "
          "will not alter the data - but only highlights the suggested changes upon the original data")
    print("2) <folder_path>_filtered.xlsx will only contain the unfiltered data points from the previous Excel file "
          "suggestions.\n")
    print(BOLD + DARK_YELLOW + "--- Configuration" + RESET)
    print("The user can configure the following aspects in the LabRat application:")
    print("1. Configure Data Filters - data filters that come out of the box are stored in the 'data_filters' folder "
          "in src.\nTo configure these data filters navigate to there code, and change their global variables. These "
          "variables are stored at the top of the class, and are in all upper-case.")
    print("To chose what data filters run and in what order - navigate to the 'filter_data' function in main.py")
    print("2. Add Data Filters - to add a data filter, create a class that inherits from BaseDataFilter (in the "
          "data_filters directory in src). Then - add this filter to the 'filter_data' function in main.py")
    print("3. The OVERVIEW_FORMULAS - in the configuration file the user can add Excel formals he would like to "
          f"appear for each overview in the Excel file. Currently, the following formals are set: {OVERVIEW_FORMULAS}")
    print("4. The OVERVIEW_FILE_NAME - in the configuration file the user can change the text file name the application"
          f" will look for. Currently, the application looks for {OVERVIEW_FILE_NAME}.")
    print(BOLD + DARK_YELLOW + "----------------------------------------------\n" + RESET)


def upload_data(root_directory: str) -> OverviewTable:
    """
        The function uploads the data from the Muscle Motion output
    """
    uploader = Uploader()
    data = uploader.load_overview_table(folder_path=root_directory)
    return data


def filter_data(data: OverviewTable, root_directory: str) -> OverviewTable:
    """
        The function specifies what filters to run on the uploaded data, and in what order
    """
    filters = Filter()
    filters.add_filter(AmplitudeFilter())
    filters.add_filter(SimpleFilter(post_filter_excel_file_name="noise_filter"))
    filters.add_filter(RelaxationTimeFilter())
    filters.add_filter(ContractionOutlierFilter())
    filters.add_filter(OverviewOutlierFilter())
    return filters.filter_overview_table(overview_table=data, root_directory=root_directory)


def download_data(data: OverviewTable, root_directory: str) -> None:
    """
        The function downloads the processed data into Excel Files
    """
    downloader = Downloader()
    downloader.write_to_excel(data=data, folder_path=root_directory, show_filtered=True)
    downloader.write_to_excel(data=data, folder_path=root_directory, show_filtered=False)


def run_application() -> None:
    # Prompt the user for a path
    path_question = inquirer.Text('path', message="Enter the folder path")
    root_directory = inquirer.prompt([path_question])['path']

    # Check if the path exists and is directory
    if not os.path.exists(root_directory):
        print(RED + f"Folder {root_directory} does not exist.\n" + RESET)
        return
    if not os.path.isdir(root_directory):
        print(RED + f"File {root_directory} is not a folder.\n" + RESET)
        return

    data = upload_data(root_directory=root_directory)
    processed_data = filter_data(data=data, root_directory=root_directory)
    download_data(data=processed_data, root_directory=root_directory)
    print(BOLD + "Finished!\n" + RESET)


def main() -> None:
    """
        Main function to be executed.
    """
    print(BOLD + "Welcome to the LabRat Command Line Application!" + RESET)
    # Define the application options
    options = [
        inquirer.List('option',
                      message=f"{DARK_YELLOW}Select an option{RESET}",
                      choices=[
                          ('Print Help', print_help),
                          ('Run LabRat', run_application),
                          ('Quit', None)
                      ],
                      default='Run LabRat'
                      )
    ]

    while True:
        # Prompt the user to select an option
        answers = inquirer.prompt(options)

        # Get the selected option
        selected_option = answers['option']

        if selected_option:
            selected_option()
        else:
            print(DARK_YELLOW + "Bye!" + RESET)
            return


if __name__ == '__main__':
    main()
