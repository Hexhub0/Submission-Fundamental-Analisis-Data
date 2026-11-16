import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide"
)

st.title("🚲 Bike Sharing Analysis Dashboard")
st.markdown("""
Dashboard ini digunakan untuk menganalisis pola penyewaan
sepeda berdasarkan periode waktu dan kondisi cuaca
selama tahun 2011 hingga 2012.
""")

@st.cache_data
def load_data():
    data_path = Path(__file__).parent / "main_data.csv"
    df = pd.read_csv(data_path)

    df["dteday"] = pd.to_datetime(df["dteday"])
    df["year"] = df["yr"].map({0: 2011, 1: 2012})
    df["weather_label"] = df["weathersit"].map({
        1: "Clear",
        2: "Mist + Cloudy",
        3: "Light Rain/Snow",
        4: "Heavy Rain/Snow"
    })
    df["month"] = df["dteday"].dt.month
    return df

df = load_data()

st.sidebar.header("Filter Data")

selected_year = st.sidebar.multiselect(
    "Pilih Tahun",
    options=sorted(df["year"].dropna().unique()),
    default=sorted(df["year"].dropna().unique())
)

selected_weather = st.sidebar.multiselect(
    "Pilih Kondisi Cuaca",
    options=sorted(df["weather_label"].dropna().unique()),
    default=sorted(df["weather_label"].dropna().unique())
)

filtered_df = df[
    (df["year"].isin(selected_year)) &
    (df["weather_label"].isin(selected_weather))
]

if filtered_df.empty:
    st.warning("Tidak ada data sesuai filter yang dipilih.")
    st.stop()

st.subheader("Ringkasan Data Penyewaan")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Penyewaan",
    f"{filtered_df['cnt'].sum():,.0f}"
)

col2.metric(
    "Rata-rata Penyewaan/Hari",
    f"{filtered_df['cnt'].mean():,.0f}"
)

col3.metric(
    "Jumlah Hari",
    f"{len(filtered_df):,}"
)

col4.metric(
    "Penyewaan Tertinggi",
    f"{filtered_df['cnt'].max():,.0f}"
)

st.divider()

st.subheader("1. Perkembangan Penyewaan Sepeda per Bulan")

monthly = (
    filtered_df.groupby(["year", "month"])
    .agg(average_rentals=("cnt", "mean"))
    .reset_index()
)

monthly["date"] = pd.to_datetime(
    monthly["year"].astype(int).astype(str)
    + "-"
    + monthly["month"].astype(str)
    + "-01"
)

monthly = monthly.sort_values("date")

fig1, ax1 = plt.subplots(figsize=(12, 5))

sns.lineplot(
    data=monthly,
    x="date",
    y="average_rentals",
    marker="o",
    ax=ax1
)

ax1.set_title("Rata-rata Penyewaan Sepeda per Bulan")
ax1.set_xlabel("Bulan dan Tahun")
ax1.set_ylabel("Rata-rata Penyewaan per Hari")

plt.xticks(rotation=45)
plt.tight_layout()

st.pyplot(fig1)
plt.close(fig1)

st.subheader("2. Penyewaan Sepeda Berdasarkan Kondisi Cuaca")

weather = (
    filtered_df.groupby("weather_label")
    .agg(average_rentals=("cnt", "mean"))
    .reset_index()
    .sort_values("average_rentals", ascending=False)
)

fig2, ax2 = plt.subplots(figsize=(10, 5))

sns.barplot(
    data=weather,
    x="weather_label",
    y="average_rentals",
    ax=ax2
)

ax2.set_title("Rata-rata Penyewaan Berdasarkan Cuaca")
ax2.set_xlabel("Kondisi Cuaca")
ax2.set_ylabel("Rata-rata Penyewaan per Hari")

plt.xticks(rotation=20)
plt.tight_layout()

st.pyplot(fig2)
plt.close(fig2)

st.subheader("3. Data Penyewaan Sepeda")

st.dataframe(
    filtered_df[
        [
            "dteday",
            "year",
            "weather_label",
            "casual",
            "registered",
            "cnt"
        ]
    ],
    use_container_width=True
)

st.caption("Dataset: Bike Sharing Dataset (2011–2012).")