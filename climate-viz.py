from re import T
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
    temps = pd.read_csv('./2895745.csv',parse_dates=[2])
    return temps
temps = read_data()

print(temps.dtypes)

# group by station
st.write(temps.groupby(by="STATION").size())

hailey1 = temps[temps.STATION == "USC00103942"]

hailey2 = temps[temps.STATION == "USC00103940"]

test = temps[temps.STATION == "USS0014F16S"]

ohio_gulch_no_snow = temps[temps.STATION == "USR0000IOHI"]


test1 = alt.Chart(hailey1).mark_line().encode(
    x = 'DATE',
    y = 'TMIN'
)

test1

test2 = alt.Chart(hailey2).mark_line().encode(
    x = 'DATE',
    y = 'TMIN'
)

test2

temps3 = ohio_gulch_no_snow[ohio_gulch_no_snow.TMAX < 200]

test4 = alt.Chart(temps3).mark_line().encode(
    x = 'DATE',
    y = 'TMAX'
)

test4

# sidebar for widget control
add_min_max_select = st.sidebar.radio(
    label="Min or Max Comparison",
    options=['Min Temp', 'Max Temp']
)
if add_min_max_select == 'Min Temp':
    temp_filter = 'TMIN'
else:
    temp_filter = 'TMAX'

# 1920s - 1980s
february1 = hailey1[hailey1["DATE"].dt.month == 2]

# 1990s - 2020s
february2 = temps3[temps3["DATE"].dt.month == 2]

