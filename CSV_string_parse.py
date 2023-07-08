__version__ = 1.0
"""
Ideas for improvements
- allow user to define a type/ lambda expression to apply to each entry
- allow user to define custom headers in place of those in string  (custom_headers: list = None) 
  - verify that number of entries in custom headers list matches number of columns in csv
- allow user to define NOT to grab headers from first row of string  (parse_headers: bool = True)
  - link to custom headers above, but automatically generate headers if undefined
- allow user to specify max number of rows to be processed
- add function to convert string to 2D table of lists
- add function to convert string to pandas dataframe
"""

def main_parser(csv_string: str, delimiter: str = ",", newline: str = "\n") -> tuple[list, list]:
    """
    Takes in raw csv formatted string and splits into rows, parsing headers from first row.
    Also checks to ensure that last row is not empty, if it is, the row is removed

    :param csv_string: A string in format of a csv file to be parsed
    :param delimiter: Delineator character between each column (defaults to ',')
    :param newline: Character(s) defining a new line/row (defaults to '\\n')
    :return: returns list of headers for CSV and list of rows (not including header row)
    """
    rows: list[str] = csv_string.split(newline)  # splits csv string into rows using designated newline chars
    headers: list[str] = rows[0].split(delimiter)  # splits first row using delimiter to get csv headers
    del rows[0]  # remove header row

    if not rows[-1]:  # checks if last row is empty, if so row is removed
        print("Last row of string was empty - removed row")
        del rows[-1]

    print(f"found {len(headers)} column headers and {len(rows)} rows")
    return headers, rows

def row_list(csv_string: str, delimiter: str = ",", newline: str = "\n") -> list[dict]:
    """
    Parses a string taking the format of a CSV file and returns a list of each row sorted into dictionary

    :param csv_string: A string in format of a csv file to be parsed
    :param delimiter: Delineator character between each column (defaults to ',')
    :param newline: Character(s) defining a new line/row (defaults to '\\n')
    :return: A list with each row seperated into dictionary with csv header values as keys ie -  {header 1: item 1, ...}
    """

    headers, rows = main_parser(csv_string, delimiter, newline)  # extracts headers and rows from incoming csv string

    return_list: list[dict] = []
    for row in rows:
        split_row = row.split(delimiter)  # splits row at delimiter
        new_dict = dict(zip(headers, split_row))  # uses zip command to create form [(header name: row entry) ...] - zipped row is then converted to dict
        return_list.append(new_dict)  # new dict is appended to return list

    return return_list

def column_list(csv_string: str, delimiter: str = ",", newline: str = "\n") -> dict[list[str]]:
    """
    Parses a string taking the format of a CSV file and returns a dict of all rows sorted to their columns

    :param csv_string: A string in format of a csv file to be parsed
    :param delimiter: Delineator character between each column (defaults to ',')
    :param newline: Character(s) defining a new line/row (defaults to '\\n')
    :return: A dict all rows sorted to their associated column, using header names as keys ie- {header 1: [row 1, row 2], ...}
    """

    headers, rows = main_parser(csv_string, delimiter, newline)  # extracts headers and rows from incoming csv string

    return_dict: dict[list] = {header: [] for header in headers}  # creates dict with headers as keys and empty list as key vals
    for row in rows:
        split_row = row.split(delimiter)  # splits row into list using delimiter

        for header, val in zip(headers, split_row):  # zips headers and list items together and iterates through
            return_dict[header].append(val)  # header calls dict associated entry and appends new item to list

    return return_dict
