#!/bin/bash

# Step 1: Add LabRat/src to PYTHONPATH
export PYTHONPATH="$PYTHONPATH:LabRat/src"

# Step 2: Create a virtual environment named 'venv'
python3 -m venv venv

# Step 3: Activate the virtual environment
source venv/bin/activate

# Step 4: Install requirements from LabRat/requirements.txt
pip install -r LabRat/requirements.txt

# Step 5: Run main.py from LabRat/src
python LabRat/src/main.py

# Step 6: Deactivate the virtual environment
deactivate
