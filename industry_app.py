import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Finnish Industry Turnover per Employee", layout="wide")

st.title("Finnish Industry Turnover per Employee")
st.caption("Comparing turnover generated per employee across Finnish industries")


@st.cache_data
def load_data():
    df = pd.read_csv("industry_data.csv")
    return df


df = load_data()

# ---------- Filter ----------
st.sidebar.header("Filter")
industries = st.sidebar.multiselect(
    "Industry",
    options=sorted(df["industry"].unique()),
    default=sorted(df["industry"].unique())
)
filtered = df[df["industry"].isin(industries)]

# ---------- KPI row ----------
col1, col2, col3 = st.columns(3)
col1.metric("Industries shown", len(filtered))
col2.metric("Median turnover per employee", f"EUR {filtered['turnover_per_employee_eur'].median():,.0f}")
col3.metric("Combined personnel", f"{filtered['personnel_thousand'].sum():,.0f}k")

st.divider()

# ---------- Chart 1: turnover per employee ranking ----------
st.subheader("Turnover per employee by industry")
st.caption("Total industry turnover divided by number of people employed in that industry.")

fig1 = px.bar(
    filtered.sort_values("turnover_per_employee_eur", ascending=False),
    x="industry", y="turnover_per_employee_eur",
    labels={"turnover_per_employee_eur": "Turnover per employee (EUR)", "industry": ""},
)
fig1.update_layout(margin=dict(t=10, b=10))
st.plotly_chart(fig1, use_container_width=True)

# ---------- Chart 2: personnel vs turnover per employee ----------
st.subheader("Workforce size and turnover per employee")
st.caption("Whether industries employing more people also tend to generate more turnover per employee.")

fig2 = px.scatter(
    filtered, x="personnel_thousand", y="turnover_per_employee_eur",
    size="enterprises", hover_name="industry",
    labels={"personnel_thousand": "Personnel (thousand)", "turnover_per_employee_eur": "Turnover per employee (EUR)"},
)
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ---------- Key observations ----------
st.subheader("Key observations")

if len(filtered) >= 2:
    top_turnover = filtered.loc[filtered["turnover_per_employee_eur"].idxmax()]
    top_personnel = filtered.loc[filtered["personnel_thousand"].idxmax()]
    corr = filtered["personnel_thousand"].corr(filtered["turnover_per_employee_eur"])

    if abs(corr) < 0.3:
        corr_note = "weak"
    elif abs(corr) < 0.6:
        corr_note = "moderate"
    else:
        corr_note = "strong"

    st.markdown(f"""
- **{top_turnover['industry']}** has the highest turnover per employee (EUR {top_turnover['turnover_per_employee_eur']:,.0f}) in this selection.
- **{top_personnel['industry']}** employs the most people ({top_personnel['personnel_thousand']:,.0f} thousand) in this selection.
- The relationship between workforce size and turnover per employee is {corr_note} in this small sample.
""")
else:
    st.caption("Select at least two industries to see comparative observations.")

st.divider()

# ---------- Data table ----------
st.subheader("Underlying data")
st.dataframe(
    filtered.rename(columns={
        "industry": "Industry", "enterprises": "Enterprises",
        "personnel_thousand": "Personnel (thousand)", "turnover_eur_million": "Turnover (EUR million)",
        "turnover_per_employee_eur": "Turnover per employee (EUR)"
    }),
    use_container_width=True, hide_index=True
)

st.caption("Source: Finland in Figures 2024, based on Statistics Finland enterprise statistics.")
