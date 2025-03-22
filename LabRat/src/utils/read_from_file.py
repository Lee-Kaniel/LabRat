from typing import List


def read_fields_from_file(file_path: str) -> List[List[str]]:
    """
        Reads a text file and splits each line into a list of words by white spaces.

        :param file_path: The path to the txt file
        :return List[List[str]]: List of the text file lines split by white spaces.
    """
    with open(file_path, 'r') as file:
        return [line.split() for line in file]