feb_total = pd.concat([february1, february2])
feb_total['decade'] = feb_total['DATE'].dt.year // 10 * 10
feb_total['week'] = 1 + ((feb_total['DATE'].dt.day - 1) // 7)
feb_total['day'] = feb_total['DATE'].dt.day

# decade daily comparison
# x: day
# y: decade
# color: temp
decade_day_min_avg = feb_total.groupby(by=["decade","day"])[temp_filter].mean().reset_index()
decade_day_min_avg = alt.Chart(decade_day_min_avg).mark_rect().encode(
    alt.X('day:N', title = "Day"),
    alt.Color(f'{temp_filter}:Q', bin=alt.Bin(maxbins=20), scale={"scheme":"purples"}),
    alt.Y('decade:N', sort='descending', title="Decade")
).properties(
    width=1000,
    height=500,
    title="February Average Daily Temps Across Decades"
)
decade_day_min_avg

# decade weekly comparison
# x: day
# y: decade
# color: temp
decade_week_min_avg = feb_total.groupby(by=['decade','week'])[temp_filter].mean().reset_index()
decade_week_min_avg = alt.Chart(decade_week_min_avg).mark_rect().encode(
    alt.X('week:N', title="Week"),
    alt.Y('decade:N', title="Decade", sort='descending'),
    alt.Color(f'{temp_filter}:Q', bin = alt.Bin(maxbins=20), scale={"scheme":"purples"})
).properties(
    width = 1000,
    height = 500,
    title = 'February Average Weekly Temps Across Decades'
)
decade_week_min_avg

decade_monthly_min_avg = feb_total.groupby(by='decade')[temp_filter].mean().reset_index()
decade_monthly_min_avg = alt.Chart(decade_monthly_min_avg).mark_rect().encode(
    alt.Y('decade:N', sort='descending'),
    alt.Color(f'{temp_filter}:Q', bin=alt.Bin(maxbins=20), scale={'scheme':'purples'})
).properties(
    width=1000,
    height=500,
    title='February Average Monthly Temps Across Decades'
)
decade_monthly_min_avg

feb_snowfall_total = pd.concat([hailey1,hailey2])
feb_snowfall_total['decade'] = feb_snowfall_total['DATE'].dt.year // 10 * 10
feb_snowfall_total['week'] = 1 + ((feb_snowfall_total['DATE'].dt.day - 1) // 7)
feb_snowfall_total['day'] = feb_snowfall_total['DATE'].dt.day

february_precip_daily_avg = feb_snowfall_total.groupby(by=['decade','day'])['SNOW'].mean().reset_index()
february_precip_daily_avg = alt.Chart(february_precip_daily_avg).mark_rect().encode(
alt.X('day:N', title = 'Day'),
alt.Y('decade:N', sort='descending', title='Decade'),
alt.Color('SNOW:Q', bin=alt.Bin(maxbins=25), scale={'scheme':'reds'})
).properties(
    width = 1000,
    height = 500,
    title = "February Snowfall Daily Averages Across Decades"
)
february_precip_daily_avg

feb_master = temps[temps['DATE'].dt.month == 2]
feb_master['decade'] = feb_master['DATE'].dt.year // 10 * 10
feb_master['week'] = 1+ ((feb_master['DATE'].dt.day - 1) // 7)
feb_master['day'] = feb_master['DATE'].dt.day


#############################
####### Snowfall ############
#############################

feb_master_snowfall_daily_avg = feb_master.groupby(by=['decade','day'])['SNOW'].mean().reset_index()
feb_master_snowfall_daily_avg = alt.Chart(feb_master_snowfall_daily_avg).mark_rect().encode(
    alt.X('day:N', title="Day"),
    alt.Y('decade:N', title="Decade", sort='descending'),
    alt.Color('SNOW:Q', bin=alt.Bin(maxbins=50), scale={'scheme':'reds'})
).properties(
    width=1000,
    height=500,
    title="February Daily Snowfall Across Decades"
)
feb_master_snowfall_daily_avg

feb_master_snowfall_weekly_avg = feb_master.groupby(by=['week','decade'])['SNOW'].mean().reset_index()
feb_master_snowfall_weekly_avg = alt.Chart(feb_master_snowfall_weekly_avg).mark_rect().encode(
    alt.X('week:N', title="Week"),
    alt.Y('decade:N', title="Decade", sort='descending'),
    alt.Color('SNOW:Q', bin=alt.Bin(maxbins=50), scale={'scheme':'reds'})
).properties(
    width=1000,
    height=500,
    title="February Weekly Snowfall Across Decades"
)
feb_master_snowfall_weekly_avg

feb_master_snowfall_avg = feb_master.groupby(by=['decade'])['SNOW'].mean().reset_index()
feb_master_snowfall_avg = alt.Chart(feb_master_snowfall_avg).mark_rect().encode(
    alt.Y('decade:N', title="Decade", sort='descending'),
    alt.Color('SNOW:Q', bin=alt.Bin(maxbins=50), scale={'scheme':'reds'})
).properties(
    width=1000,
    height=500,
    title="February Snowfall Across Decades"
)
feb_master_snowfall_avg


#############################
####### Precipitation #######
#############################

feb_master_precip_daily_avg = feb_master.groupby(by=['decade','day'])['PRCP'].mean().reset_index()
feb_master_precip_daily_avg = alt.Chart(feb_master_precip_daily_avg).mark_rect().encode(
    alt.X('day:N', title="Day"),
    alt.Y('decade:N', title="Decade", sort='descending'),
    alt.Color('PRCP:Q', bin=alt.Bin(maxbins=50), scale={'scheme':'reds'})
).properties(
    width=1000,
    height=500,
    title="February Daily Precipitation Across Decades"
)
feb_master_precip_daily_avg

feb_master_precip_weekly_avg = feb_master.groupby(by=['week','decade'])['PRCP'].mean().reset_index()
feb_master_precip_weekly_avg = alt.Chart(feb_master_precip_weekly_avg).mark_rect().encode(
    alt.X('week:N', title="Week"),
    alt.Y('decade:N', title="Decade", sort='descending'),
    alt.Color('PRCP:Q', bin=alt.Bin(maxbins=50), scale={'scheme':'reds'})
).properties(
    width=1000,
    height=500,
    title="February Weekly Precipitation Across Decades"
)
feb_master_precip_weekly_avg

feb_master_precip_avg = feb_master.groupby(by=['decade'])['PRCP'].mean().reset_index()
feb_master_precip_avg = alt.Chart(feb_master_precip_avg).mark_rect().encode(
    alt.Y('decade:N', title="Decade", sort='descending'),
    alt.Color('PRCP:Q', bin=alt.Bin(maxbins=50), scale={'scheme':'blues'})
).properties(
    width=1000,
    height=500,
    title="February Precipitation Across Decades"
)
feb_master_precip_avg


#######################################
##### Yearly Snow Totals Barchart #####
#######################################

feb_master['year'] = feb_master['DATE'].dt.year
feb_master_snowfall_yearly_total = feb_master.groupby(by=['year', 'STATION'])['SNOW'].sum().reset_index()

bars = alt.Chart(feb_master_snowfall_yearly_total).mark_bar().encode(
    alt.Y('SNOW:Q'),
    alt.X('year:O', title="Year"),
    alt.Color('STATION:N')
)

rolling_avg = alt.Chart(feb_master_snowfall_yearly_total).mark_line(color='red').transform_window(
    rolling_mean = 'mean(SNOW)',
    frame = [-5,5]
).encode(
    x='year:O',
    y='rolling_mean:Q'
)

feb_master_snowfall_yearly_total = (bars + rolling_avg).properties(
    width=1000,
    height=500,
    title="Yearly Snowfall Totals"
)
feb_master_snowfall_yearly_total


#######################################
#### Yearly Precip Totals Barchart ####
#######################################

feb_master['year'] = feb_master['DATE'].dt.year[feb_master['PRCP'] > 0]
precip_master = feb_master[feb_master['DATE'].dt.year > 1981]
feb_master_precip_yearly_total = precip_master.groupby(by=['year', 'STATION'])['PRCP'].sum().reset_index()

bars = alt.Chart(feb_master_precip_yearly_total).mark_bar().encode(
    alt.Y('PRCP:Q'),
    alt.X('year:O', title="Year"),
    alt.Color('STATION:N')
)

rolling_avg = alt.Chart(feb_master_precip_yearly_total).mark_line(color='red').transform_window(
    rolling_mean = 'mean(PRCP)',
    frame = [-5,5]
).encode(
    x='year:O',
    y='rolling_mean:Q'
)

feb_master_precip_yearly_total = (bars + rolling_avg).properties(
    width=1000,
    height=500,
    title="Yearly Precipitation Totals"
)
feb_master_precip_yearly_total


#######################################
###### Decade Max Min Temp Chart ######
#######################################

tmin_master = feb_master.groupby(by=['day','decade'])['TMIN'].mean().reset_index()
tmax_master = feb_master.groupby(by=['day','decade'])['TMAX'].mean().reset_index()

tmin_master

base = alt.Chart(tmin_master).properties(width = 900, height = 500)

line = base.mark_line().encode(
    alt.X('week:O', title="Week"),
    alt.Y('TMIN:Q', title="Min Temp"),
    color='decade:N'
)
line


#######################################
####### Min Max Temp Comparison #######
#######################################
current_decade = feb_master[feb_master['DATE'].dt.year > 2019]

decade_choice = st.sidebar.select_slider("Choose a Decade to Compare", options=['2010','2000','1990','1980','1970','1960', '1950','1940','1930'])
other_decade = feb_master[feb_master['decade'] == int(decade_choice)]

comparison = pd.concat([current_decade, other_decade])
comparison_tmin = comparison.groupby(by=['decade', 'day'])['TMIN'].mean().reset_index()
comparison_tmax = comparison.groupby(by=['decade', 'day'])['TMAX'].mean().reset_index()
tmin_line = alt.Chart(comparison_tmin).mark_line().encode(
    alt.X('day:N'),
    alt.Y('TMIN:Q'),
    alt.Color('decade:N')
)

tmax_line = alt.Chart(comparison_tmax).mark_line().encode(
    alt.X('day:N'),
    alt.Y('TMAX:Q'),
    alt.Color('decade:N')
)

t = (tmin_line + tmax_line).properties(
    width = 1000,
    height = 500,
    title = "Comparing 2020 Temps to Other Decades"
)
t

#######################################
##### Min Max Snowfall Comparison #####
#######################################
current_decade = feb_master[feb_master['DATE'].dt.year > 2019]
other_decade = feb_master[feb_master['decade'] == int(decade_choice)]

comparison = pd.concat([current_decade, other_decade])
comparison_snowfall = comparison.groupby(by=['decade', 'day'])['SNOW'].mean().reset_index()
snow_line = alt.Chart(comparison_snowfall).mark_point(color='blue').encode(
    alt.X('day:N'),
    alt.Y('SNOW:Q'),
    alt.Color('decade:N'),
    alt.Size('SNOW:Q'),
).properties(
    width=1000,
    height=500,
    title="Comparing 2020 Snowfall to Other Decades"
)
snow_line


#######################################
##### Min Max Snowfall Comparison #####
#######################################
current_year = feb_master[feb_master['DATE'].dt.year == 2022]
year_choice = st.sidebar.select_slider("Select Year for Comparison", np.arange(1933,2021))
other_year = feb_master[feb_master['year'] == int(year_choice)]

comparison2 = pd.concat([current_year, other_year])
comparison2
comparison2_snowfall = comparison2.groupby(by=['year', 'day'])['SNOW'].sum().reset_index()
comparison2_snowfall
snow_line2 = alt.Chart(comparison2_snowfall).mark_point().encode(
    alt.X('day:N'),
    alt.Y('SNOW:Q'),
    alt.Color('year:N'),
).properties(
    width=1000,
    height=500,
    title="Comparing 2022 Snowfall to Other Years"
)
snow_line2


#######################################
##### Min Max Snowfall Comparison #####
#######################################
current_year = feb_master[feb_master['DATE'].dt.year == 2022]
other_year = feb_master[feb_master['year'] == int(year_choice)]

comparison3 = pd.concat([current_year, other_year])
comparison3
comparison3_snowfall = comparison3.groupby(by=['year', 'day'])['SNWD'].mean().reset_index()
comparison3_snowfall
snow_line3 = alt.Chart(comparison3_snowfall).mark_line().encode(
    alt.X('day:N'),
    alt.Y('SNWD:Q'),
    alt.Color('year:N'),
).properties(
    width=1000,
    height=500,
    title="Comparing 2022 Snow Depth to Other Years"
)
snow_line3
