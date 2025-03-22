@echo off

REM Step 1: Add LabRat/src to PYTHONPATH
set PYTHONPATH=%PYTHONPATH%;LabRat\src

REM Step 2: Create a virtual environment named 'venv'
python -m venv venv

REM Step 3: Activate the virtual environment
venv\Scripts\activate

REM Step 4: Install requirements from LabRat/requirements.txt
pip install -r LabRat\requirements.txt

REM Step 5: Run main.py from LabRat/src
python LabRat\src\main.py

REM Step 6: Deactivate the virtual environment
deactivate

