import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="superstore", page_icon=":Bar_chart:", layout="wide")

st.title(":bar_chart: My superstore EDA Application")
st.markdown("<style>div.block-container{padding-top:1rem;</style>", unsafe_allow_html=True)

f1 = st.file_uploader(":file_folder: upload a file", type=(["csv","txt","xlsx","xls"]))
if f1 is not None:
    filename = f1.name
    st.write(filename, encoding = "ISO-8859-1")
    df = pd.read_csv(filename)
else:
    os.chdir(r"C:\Users\varte\OneDrive\Desktop\Data Science Course\Class projects")
    df = pd.read_csv("superstore.csv", encoding = "ISO-8859-1")
col1, col2, = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])

# Getting the min and max date
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("end Date", endDate))

df = df[(df["Order Date"]>= date1) & (df["Order Date"]<= date2)].copy()

# create for Region
st.sidebar.header("Choose your filter:")
Region = st.sidebar.multiselect("Pick your region", df["Region"].unique())
if not Region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(Region)]

# Create for States
state = st.sidebar.multiselect("Pick your state", df2["State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

# Create for city

city = st.sidebar.multiselect("Pick your city", df3["City"].unique())

# Filter the data based on Region, state and city

if not Region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(Region)]
elif not Region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[df["State"].isin(state) & df["City"].isin(city)]

elif Region and city:
    filtered_df = df3[df["State"].isin(Region) & df["City"].isin(city)]
elif Region and state:
    filtered_df = df3[df["State"].isin(Region) & df["State"].isin(city)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[df3["Region"].isin(Region) & df3["State"].isin(state) & df3["City"].isin(City)]

Category_df = filtered_df.groupby(by=["Category"], as_index = False)["Sales"].sum()
with col1:
    st.subheader("Sales Category")
    fig = px.bar(Category_df, x = "Category", y = "Sales", text=["${:,.2f}".format(x) for x in Category_df["Sales"]],
                 template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height =200)

with col2:
    st.subheader("Sales by Region")
    fig = px.pie(filtered_df, values="Sales",names="Region", hole = 0.5)
    fig.update_traces(text= filtered_df["Region"], textposition="outside")
    st.plotly_chart(fig,use_container_width=200)

col1, col2 = st.columns(2)

with col1:
    with st.expander("category_viewData"):
        st.write(Category_df.style.background_gradient(cmap="Blues"))
        csv = Category_df.to_csv(index= False).encode("utf-8")
        st.download_button("Download Data", data= csv,file_name = "category.csv", mime = "text/csv",
                           help="click to download the CSV / text file")
with col2:
    with st.expander("Region_viewData"):
        region = filtered_df.groupby(by= "Region", as_index=False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap= "Oranges"))
        csv = region.to_csv(index=False).encode("utf-8")
        st.download_button("Download Data", data=csv,file_name="Region.csv", mime ="text/csv",
                           help="click to download the CSV / text file")

filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader("Time Series Analysis")

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y: %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x="month_year", y="Sales", labels={"Sales": "Amount"}, height=500, width=1000, template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button("Download Data", data=csv, file_name="TimeSeries.csv", mime="text/csv")

# create a treem based on Region, Category, sub-Category
st.subheader("Hierarchical View of Sales using TreeMap")
fig3 = px.treemap(filtered_df,path=["Region", "Category", "Sub-Category"], values="Sales", hover_data=["Sales"], color="Sub-Category")
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3,use_container_width=True)

chart1, chart2 = st.columns((2))

with chart1:
    st.subheader("Segment of Sales")
    fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
    fig.update_traces(text = filtered_df["Segment"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

with chart2:
    st.subheader("Category of Sales")
    fig = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
    fig.update_traces(text = filtered_df["Category"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

import plotly.figure_factory as ff
st.subheader(":point_right: Month of Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample = df[0:5][["Region","State", "City", "Category","Sales","Profit","Quantity"]]
    fig = ff.create_table(df_sample, colorscale="cividis")
    st.plotly_chart(fig,use_container_width=True)

    st.markdown("Month of Sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    Sub_Category_year = pd.pivot_table(data=filtered_df,values="Sales",index=["Sub-Category"], columns="month")
    st.write(Sub_Category_year.style.background_gradient(cmap="Blues"))

# create  a scatter plot

date1 = px.scatter(filtered_df, x="Sales", y = "Profit", size="Quantity")
date1["layout"].update(title="Relationship between Sales and Profits using Scatter plot",
                       titlefont=dict(size=20), xaxis=dict(title="Sales", titlefont=dict(size=19)),
                       yaxis=dict(title="Profit", titlefont=dict(size=19)))
st.plotly_chart(date1,use_container_width=True)

with st.expander("View Date"):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Oranges"))

# Download Original DataSet
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Download Original Data", data= csv, file_name="Data.csv", mime="text/csv")




























