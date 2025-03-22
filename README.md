
# LabRat Data Analysis

LabRat is a custom filtering tool designed for processing and analyzing muscle motion data. The tool uses Python scripts to filter raw data, process it, and output results in Excel format. This README will guide you through the process of running the code, understanding its structure, and using its features.

## 🚀 How to Run the Code

### Requirements:
- Python >= 3.8
- Package installer (e.g., pip) to install dependencies

### **Important Note**:
Before running the code, ensure that the data is formatted according to the correct structure. The **"Overview Results"** file must be organized into columns in the following order:
1. Contraction duration [10% above baseline] (ms)
2. Time to peak (ms)
3. Relaxation time (ms)
4. 90 to 90 transient (ms)
5. 50 to 50 transient (ms)
6. 10 to 10 transient (ms)
7. Baseline value
8. Peak amplitude
9. Contraction amplitude
10. Peak to peak time

This is the default format exported by Muscle Motion when the relevant transient options are selected. If your data includes additional columns or has a different structure, you must reformat it to match this layout before running the code. 
Additionally, ensure that your file names are organized correctly as explained below.

### Running via Terminal

1. **Navigate to the LabRat directory:**
    - Use the terminal and navigate to the outer `LabRat` folder.

2. **Run the appropriate script:**
    - **For Mac:**  
      ```bash
      ./run_labrat_mac.sh
      ```
    - **For Windows:**  
      ```bash
      run_labrat_windows.bat
      ```

Alternatively, if you prefer running without the helper scripts:

1. Open terminal/cmd.
2. Navigate to the `LabRat` directory.
3. Run the following commands (for Linux):
    ```bash
    export PYTHONPATH="$PYTHONPATH:LabRat/src"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r LabRat/requirements.txt
    python LabRat/src/main.py
    ```

### Running via IDE (PyCharm)

1. **Download PyCharm.**
2. **Open the `LabRat` folder** as the working directory.
3. **Set up the run configuration**:
    - Make sure the working directory is set to the outer `LabRat` folder.
    - In the run configuration, set the script path to the location of `main.py`.
    - Enable the “Emulate terminal in output console” option.
4. **Install dependencies**:  
   When you first open the requirements file in PyCharm, it will prompt you to download the necessary libraries.

## 📝 Code Structure

### Main Code

Before running the code make sure your file names are organized correct and in the correct format. 
There should be a main folder, with a name that corresponds to the name of the output excel file.
In the main folder there needs to be subfolders for each well. 
In each well folder there needs to be an overview file. 
The overview file name can be updated in the configuration.py if needed, the default is “Overview-results.txt”.


The `main.py` file is the core of the program. Running this script will give you a choice of actions, including:
- Print help
- Run LabRat
- Quit

You will need to:
1. Select **Run LabRat**. (Use the up and down arrows to pick the option run labrat and then press enter)
2. Provide the folder path (not the folder name, but its location).
3. Confirm the frequency. If you are running the frequency the code presents you with enter y. If you are running on a different frequency enter n.
4. The output will generate four Excel files:
    1. Data with deleted contractions in red and edited contractions in yellow (noise filters).
    2. Final data after noise filtering.
    3. Data with deleted contractions in red (physiological filters).
    4. Final data after all filtering steps (Outliers will be flagged as “outlier” in specific boxes).

To run the code on an addition folder simply pick the run labrat option again. 
When you want to exit the code pick the quit option.


### Services Folder

- **Uploader:** Uploads raw data from text files into the program.
- **Filter:** Responsible for applying filtering operations to the data.
- **Downloader:** Downloads processed data into Excel, sorting and adding necessary headers.

### Schemas Folder

