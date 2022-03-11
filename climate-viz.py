from calendar import month, month_name, week
import datetime
from enum import unique
from re import T
import time
from tokenize import group
from matplotlib import use
from matplotlib.pyplot import axis, winter
from numpy import add, datetime64, number
from numpy.core.fromnumeric import sort
from numpy.core.numeric import outer
import pandas as pd
from pandas.core.window import rolling
import streamlit as st
import altair as alt
from toolz.itertoolz import frequencies
import numpy as np

@st.cache
def read_data():
    data = pd.read_csv('./2895745.csv',parse_dates=[2])
    return data
data = read_data()

st.header("Hailey, Idaho - Weather Exploration")

INTRO = """I've been living in Hailey, Idaho for a little over a month, and by all accounts it has been an unusual Winter! Since arriving, Hailey hasn't
had more than 1 inch of new snow. Ketchum, Idaho, 20 minutes from Hailey and the location of the Sun Valley Ski Resort, hasn't had much more! Everyone I
spoke to reported that the early season was phenomenal. From about mid-December through the first week of January, it snowed consistently and heavily.
However, since then, there hasn't been hardly any new snowfall!

I wanted to determine if this Winter was unusual. I chose to look at historical data for Hailey dating back to 1923.
"""
st.markdown(INTRO)

LOCATION = """The climate data is sourced from area code 83333 which is my area code in Hailey, Idaho. NOAA (National Oceanic and Atmospheric Associaton) and the NCDC
(National Climate Data Center) maintain records for this region dating back to the late 1800s. 9 sites recorded data from 1923-present, though the information recorded by
station varies."""

st.markdown(LOCATION)
st.image('./83333_region.png')

MIN_DATE = min(data['DATE'].dt.date)
MAX_DATE = max(data['DATE'].dt.date)
MONTHS = list(range(8,13)) + list(range(1,8))
UNIQUE_DATE_RANGE = data['DATE'].dt.date.sort_values().unique()

def format_months(option):
    """Format month options for slider."""
    if option == 1:
        return "Jan"
    elif option == 2:
        return "Feb"
    elif option == 3:
        return "Mar"
    elif option == 4:
        return "Apr"
    elif option == 5:
        return "May"
    elif option == 6:
        return "Jun"
    elif option == 7:
        return "Jul"
    elif option == 8:
        return "Aug"
    elif option == 9:
        return "Sep"
    elif option == 10:
        return "Oct"
    elif option == 11:
        return "Nov"
    elif option == 12:
        return "Dec"

def format_month_day(date):
    """Return formatted month-day for chart display."""
    month = date.month
    day = date.day

    if month == 1:
        return f"Jan {day}"
    elif month == 2:
        return f"Feb {day}"
    elif month == 3:
        return f"Mar {day}"
    elif month == 4:
        return f"Apr {day}"
    elif month == 5:
        return f"May {day}"
    elif month == 6:
        return f"Jun {day}"
    elif month == 7:
        return f"Jul {day}"
    elif month == 8:
        return f"Aug {day}"
    elif month == 9:
        return f"Sep {day}"
    elif month == 10:
        return f"Oct {day}"
    elif month == 11:
        return f"Nov {day}"
    elif month == 12:
        return f"Dec {day}"

