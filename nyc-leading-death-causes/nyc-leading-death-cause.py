import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="NYC Leading Causes of Death", layout="wide")
st.title("📊 NYC Leading Causes of Death Dashboard")

df = pd.read_csv(
    r"C:\Users\abdan\Downloads\streamlit-dashboard\data\New_York_City_Leading_Causes_of_Death_20250923.csv",
    na_values="."
)

for col in ["Leading Cause", "Sex", "Race Ethnicity"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

if "Sex" in df.columns:
    df["Sex"] = df["Sex"].astype(str).str.strip()
    df["Sex"] = df["Sex"].replace({
        "F": "Female", "M": "Male",
        "f": "Female", "m": "Male",
        "female": "Female", "male": "Male",
        "FEMALE": "Female", "MALE": "Male"
    })

    df["Sex"] = df["Sex"].apply(lambda x: "Female" if isinstance(x, str) and x.upper().startswith("F")
                                         else ("Male" if isinstance(x, str) and x.upper().startswith("M")
                                               else x))

if "Race Ethnicity" in df.columns:
    df["Race Ethnicity"] = df["Race Ethnicity"].replace({
        "Black Non-Hispanic": "Non-Hispanic Black",
        "White Non-Hispanic": "Non-Hispanic White",
        "Other Race/ Ethnicity": "Other Race/Ethnicity"
    })

if "Year" in df.columns:
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")

for col in ["Deaths", "Death Rate", "Age Adjusted Death Rate"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce")

years = []
if "Year" in df.columns:
    years = sorted([int(y) for y in df["Year"].dropna().unique()])
selected_year = st.sidebar.selectbox("Select a Year", years)

sex_options = ["All"]
if "Sex" in df.columns:
    sex_options += sorted(df["Sex"].dropna().unique().tolist())
selected_sex = st.sidebar.selectbox("Select a Sex", sex_options)

race_options = ["All"]
if "Race Ethnicity" in df.columns:
    race_options += sorted(df["Race Ethnicity"].dropna().unique().tolist())
selected_race = st.sidebar.selectbox("Select a Race/Ethnicity", race_options)

filtered_df = df.copy()
if "Year" in df.columns:
    filtered_df = filtered_df[filtered_df["Year"] == selected_year]

if selected_sex != "All":
    filtered_df = filtered_df[filtered_df["Sex"] == selected_sex]

if selected_race != "All":
    filtered_df = filtered_df[filtered_df["Race Ethnicity"] == selected_race]

st.write(f"### Filtered Data ({selected_year}, {selected_sex}, {selected_race}) — {len(filtered_df)} rows")
st.dataframe(filtered_df.head(50))

if filtered_df.empty:
    st.warning("No rows match these filters. Tip: open 'Debug values' below to see exactly what values exist for Sex and Race.")

numeric_cols = [c for c in ["Deaths", "Death Rate", "Age Adjusted Death Rate"] if c in filtered_df.columns]
for col in numeric_cols:
    st.write(f"### {col} Summary")
    st.write(filtered_df[col].describe())

    fig, ax = plt.subplots()
    filtered_df[col].dropna().hist(ax=ax, bins=20)
    ax.set_title(f"Distribution of {col} — {selected_year}")
    st.pyplot(fig)

if "Leading Cause" in filtered_df.columns and "Deaths" in filtered_df.columns and not filtered_df["Deaths"].dropna().empty:
    st.write("### Top Causes of Death (by Deaths)")
    top_causes = (
        filtered_df.groupby("Leading Cause")["Deaths"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    st.bar_chart(top_causes)
with st.expander("Debug values (unique entries)"):
    if "Sex" in df.columns:
        st.write("Sex unique:", sorted(df["Sex"].dropna().unique().tolist()))
    if "Race Ethnicity" in df.columns:
        st.write("Race/Ethnicity unique:", sorted(df["Race Ethnicity"].dropna().unique().tolist()))
    if "Year" in df.columns:
        st.write("Years available:", years)