The schemas are the models of the data. The data from the muscle motion enters the schemas and then the code can use it. 
Overview.py configures the data we have for each specific overview. The alias names for group, well, avg/std can be changed here if you want the headers of these columns to be named differently in the excel.
The well and group name are extracted according to the pattern that appears in each function that corresponds to the name extraction. If your folder and file names are formatted correctly as mentioned under the main.py section this will run smoothly.
Contraction.py configures the data for each contraction. The alias names for these columns can be changed here.
Filter_flag states what excel style is correspondent with something that needs to be deleted (default is red) and what was updated (default is yellow).
Additional formulas (other than the default average and std) can be added to the excel format through the configuration.py (not in the schemas folder). 
Simply add the additional formule to the overview_formulas parameter. The order the formulas appear in the overview_formulas is the order they will appear in the excel. 
After adding a formula you can change the alias name in the overview.py to include the additional formula (ex- change ‘avg/std’ to ‘avg/std/new formula’.



### Utils Folder

Contains utility functions that are used throughout the codebase.

### Data Filters Folder

This folder holds the filter classes, including prewritten filters like:
- **Amplitude Filter**
  The filter is built in two parts:
  First-
  A part that marks the contractions for filtration. It uses the contraction amplitude to mark noise and baseline errors.
  Any contraction that is either 2 std deviations bellow the mean amplitude or ¼ of the highest peak are marked for filtration.
  The filter parameters can be edited to be stronger or weaker by changing the std_from_amplitude (how many std away from mean you want) or partial_amplitude (what fraction of the maximum contraction amplitude you want) parameter at the beginning of the code.
  Second-
  The second part of the code is built to differentiate between baseline errors and noise errors.
  To do so a list of “actual peaks” is formed (a list that doesn’t include the contractions marked for filtration).
  From the actual peaks a list called difference_real_peak_to_peak is formed. This list is a list of the time to peak between each “actual peak”.
  Then the code runs on the filtered list, for each contraction it checks if it is less then median-0.25std away from the actual peak before it or the actual peak after it.
  If one if these is true it is filtered as noise, if not then it is filtered as a baseline. For each noise contraction the time to peak is updated to the next contraction in the list.
  This filter can also be edited to strengthen or weaken the parameters by changing std_from_peak_to_peak(which is how many std from the median you want).

- **Simple Filter**
  As its name suggests this is a simple filter.
  It runs on the data left after the amplitude filter and gets ride of any contractions with zero values (except if the zero value is in the peak_to_peak column).

- **Relaxation Time Filter**
  The code uses the knowledge that a physiological relaxation time at rest is no less than 200 milliseconds and no greater than 1200.
  The code also relays on the approximation that the relaxation time is affected linearly by the frequency.
  This filter uses the information provided at the start of the code on the frequency.
  The code runs on each relaxation time and checks if it is smaller than 200/frequency or >= to 1200. If this is true it is filtered out.

- **Contraction Outlier Filter**
  The filter runs on each column and calculates outliers using percentiles and iqr.
  An outlier is defined as: smaller than q1-1.5*iqr  or  bigger than q3+1.5*iqr
  If a peak has an outlier in either contraction duration, time to peak, or contraction amplitude the whole peak is deleted.
  If a peak has an outlier in any of the other columns the peak is kept but the final excel will show “outlier” in the specified column.
  In the final filtered excel the averages under each column do not include the “outliers”.

- **Overview Outlier Filter**
  This filter is similar to Contraction Outlier Filter but runs on wells. The filter will compare wells from the same group by using the averages of each column.
  Outliers are defined as in Contraction Outlier Filter.
  If a well is found to be an outlier the well name is marked in red with a “delete” written next to, and in the final excel after filtrations it will not appear.



### Adding a New Filter

If you want to add an addition filter you need to add filters.add_filter(“new filter name”) to the filter_data function written in the main.py code. 
Be sure to also add the filter to the import section at the top of the main.py code. 
It is important to remember that the order in which the filters appear in the filter_data function is the order they run. 
(*the amplitude and simple filters that are already part of the code must run in the order they are written by default to work properly. 
And the outlier contraction and outlier wells must run in there order after all other filters). 
Additional information about how to add a new filter will be written under services.

To add a new filter:
1. Create a new script.
2. Define the filter class inheriting from `BaseDataFilter`.
3. Update `main.py` to add the new filter in the `filter_data` function and include it in the import section.


## 📊 How to Interpret Output

The program generates Excel files with four key outputs:
1. **All Data with Deleted and Edited Contractions** (Red = Deleted, Yellow = Edited).
2. **Final Data After Noise Filtering**.
3. **Deleted Contractions from Physiological Filters**.
4. **Final Data After All Filtration Steps** (Outliers will be flagged).

You can verify successful execution by checking for the presence of these Excel files and ensuring they are timestamped correctly.
