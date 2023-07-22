"""
Potential TODO ideas
-
"""

# imports
from csv import DictReader
import requests as req
import matplotlib.pyplot as plt
from pandas import DataFrame
from datetime import datetime as dates
from time import strftime, localtime
import CSV_string_parse as parser
import argparse
from pathlib import Path

__version__ = 2.0

USE_WEB = True  # set True to load real-time data from web source
file_name: Path = Path("test.txt")  # path to file to use if USE_WEB is false
bpa_page = "https://transmission.bpa.gov/Business/Operations/Wind/baltwg.txt"  # URL to use if USE_WEB is true


# function takes in datestamp in the form of "mm/dd/yyyy hh:mm" and returns converted unix timecode
def to_unix(date) -> int:
    bpa_format = "%m/%d/%Y %H:%M"  # the formate of timestamps in the raw BPA data (written using pythons strptime notation)
    return int(dates.strptime(date, bpa_format).timestamp())  # converts passed datestamp to datetime object and derives unix timecode


# URL document and file document have different newline delineators, if statement chooses appropriate one to use
page_newline: str = ""
page_raw: str = ""  # raw loaded document is saved here
if USE_WEB:
    print(f"Attempting to request document \'{bpa_page}\'")
    page_newline = "\r\n"

    try:
        page_raw = req.get(bpa_page).text  # load url using requests library
    except req.exceptions.ConnectionError:  # catches exception if library cannot connect to url
        print(f"could not connect to page \'{bpa_page}\'\n\tCheck if device is connected to internet")
        exit()
else:
    print(f"loading file \'{file_name}\'")
    page_newline = "\n"

    with file_name.open() as file:  # pens file using pathlib.Path builtin
        page_raw = file.read()  # grabs entire contents of file and loads as string

page_process: list = page_raw.split(page_newline)[11:]  # removes first 11 lines of document (unneeded filler)
page_build: str = "\n".join(page_process)  # rejoins document into string

data = parser.row_list(page_build, "\t")  # calls parsing function to convert csv document to dict
load_data: DataFrame = DataFrame(data)  # creates data frame with loaded csv data

# removes all entries from dataframe that do not have a value in their "Load" field
# BPA builds data table in such a way that often leads to empty rows (other than date string)
blank_entries = load_data[load_data["Load"] == ''].index.values.tolist()
load_data.drop(index=blank_entries, inplace=True)

# renames timestamp column
load_data.rename(columns={"Date/Time       ": "Date"}, inplace=True)

# changes existing datestamps to unix timestamps
load_data["Date"] = load_data["Date"].transform(to_unix)

# sets Date column to be dataframe index
load_data.set_index("Date", drop=True, inplace=True)

# applies int() operator to all entries in dataframe
load_data = load_data.applymap(lambda value: int(value))

# sum of all generation sources
load_data["Total Generation"] = load_data["VER"] + load_data["Hydro"] + load_data["Fossil/Biomass"] + load_data["Nuclear"]

# excess generation, expressed as the difference between total generation and system load
load_data["Excess"] = load_data["Total Generation"] - load_data["Load"]
load_data["Excess"].where(load_data["Excess"] >= 0, 0, inplace=True)  # limits the lowest potential value of column to 0

# if load_data["Excess"].min() == 0:
#     load_data["Import"] =

info_frame = load_data.aggregate(["max", "min", "average"])
info_frame = info_frame.applymap(lambda value: int(value))
print(info_frame)

# ------------------------------------------------------------ #
# plots bpa data to graph and modifies scaling and axis ticks to make chart usable

# defines title and axis names of graph
plt.title("BPA load graph")
plt.ylabel("Megawatts")


# gets list of all columns in dataframe
columns = load_data.columns.tolist()

# iterates through all columns in dataframe and plots them to graph
# column values are plotted to the y-axis and time is used for x
colors = {"Load": "Red", "VER": "green", "Hydro": "blue", "Fossil/Biomass": "maroon", "Nuclear": "purple", "Total Generation": "gray", "Excess": "pink"}  # colors match those from original BPA chart
for column in columns:
    plt.plot(load_data.index.to_list(), load_data[column], label=column, color=colors[column])

# generates major and minor ticks for x-axis
tw_hours = 43200  # number of seconds in 12 hours
start_time = load_data.index.to_list()[0]  # gets time of first entry in data
minor_start = start_time + tw_hours  # adds 12 hours to first start date for minor tick counting
major_ticks = [start_time + (inc * tw_hours * 2) for inc in range(8)]
minor_ticks = [minor_start + (inc * tw_hours * 2) for inc in range(7)]

# generates labels for major ticks by taking unix time stamp and converting into custom datestamp
major_labels = [strftime("%b%d", localtime(tick)) for tick in major_ticks]

# sets x-axis ticks
plt.xticks(major_ticks, major_labels)

# sets y-axis ticks
y_ticks = [0, 5000, 10000]
plt.yticks(y_ticks, [str(val) for val in y_ticks])

# visual modifiers
plt.minorticks_on()
plt.grid()
plt.ylim(-10, 13000)
plt.xlim(major_ticks[0], major_ticks[-1])
plt.legend()
plt.yscale("linear")

# TODO: Change background color to something less eye burning

plt.savefig("test.jpg", dpi=300)
# plt.show()
