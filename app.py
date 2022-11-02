import pandas as pd                 # pip install pandas openpyxl
import plotly.express as px         # pip install plotly-express
import plotly.graph_objects as go
import streamlit as st              # pip install streamlit
import calendar

st.set_page_config(
    page_title = 'PV Production',
    page_icon = '☀️',
    layout = 'wide'
)

with open('main.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

df = pd.read_csv('PV.csv')

df.columns = df.columns.str.replace(' ', '_')
df['Date_and_time'] = pd.to_datetime(df['Date_and_time'], format = '%Y-%m-%dT%H:%M:%S')
df["Total_production"] = pd.to_numeric(df["Total_production"]) / 1000
df["Total_consumption"] = pd.to_numeric(df["Total_consumption"]) / 1000
df["Own_consumption"] = pd.to_numeric(df["Own_consumption"]) / 1000
df["Energy_to_grid"] = pd.to_numeric(df["Energy_to_grid"]) / 1000
df["Energy_from_grid"] = pd.to_numeric(df["Energy_from_grid"]) / 1000
df['Year'] = df['Date_and_time'].dt.year
df['Month'] = df['Date_and_time'].dt.month.apply(lambda x: calendar.month_name[x])

pd.set_option('display.max_rows', None)


# ----- DAILY OVERVIEW -----
st.title("Daily Overview")

col_1, col_2, col_3 = st.columns(3)
with col_1:
    st.markdown('##### Average solar production')
    avg_solar_production = int(df['Total_production'].mean())
    st.markdown(f'{avg_solar_production}kWh')

with col_2:
    st.markdown('##### Average solar consumption')
    avg_solar_consumption = int(df['Own_consumption'].mean())
    st.markdown(f"{avg_solar_consumption}kWh")
    st.markdown('##### Average energy from the grid')
    avg_energy_from_grid = int(df['Energy_from_grid'].mean())
    st.markdown(f'{avg_energy_from_grid}kWh')
    st.markdown('##### Average total consumption')
    avg_total_consumption = int(df['Total_consumption'].mean())
    st.markdown(f'{avg_total_consumption}kWh')

with col_3:
    st.markdown('##### Average energy to the grid')
    avg_energy_to_grid = int(df['Energy_to_grid'].mean())
    st.markdown(f'{avg_energy_to_grid}kWh')

st.write('#')



# ----- TOTAL ENERGY -----
st.title("Total Energy")

total_consumption = int(df['Total_consumption'].sum())
total_energy_from_grid = int(df['Energy_from_grid'].sum())
total_energy_to_grid = int(df['Energy_to_grid'].sum())
total_solar_production = int(df['Total_production'].sum())
total_solar_consumption = int(df['Own_consumption'].sum())

labels_production = ["Total solar consumption", "Total energy to the grid"]
values_production = [total_solar_consumption, total_energy_to_grid]
production_grph = [go.Pie(
    name = 'Total_Production',
    labels = labels_production,
    values = values_production,
    title = f'Total Production <br>{total_solar_production}kWh</br>',
    pull = [0.12, 0],
    hovertemplate = '%{label}<br>%{value}kWh</br><extra></extra>'
)]

labels_consumption = ["Total solar consumption", "Total energy from the grid"]
values_consumption = [total_solar_consumption, total_energy_from_grid]
consumption_grph = [go.Pie(
    name = 'Total_Consumption',
    labels = labels_consumption,
    values = values_consumption,
    title = f'Total Consumption <br>{total_consumption}kWh</br>',
    pull = [0.12, 0],
    hovertemplate = '%{label}<br>%{value}kWh</br><extra></extra>'
)]

col_11, col_22 = st.columns(2)
with col_11:
    st.plotly_chart(production_grph, use_container_width = True)

with col_22:
    st.plotly_chart(consumption_grph, use_container_width = True)

st.write('#')



# ----- PV PRODUCTION -----
st.title("PV Production")

estimate_10kwh_output = {
    'Month':['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
    'Year':['Estimate', 'Estimate', 'Estimate', 'Estimate', 'Estimate', 'Estimate', 'Estimate', 'Estimate', 'Estimate', 'Estimate', 'Estimate', 'Estimate'],
    'Total_production':[1711, 1471, 1285, 1021, 756, 632, 719, 971, 1248, 1484, 1637, 1756]
}

estimated_production_df = pd.DataFrame(estimate_10kwh_output)

total_production_df = (
    df.groupby(['Year', 'Month'], as_index = False, sort = False)['Total_production'].sum().rename(columns={'Year':'Year', 'Month':'Month'})
)
total_production_df.style.set_precision(2)
total_production_df['Year'] = total_production_df['Year'].astype(str)
total_production_df['Total_production'] = total_production_df['Total_production'].round(2).astype(int)
# st.dataframe(total_production_df)

merged_production_df = pd.concat([estimated_production_df, total_production_df])
# st.dataframe(merged_production_df)

merged_production_grph = px.line(merged_production_df,
    x = 'Month',
    y = 'Total_production',
    color = 'Year',
    labels = dict(Total_production = 'Total Production (kWh)'),
    markers = True)
merged_production_grph.update_layout(
    plot_bgcolor='#363b4f',
    paper_bgcolor='#363b4f'
)

st.markdown('##### Total Solar Production (kWh)')

ordered_months = df.Month.iloc[
       pd.to_datetime(df.Month, format='%B').argsort()
].unique()
total_month_df = pd.pivot_table(
    df,
    index = 'Year',
    columns = 'Month',
    values = 'Total_production',
    aggfunc = 'sum',
    fill_value = 0).reindex(columns = ordered_months).round(0).astype(int)
st.dataframe(total_month_df)
st.plotly_chart(merged_production_grph)

st.markdown('##### Highest Solar Production (kWh)')
st.markdown('Highest recorded solar production in one day')
max_month_df = pd.pivot_table(
    df,
    index = 'Year',
    columns = 'Month',
    values = 'Total_production',
    aggfunc = 'max',
    fill_value = 0).reindex(columns = ordered_months).round(0).astype(int)
st.dataframe(max_month_df)

st.markdown('##### Average Solar Production (kWh)')
st.markdown('Daily average solar produced')
avg_month_df = pd.pivot_table(
    df,
    index = 'Year',
    columns = 'Month',
    values = 'Total_production',
    aggfunc = 'mean',
    fill_value = 0).reindex(columns = ordered_months).round(0).astype(int)
st.dataframe(avg_month_df)

st.write('#')



# ----- FILTER -----

st.header('Select Filter:')
year = st.selectbox(
    'Select Year',
    options = df['Year'].unique()[::-1],
    index = 0
)
months = st.multiselect(
    'Select Months',
    options = df['Month'].unique(),
    default = df['Month'].unique()
)
query_df = df.query(
    "Year == @year & Month == @months"
)

groupby_query_df = (
    query_df.groupby(by=["Month"], as_index = True, sort = False).sum()
)
groupby_query_df['Month'] = groupby_query_df.index

newnames = {'Own_consumption':'hello'}
query_production_grph = px.bar(
    groupby_query_df,
    x = 'Month',
    y = ['Total_production', 'Own_consumption', 'Energy_to_grid'],
    title = '<b>Production</b>',
    template = "plotly_white",
    labels = {'Own_consumption': 'Solar', },
    barmode = 'group'
)
query_production_grph.update_yaxes(title_text = 'kWh')
query_production_grph.update_layout(
    legend_title = 'Energy usage',
    plot_bgcolor = '#363b4f',
    paper_bgcolor = '#363b4f'
)

query_consumption_grph = px.bar(
    groupby_query_df,
    x = 'Month',
    y = ['Total_consumption', 'Own_consumption', 'Energy_from_grid'],
    title = '<b>Consumption</b>',
    template = 'plotly_white',
    barmode = 'group'
)
query_consumption_grph.update_yaxes(title_text = 'kWh')
query_consumption_grph.update_layout(
    legend_title = 'Energy usage',
    plot_bgcolor = '#363b4f',
    paper_bgcolor = '#363b4f'
)

col_1, col_2 = st.columns(2)
with col_1:
    st.plotly_chart(query_production_grph)

with col_2:
    st.plotly_chart(query_consumption_grph)

st.dataframe(groupby_query_df)



# ----- RAW -----
st.title("RAW")
st.dataframe(df)






# to run type 'streamlit run app.py' in terminal

# setup: https://github.com/streamlit/streamlit/wiki/Installing-in-a-virtual-environment
# ref  : https://www.youtube.com/watch?v=Sb0A9i6d320&ab_channel=CodingIsFun
