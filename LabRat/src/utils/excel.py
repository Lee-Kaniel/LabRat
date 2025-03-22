import re


def serialize_excel_title(input_string):
    # Replace or remove invalid characters
    clean_string = re.sub(r'[\\/:*?"<>|\[\]]+', '', input_string)  # Remove special characters
    clean_string = clean_string.replace(' ', '_')  # Replace spaces with underscores for table names

    # Check if the name starts with a number, prepend with an underscore if so
    if re.match(r'^\d', clean_string):
        clean_string = '_' + clean_string

    # Check if the clean string is empty or reduced to an invalid state
    if clean_string == '':
        return "None"

    return clean_string


def serialize_excel_worksheet_name(input_string):
    # Replace or remove invalid characters
    clean_string = re.sub(r'[\\/:*?"<>|\[\]]+', '', input_string)

    # Ensure the name is not longer than 31 characters
    clean_string = clean_string[:31]

    # Check if the name is reduced to an invalid state (e.g., empty)
    if clean_string.strip() == '':
        return "None"

    return clean_string
