import pandas as pd
import streamlit as st
import datetime
import plotly.express as px

try:
    df = pd.read_csv('orderdates.csv')
except FileNotFoundError:
    st.error("CSV dosyası bulunamadı!")
    st.stop()

df['Siparis Tarihi'] = pd.to_datetime(df['Siparis Tarihi'], errors='coerce')

st.title("Sipariş Analizi")

start_date = st.date_input(
    "Başlangıç Tarihi",
    min_value=df['Siparis Tarihi'].min().date(),
    max_value=df['Siparis Tarihi'].max().date(),
    value=datetime.date(2024, 1, 1)
)

end_date = st.date_input(
    "Bitiş Tarihi",
    min_value=df['Siparis Tarihi'].min().date(),
    max_value=df['Siparis Tarihi'].max().date(),
    value=datetime.date(2024, 12, 31)
)

filtered_df = df[(df['Siparis Tarihi'] >= pd.to_datetime(start_date)) &
                 (df['Siparis Tarihi'] <= pd.to_datetime(end_date))]

if filtered_df.empty:
    st.warning("Seçilen tarihler arasında sipariş bulunmamaktadır.")
    st.stop()

filtered_df = filtered_df.copy()
filtered_df.loc[:, 'hour_interval'] = (
    filtered_df['Siparis Tarihi'].dt.strftime('%H:00 - ') +
    (filtered_df['Siparis Tarihi'] + pd.Timedelta(hours=1)).dt.strftime('%H:00')
)

# Define the mapping from English to Turkish day names
day_name_mapping = {
    'Monday': 'Pazartesi',
    'Tuesday': 'Salı',
    'Wednesday': 'Çarşamba',
    'Thursday': 'Perşembe',
    'Friday': 'Cuma',
    'Saturday': 'Cumartesi',
    'Sunday': 'Pazar'
}

# Convert the 'day_of_week' column to Turkish day names
filtered_df['day_of_week'] = filtered_df['Siparis Tarihi'].dt.day_name().map(day_name_mapping)

# Define the correct order for the days of the week in Turkish
day_order_tr = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']

# Convert the 'day_of_week' column to a categorical type with the specified order
filtered_df['day_of_week'] = pd.Categorical(
    filtered_df['day_of_week'],
    categories=day_order_tr,
    ordered=True
)

pivot_table = filtered_df.pivot_table(
    index='hour_interval',
    columns='day_of_week',
    values='Sip Mik',
    aggfunc='sum',
    fill_value=0
)

week_total = pivot_table.sum().sum()
pivot_table_normalized = (pivot_table / week_total) * 100

total_percent = pivot_table_normalized.sum(axis=0)

st.markdown("<h2 style='text-align: center;'>Haftalık Saatlik Sipariş Dağılımı</h2>", unsafe_allow_html=True)

fig = px.bar(pivot_table_normalized,
             x=pivot_table_normalized.columns,
             y=pivot_table_normalized.index,
             orientation='h',
             title=" ",
             labels={"value": "% Dağılım", "hour_interval": "Saatlik Aralık", "day_of_week": "Haftanın Günü"})

fig.update_layout(
    xaxis_title="Yüzdelik Oran %",
    yaxis_title="Saatlik Aralık",
    title_x=0.5,
    title_y=0.95,
    barmode='stack',
    bargap=0.2
)

st.plotly_chart(fig)


# Add the total percentage as a new row in the pivot_table_normalized DataFrame
pivot_table_normalized.loc['Total Week %'] = pivot_table_normalized.sum(axis=0)
pivot_table_normalized.loc['Total Week %', :] = total_percent

# Display the updated table
st.markdown("<h2 style='text-align: center;'>Her Gün İçin Toplam % ve Haftalık Toplam %</h2>", unsafe_allow_html=True)
st.table(pivot_table_normalized)