"""
Potential TODO ideas
- plot graph directly from dataframe
"""

# imports
from csv import DictReader
import matplotlib.pyplot as plt
from pandas import DataFrame
from datetime import datetime as dates
from time import strftime, localtime


# read_file = "BPA-data.txt"
read_file = "BPA-09-21.txt"

# function takes in datestamp in the form of "mm/dd/yyyy hh:mm" and returns converted unix timecode
def to_unix(date) -> int:
    # the formate of timestamps in the raw BPA data (written using pythons strptime notation)
    bpa_format = "%m/%d/%Y %H:%M"

    # converts passed datestamp to datetime object and derives unix timecode
    return int(dates.strptime(date, bpa_format).timestamp())


# ------------------------------------------------------------ #
# Imports data from file and processes for graphing

# Loads raw data from txt file using csv.DictReader and dumps to pandas dataframe
with open(read_file, "r") as file_data:
    read_data = DictReader(file_data, delimiter="\t")  # loads file using csv module with seperator set to tabs
    load_data = DataFrame(read_data)

# removes all entries from dataframe that do not have a value in their "Load" field
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

info_frame = load_data.aggregate(["idxmax", "idxmin"])
print(info_frame)
# exit()

# ------------------------------------------------------------ #
# plots bpa data to graph and modifies scaling and axis ticks to make chart usable

# defines title and axis names of graph
plt.title("BPA load graph")
plt.xlabel("Time")
plt.ylabel("Megawatts")


# gets list of all columns in dataframe
columns = load_data.columns.tolist()

# iterates through all columns in dataframe and plots them to graph
# column values are plotted to the y-axis and time is used for x
colors = {"Load": "Red", "VER": "green", "Hydro": "blue", "Fossil/Biomass": "maroon", "Nuclear": "purple", "Total Generation": "gray"}  # colors match those from original BPA chart
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
plt.ylim(0, 11000)
plt.xlim(major_ticks[0], major_ticks[-1])
plt.legend()
plt.yscale("linear")

plt.show()

