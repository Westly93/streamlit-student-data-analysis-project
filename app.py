from datetime import date
import streamlit as st
import plotly.express as px
import pandas as pd
from streamlit_extras.metric_cards import style_metric_cards


st.set_page_config(layout="wide", page_icon=":bar_chart:",
                   page_title="Student Registration Statistics")
hide_streamlit_styles = """
<style>
#MainMenu{
    visibility: hidden;
}
footer{
    visibility: hidden;
}
header{
    visibility: hidden;
}
</style>
"""

st.markdown(hide_streamlit_styles, unsafe_allow_html=True)
st.title(":bar_chart: Student Registration Dashboard")


@st.cache_data
def load_dataframe():
    data = pd.read_csv("./data/registrations.csv")
    data["year"] = data["period"].str.extract(r'(\d{4})')
    data["year"] = data["year"].fillna(0)
    data["year"] = data['year'].astype('int64')
    data = data[~data["period"].astype("str").str.contains("Manicaland")]
    data["level"] = data.academic_year.astype(
        "str")+"."+data.semester.astype("str")
    return data


def get_active_period(dataframe):
    current_year = pd.to_datetime("today").year
    if current_year in dataframe["period"]:
        dataframe = dataframe[dataframe['period'].str.contains(
            str(current_year)) & dataframe['period'].str.contains('Third Quarter')]
        return dataframe
    else:
        dataframe = dataframe[dataframe['period'].str.contains(
            str(current_year)) & dataframe['period'].str.contains('Third Quarter')]
        return dataframe


def new_column_age(df):
    df["dob"] = pd.to_datetime(df["dob"])
    current_date = pd.to_datetime(date.today())
    df['age'] = ((current_date - df['dob']).dt.days / 365).astype('int64')
    # df["age"] = df.age.astype("int64")
    return df


data = load_dataframe()

df = get_active_period(data)
attendance_type = data.attendance_type.unique().tolist()
periods = data.period.unique().tolist()[-16:]


with st.expander("View Dataset"):
    show_data = st.dataframe(data)

col1, col2, col3, col4 = st.columns(4, gap='small')

with col1:
    st.info('Active Students', icon="💰")
    st.metric(label="Students in thousands",
              value=f"{df.registration_number.nunique():,.0f}k")

with col2:
    st.info('Active Male Students', icon="💰")
    st.metric(label="Students in thousands",
              value=f'{df[df.gender == "male"].registration_number.nunique():,.0f}k')
with col3:
    st.info('Active Female Students', icon="💰")
    st.metric(label="Students in thousands",
              value=f"{df[df.gender == 'female'].registration_number.nunique():,.0f}k")
with col4:
    st.info('Number of Graduates', icon="💰")
    st.metric(label="Students in thousands", value=100)
style_metric_cards(background_color="#33ddff", border_left_color="#686664",
                   border_color="#000000", box_shadow="#F71938")


def graphs():
    # distribution by faculty
    distribution_by_faculty = df.groupby(
        by="faculty")['registration_number'].nunique()
    distribution_by_faculty = distribution_by_faculty.reset_index(
        name="Students")
    plot1 = px.pie(
        distribution_by_faculty,
        values='Students',
        names="faculty",
        color_discrete_sequence=px.colors.sequential.RdBu_r,
        title=f"Student Distribution By faculty {max(data.year.unique().tolist())}"
    )
    st.plotly_chart(plot1, use_container_width=True)
    # Attendance Type Distribution
    attendance_type_distribution = df.groupby(
        by="attendance_type").registration_number.nunique()
    attendance_type_distribution = attendance_type_distribution.reset_index(
        name="Students")
    plot4 = px.pie(
        attendance_type_distribution,
        names='attendance_type',
        values="Students",
        template="plotly_white",
        title="Attendance Type Distribution",
        color_discrete_sequence=px.colors.sequential.RdBu_r
    )
    st.plotly_chart(plot4, use_container_width=True)
    # distribution by level
    data_grouped = df.groupby(by="level").registration_number.nunique()
    data_grouped = data_grouped.reset_index(name="Students")
    plot2 = px.bar(
        data_grouped,
        x='level',
        y="Students",
        template="plotly_white",
        color_discrete_sequence=px.colors.sequential.Bluyl_r,
        title="Distribution by Level"
    )
    st.plotly_chart(plot2, use_container_width=True)
    # Distribution by age
    aged_data = new_column_age(df)
    age_distribution = aged_data.groupby(
        by="age").registration_number.nunique()
    age_distribution = age_distribution.reset_index(name="Students")
    plot3 = px.bar(
        age_distribution,
        x='age',
        y="Students",
        template="plotly_white",
        title="Distribution by Age",
        color_discrete_sequence=px.colors.sequential.Bluyl_r
    )
    st.plotly_chart(plot3, use_container_width=True)

    # distribution by year
    st.markdown("---")
    years = st.slider(
        "Years",
        min_value=min(data.year.unique().tolist()[1:]),
        max_value=max(data.year.unique().tolist()),
        value=(min(data.year.unique().tolist()[1:]), max(
            data.year.unique().tolist())),
    )

    mask = data.year.between(*years)
    data_grouped = data[mask].groupby(
        by="year")["registration_number"].nunique()
    data_grouped = data_grouped.reset_index(name="Students")
    data_grouped["year"] = data_grouped["year"].astype("str")
    plot = px.bar(
        data_grouped,
        x='year',
        y="Students",
        template="plotly_white",
        color_discrete_sequence=px.colors.sequential.Bluyl_r,
        title=f"Student Distribution {years}"
    )
    plot.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=data_grouped['year'],
            ticktext=data_grouped['year'].astype('str'),

        ),
        xaxis_tickangle=45
    )
    st.plotly_chart(plot, use_container_width=True)


graphs()