def format_month_week(date):
    """Return formatted month-day for chart display."""
    month = date.month
    week = 1 + ((date.day - 1) // 7)

    if month == 1:
        return f"Jan {week}"
    elif month == 2:
        return f"Feb {week}"
    elif month == 3:
        return f"Mar {week}"
    elif month == 4:
        return f"Apr {week}"
    elif month == 5:
        return f"May {week}"
    elif month == 6:
        return f"Jun {week}"
    elif month == 7:
        return f"Jul {week}"
    elif month == 8:
        return f"Aug {week}"
    elif month == 9:
        return f"Sep {week}"
    elif month == 10:
        return f"Oct {week}"
    elif month == 11:
        return f"Nov {week}"
    elif month == 12:
        return f"Dec {week}"

def format_date(option):
    return option.strftime("%m.%d.%Y")

def format_month_range(start_month, end_month):
    """Return a list range from start month to end month for data filtering."""

    if start_month >=8 and start_month <= 12:
        start_range = list(range(start_month, 13))
        end_range = list(range(1, end_month + 1))
        month_range = start_range + end_range
    else:
        month_range = list(range(start_month, end_month + 1))
    
    return month_range

user_min_date, user_max_date = st.sidebar.select_slider("Select Date Range", options = UNIQUE_DATE_RANGE, format_func=format_date, value = (MIN_DATE, MAX_DATE))
start_month, end_month = st.sidebar.select_slider("Select Month Range", options = MONTHS, format_func = format_months, value = (10, 4))

MONTH_RANGE = format_month_range(start_month, end_month)

@st.cache()
def augment_data_dates(data):
    data = data.assign(
        decade=data['DATE'].dt.year // 10 * 10).assign(
            week = 1 + ((data['DATE'].dt.day - 1) // 7)).assign(
                day=data['DATE'].dt.day).assign(
                    year = data['DATE'].dt.year).assign(
                        month = data['DATE'].dt.month
                    )
    month_day = data['DATE'].apply(format_month_day)
    month_week = data['DATE'].apply(format_month_week)
    data = pd.merge(left = data, right = month_day, how='left', left_index = True, right_index=True)
    data = pd.merge(left = data, right = month_week, how='left', left_index = True, right_index=True)
    return data
date_augmented_data = augment_data_dates(data)

@st.cache()
def time_filter_data(data):
    time_filtered_data = data[(data['DATE_x'].dt.date < user_max_date) & (data['DATE_x'].dt.date > user_min_date)]
    time_filtered_data = time_filtered_data[time_filtered_data['DATE_x'].dt.month.isin(MONTH_RANGE)]
    return time_filtered_data

time_filtered_data=time_filter_data(date_augmented_data)

FILTERING = """Start by filtering the dataset with the sliders in the sidebar on the left (if you'd like). The date range includes all data from all stations
between the dates selected. Similarly, the month range will filter the data to only reflect the months between the range selected, inclusive. The filters default to
the entire date range for those months that generally report snowfall."""

st.markdown(f"_{FILTERING}_")

################################
##### Snow Totals Barchart #####
################################
SNOWFALL_TOTALS = """To start, we can look at snowfall totals, colored by the station recording the data. The red line represents a 5-year rolling average of
snowfall to hint at trends on a larger time scale. There are a few important things to notice about this chart. First, out of the 9 stations in our dataset, only 4 have
reported the snowfall metric. In addition, don't be fooled by the contiguous x-axis: looking closely at the years represented, you'll note that there are periods where
snowfall data is absent, like from 1989-2005, during which no snowfall data is available. Finally, it's important to realize that snowfall could vary due to the different
locations of the stations throughout this region."""
st.write(SNOWFALL_TOTALS)

snowfall_totals = time_filtered_data.groupby(by=['year', 'STATION'])['SNOW'].sum().reset_index()
snowfall_totals = snowfall_totals[snowfall_totals['SNOW'] > 0]

bars = alt.Chart(snowfall_totals).mark_bar().encode(
    alt.Y('SNOW:Q', title = "Snowfall (Inches)"),
    alt.X('year:O', title="Year"),
    alt.Color('STATION:N', title = "Station")
)
rolling_avg = alt.Chart(snowfall_totals).mark_line(color='red').transform_window(
    groupby=['STATION'],
    frame = [-4,0],
    rolling_mean = 'mean(SNOW)'
).encode(
    x='year:O',
    y='rolling_mean:Q'
)
snowfall_totals = (bars + rolling_avg).properties(
    width=1000,
    height=500,
    title="Snowfall Totals"
)

snowfall_totals
SNOWFALL_TOTALS_CONCLUSIONS = """This visualization does however contribute to an answer to my original question. 2022 has had significantly less snow than
2019-2021, and these 4 values were all recorded at the same station. Across all stations, 2022 is one least snowiest seasons on record, in addition to 2013."""
st.write(SNOWFALL_TOTALS_CONCLUSIONS)

###############################
##### Snow Depth Stations #####
###############################
st.write("""Since the 2004, a number of stations have been recording snow depth. We can visualize total snow depth at these stations using a stacked bar chart.
Surprisingly, total snow depth in 2022 is higher for most stations compared to other years.""")

snow_depth_total = date_augmented_data[date_augmented_data["year"] >= 2004]

comparison3_snowfall = snow_depth_total.groupby(by=['year', 'STATION'])['SNWD'].mean().reset_index()
snow_line3 = alt.Chart(comparison3_snowfall).mark_bar().encode(
    alt.X('year:N'),
    alt.Y('SNWD:Q'),
    alt.Color('STATION:N'),
).properties(
    width=1000,
    height=500,
    title="Snow Depth since 2004"
)
snow_line3

#################################
##### Snow Depth Comparison #####
#################################
SNOW_DEPTH = """Snow depth is another good representation of the amount of snowfall in a given Winter. We can use a line chart to compare
average snow depth across all stations for this Winter vs a prior Winter. Use the slider to select a comparison year."""
comparison_year = st.slider("Select Comparison Year", min_value=2004, max_value=2021)

@st.cache()
def prepare_snow_depth_data(comparison_year, data):
    """Cache snow depth preparation."""
    current_winter = data[((data['year']==2021) & (data['month'].isin([12]))) | (data['year']==2022)]
    current_winter['winter_type'] = "Current"
    comparison_winter = data[((data['year']==comparison_year-1) & (data['month'].isin([12]))) | (data['year']==comparison_year)]
    comparison_winter = comparison_winter[(comparison_winter['month'] <= 2) | ((comparison_winter['month'] == 12) & (comparison_winter['year'] == comparison_year -1))]
    comparison_winter['winter_type'] = "Past"

    winter_comparison = pd.concat([current_winter, comparison_winter])
    month_day = winter_comparison['DATE_x'].apply(format_month_day)
    winter_comparison = pd.merge(left=winter_comparison, right = month_day, how='left', on=winter_comparison.index)
    winter_comparison = winter_comparison.groupby(by=['DATE_y', 'winter_type'])['SNWD'].mean().reset_index()
    return winter_comparison

winter_comparison = prepare_snow_depth_data(comparison_year, date_augmented_data)

sort_order = ["D", "J", "F"]
dates_sorted = sorted(winter_comparison['DATE_y'],key = lambda date: (sort_order.index(date[0]), int(date[3:])))

snow_depth_comparison = alt.Chart(winter_comparison).mark_line().encode(
    alt.Y('SNWD:Q', title = "Snow Depth (Inches)"),
    alt.X('DATE_y:O', title="Day", sort=dates_sorted, axis=alt.Axis(labelOverlap=True)),
    alt.Color('winter_type:N', title="Winter")
).properties(
    width = 1000,
    height = 500,
    title = f"Snow Depth Comparison, Current Winter to Winter {comparison_year}"
)
snow_depth_comparison

SNOW_DEPTH_CONCLUSIONS = """This chart corroborates what I've heard from locals. The early season was good for snow, but snow depth in Hailey has only been
declining since about December 26th! In other Winters, the snow depth continues to accumulate throughout the season. That said, snow depth at the end of
February this Winter is comparable to other Winters, in some cases exceeding values from the past. This means that the early season really must have been
exceptional - even without additional storms after mid-January, the snow depth is similar to that of most other Winters. This chart also tells me that many
of the stations do not seem to report on snowfall because the total snowfall reported in 2022 is only about 10 inches, while snow depth was close to 50 inches
on December 26th. Check 2004 and 2017 for a couple exceptional Winters from the past!"""

st.write(SNOW_DEPTH_CONCLUSIONS)

##################################
###### Temp & Precipitation ######
##################################
def format_group_method(option):
    return option.capitalize()

col1, col2 = st.columns(2)
with col1:
    time_resolution= st.radio("Select Time Resolution",index = 2, options=["month","week","day"], format_func=format_group_method)
with col2:
    # sidebar for widget control
    temp_select = st.radio(
        label="Min or Max Comparison",
        options=['Min Temp', 'Max Temp']
    )
if temp_select == 'Min Temp':
    TEMP_FILTER = 'TMIN'
else:
    TEMP_FILTER = 'TMAX'

month_order = ["Oct","Nov","Dec","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep"]
dates_sorted = sorted(time_filtered_data['DATE_y'].unique(), key = lambda date: (month_order.index(date[:3]), int(date[3:])))

if time_resolution == "month":
    temp = alt.Chart(time_filtered_data).mark_rect().encode(
        alt.Y('decade:N', title="Decade", sort='descending'),
        alt.X('month:O', title=f"{time_resolution}".capitalize(), sort=dates_sorted, axis=alt.Axis(labelOverlap=True)),
        alt.Color(f'mean({TEMP_FILTER}):Q', scale={'scheme':'reds'}, title=f"{temp_select}"),
    )
    precip = alt.Chart(time_filtered_data).mark_rect().encode(
        alt.Y('decade:N', title="Decade", sort='descending'),
        alt.X('month:O', title=f"{time_resolution}".capitalize(), sort=dates_sorted, axis=alt.Axis(labelOverlap=True)),
        alt.Color('mean(PRCP):Q', scale={'scheme':'greens'}, title="Precip"),
    )
    snow = alt.Chart(time_filtered_data).mark_rect().encode(
        alt.Y('decade:N', title="Decade", sort='descending'),
        alt.X('month:O', title=f"{time_resolution}".capitalize(), sort=dates_sorted, axis=alt.Axis(labelOverlap=True)),
        alt.Color('mean(SNOW):Q', scale={'scheme':'blues'}, title="Snowfall"),
    )
elif time_resolution == "week":
    temp = alt.Chart(time_filtered_data).mark_rect().encode(
        alt.Y('decade:N', title="Decade", sort='descending'),
        alt.X('DATE:O', title=f"{time_resolution}".capitalize(), sort=dates_sorted, axis=alt.Axis(labelOverlap=True)),
        alt.Color(f'mean({TEMP_FILTER}):Q', scale={'scheme':'reds'}, title=f"{temp_select}"),
    )
    precip = alt.Chart(time_filtered_data).mark_rect().encode(
        alt.Y('decade:N', title="Decade", sort='descending'),
        alt.X('DATE:O', title=f"{time_resolution}".capitalize(), sort=dates_sorted, axis=alt.Axis(labelOverlap=True)),
        alt.Color('mean(PRCP):Q', scale={'scheme':'greens'}, title="Precip"),
    )
    snow = alt.Chart(time_filtered_data).mark_rect().encode(
        alt.Y('decade:N', title="Decade", sort='descending'),
        alt.X('DATE:O', title=f"{time_resolution}".capitalize(), sort=dates_sorted, axis=alt.Axis(labelOverlap=True)),
        alt.Color('mean(SNOW):Q', scale={'scheme':'blues'}, title="Snowfall"),
    )
else:
    temp = alt.Chart(time_filtered_data).mark_rect().encode(
        alt.Y('decade:N', title="Decade", sort='descending'),
        alt.X('DATE_y:O', title=f"{time_resolution}".capitalize(), sort=dates_sorted, axis=alt.Axis(labelOverlap=True)),
        alt.Color(f'mean({TEMP_FILTER}):Q', scale={'scheme':'reds'}, title=f"{temp_select}")
    )
    precip = alt.Chart(time_filtered_data).mark_rect().encode(
        alt.Y('decade:N', title="Decade", sort='descending'),
        alt.X('DATE_y:O', title=f"{time_resolution}".capitalize(), sort=dates_sorted, axis=alt.Axis(labelOverlap=True)),
        alt.Color('mean(PRCP):Q', scale={'scheme':'greens'}, title="Precip")
    )
    snow = alt.Chart(time_filtered_data).mark_rect().encode(
        alt.Y('decade:N', title="Decade", sort='descending'),
        alt.X('DATE_y:O', title=f"{time_resolution}".capitalize(), sort=dates_sorted, axis=alt.Axis(labelOverlap=True)),
        alt.Color('mean(SNOW):Q', scale={'scheme':'blues'}, title="Snowfall"),
    )
temp = temp.properties(
    width=1000,
    height=400,
    title=f"{temp_select} Across Decades"
)
temp
snow = snow.properties(
    width=1000,
    height=400,
    title="Snowfall Across Decades"
)
snow
precip = precip.properties(
    width=1000,
    height=400,
    title="Precipitation Across Decades"
)
precip

#######################################
####### Min Max Temp Comparison #######
#######################################

current_decade = time_filtered_data[time_filtered_data['DATE_x'].dt.year >= 2020]
current_decade["time_period"] = "Current Decade (2020-2022)"

range_start, range_end = st.select_slider("Choose a Time Period to Compare", options=np.arange(1923,2020), value = (1923,2019))
time_frame = list(range(range_start, range_end+1))
other_time_frame = time_filtered_data[time_filtered_data['year'].isin(time_frame)]
other_time_frame["time_period"] = f"Comparison ({range_start}-{range_end})"

comparison = pd.concat([current_decade, other_time_frame])
tmin = comparison.groupby(by=["DATE_y", "time_period"])['TMIN'].mean().reset_index()
tmax = comparison.groupby(by=["DATE_y", "time_period"])['TMAX'].mean().reset_index()
tmin_line = alt.Chart(tmin).mark_line().encode(
    alt.X('DATE_y:O', sort = dates_sorted, axis=alt.Axis(labelOverlap=True), title = "Date"),
    alt.Y('TMIN:Q', title="Min Temp"),
    alt.Color('time_period:N',sort = ['Current Decade (2020-2022)'])
)
tmax_line = alt.Chart(tmax).mark_line().encode(
    alt.X('DATE_y:O', sort = dates_sorted, axis=alt.Axis(labelOverlap=True), title = "Date"),
    alt.Y('TMAX:Q', title = "Max Temp"),
    alt.Color('time_period:N', title="Time Period", sort = ['Current Decade (2020-2022)'])
)
temp_comparison = (tmin_line + tmax_line).properties(
    width = 1000,
    height = 500,
    title = f"Comparing Current Decade Temps to Temps {range_start}-{range_end}"
)
temp_comparison

#######################################
##### Min Max Snowfall Comparison #####
#######################################
selection = alt.selection_multi(fields=['time_period'])
color = alt.condition(selection,
                      alt.Color('time_period:N', legend=None),
                      alt.value('lightgray'))

snow_points = alt.Chart(comparison).mark_point().encode(
    alt.X('DATE_y:N', axis = alt.Axis(labelOverlap=True), sort = dates_sorted, title="Date"),
    alt.Y('mean(SNOW):Q', title="Snowfall"),
    alt.Size('mean(SNOW):Q', title="Snowfall (inches)"),
    color=color,
).properties(
    width=1000,
    height=500,
    title=f"Comparing Current Decade Snowfall to Snowfall {range_start}-{range_end}"
)

legend = alt.Chart(comparison).mark_rect().encode(
    y=alt.Y('time_period:N', sort="descending", axis=alt.Axis(orient='right'), title="Time Period"),
    color=color
).add_selection(
    selection
)

snow_points | legend

#######################################
##### Min Max Snowfall Comparison #####
#######################################
decade_select = alt.selection_multi(fields=['decade'])
color = alt.condition(decade_select,
                      alt.Color('decade:N', legend=None, scale={'scheme':'category20'}),
                      alt.value('lightgray'))
comparison['decade'] = comparison['decade'].astype(str)

snow_points2 = alt.Chart(comparison).mark_point().encode(
    alt.X('DATE_y:N', axis = alt.Axis(labelOverlap=True), sort = dates_sorted, title="Date"),
    alt.Y('mean(SNOW):Q', title="Snowfall"),
    alt.Size('mean(SNOW):Q', title="Snowfall (inches)"),
    color=color
).properties(
    width=1000,
    height=500,
    title="Comparing 2020 Snowfall to Other Decades"
)

legend = alt.Chart(comparison).mark_rect().encode(
    y=alt.Y('decade:N', sort="descending", axis=alt.Axis(orient='right'), title = 'Decade'),
    color=color
).add_selection(
    decade_select
)

snow_points2 | legend