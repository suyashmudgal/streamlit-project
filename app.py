import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
from plotly import graph_objects as go
from plotly.subplots import make_subplots



# Streamlit layout settings
st.set_page_config(layout="wide", initial_sidebar_state="expanded", page_title='Startup Analysis')

# Load and clean data
df = pd.read_csv("Startup_clearned.csv")
df.columns = df.columns.str.strip()
df['Investor'] = df['Investor'].astype(str).str.strip()
df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
df['Year'] = df['Date'].dt.year

# ============ Investor POV Function (Untouched) ============
def load_investor_details(investor):
    st.title(f"{investor}")
    investor_df = df[df['Investor'].str.contains(investor, case=False, na=False)]
    last5_df = investor_df.sort_values('Date', ascending=False).head()[['Date', 'Startup', 'vertical', 'City', 'Round', 'Amount']]
    st.subheader("Recent Investments")
    st.dataframe(last5_df)

    col1, col2 = st.columns(2)

    with col1:
        big_series = investor_df.groupby('Startup')['Amount'].sum().sort_values(ascending=False).head()
        st.subheader("Biggest Investments")
        fig1 = px.bar(big_series, x=big_series.index, y=big_series.values,
                      labels={'x': 'Startup', 'y': 'Total Investment'},
                      title="Top 5 Investments by Startup")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("📊 Sector Allocation (Improved View)")
        sector_data = investor_df.groupby('vertical')['Amount'].sum().sort_values(ascending=True).reset_index()
        fig = px.bar(sector_data, x='Amount', y='vertical', orientation='h', color='Amount',
                     color_continuous_scale='Viridis', title="Investment Distribution by Sector",
                     labels={'Amount': 'Total Investment', 'vertical': 'Sector'})
        fig.update_layout(margin=dict(l=100, r=20, t=50, b=50), height=500)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Investment by Stage (Bar Chart)")
        stage_series = investor_df.groupby('Round')['Amount'].sum().reset_index().sort_values('Amount', ascending=True)
        fig3 = px.bar(stage_series, x='Amount', y='Round', orientation='h', text='Amount', color='Round',
                      title='Total Investment by Funding Stage')
        fig3.update_layout(yaxis_title="Funding Stage", xaxis_title="Total Amount Invested", showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.subheader("Investment by City")
        city_series = investor_df.groupby('City')['Amount'].sum().sort_values()
        fig4 = px.bar(city_series, x=city_series.values, y=city_series.index,
                      orientation='h', labels={'x': 'Total Investment', 'y': 'City'},
                      title="City-wise Investment Distribution")
        st.plotly_chart(fig4, use_container_width=True)

    col5, col6 = st.columns(2)
    with col5:
        st.subheader("Investment Trend Over Years")
        year_series = df[df['Investor'].str.contains(investor, case=False, na=False)].groupby('Year')['Amount'].sum().reset_index()
        fig5 = px.line(year_series, x='Year', y='Amount', markers=True, title="Investment Trend Over the Years")
        st.plotly_chart(fig5, use_container_width=True)

    with col6:
        startups = investor_df['Startup'].unique()
        similar_df = df[df['Startup'].isin(startups)]
        co_investors = similar_df[~similar_df['Investor'].str.contains(investor, case=False, na=False)]
        similar_investors = co_investors['Investor'].value_counts().head(5)
        st.subheader("Similar Investors")
        st.bar_chart(similar_investors)

# ============ Startup POV ============
def load_startup_details(startup):
    st.title(f"📌 StartUp Analysis: {startup}")
    startup_df = df[df['Startup'] == startup]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Yearly Funding Trend")
        yearwise = startup_df.groupby('Year')['Amount'].sum().reset_index()
        fig = px.line(yearwise, x='Year', y='Amount', markers=True, title="Yearly Funding Trend")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Funding by Stage")
        stage_data = startup_df.groupby('Round')['Amount'].sum().reset_index()
        fig2 = px.bar(stage_data, x='Round', y='Amount', title="Funding by Round")
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.subheader("City-wise Funding")
        city_data = startup_df.groupby('City')['Amount'].sum().reset_index()
        fig3 = px.pie(city_data, names='City', values='Amount', title="Funding by City")
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader("Sector Focus")
        sector_data = startup_df.groupby('vertical')['Amount'].sum().reset_index()
        fig4 = px.bar(sector_data, x='vertical', y='Amount', title="Investment by Sector")
        st.plotly_chart(fig4, use_container_width=True)

    st.subheader("📄 Investment Records")
    st.dataframe(startup_df[['Date', 'Investor', 'Round', 'Amount', 'City', 'vertical']].sort_values('Date', ascending=False))

# ============ Startup Comparison ============
def compare_startups(s1, s2):
    st.title("🔍 Compare Two Startups")
    df1 = df[df['Startup'] == s1]
    df2 = df[df['Startup'] == s2]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"{s1} Funding Summary")
        fig1 = px.bar(df1.groupby('Year')['Amount'].sum().reset_index(), x='Year', y='Amount', title=f"{s1} Funding Over Years")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader(f"{s2} Funding Summary")
        fig2 = px.bar(df2.groupby('Year')['Amount'].sum().reset_index(), x='Year', y='Amount', title=f"{s2} Funding Over Years")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📊 Side-by-Side Comparison")
    comp = pd.DataFrame({
        'Startup': [s1, s2],
        'Total Funding': [df1['Amount'].sum(), df2['Amount'].sum()],
        'Funding Rounds': [df1['Round'].nunique(), df2['Round'].nunique()],
        'Investors': [df1['Investor'].nunique(), df2['Investor'].nunique()],
        'Cities': [df1['City'].nunique(), df2['City'].nunique()],
        'Sectors': [df1['vertical'].nunique(), df2['vertical'].nunique()]
    })
    st.dataframe(comp)

# ============ Best Startup by Year ============
def find_best_startup(year):
    st.title(f"🏆 Best Startup of {year}")
    best_df = df[df['Year'] == year].groupby('Startup')['Amount'].sum().reset_index().sort_values(by='Amount', ascending=False)
    if not best_df.empty:
        top_startup = best_df.iloc[0]
        st.success(f"🏅 The best startup in {year} is **{top_startup['Startup']}** with ₹{top_startup['Amount']:,.0f} funding.")
        load_startup_details(top_startup['Startup'])
    else:
        st.warning("No data for selected year.")

# ============ Sidebar Navigation ============
st.sidebar.title("Startup Funding Analysis")
option = st.sidebar.selectbox("Select an option", ["Overall Analysis", "StartUp", "Compare Startups", "Best Startup by Year", "Investor"])

if option == "Overall Analysis":
    pass

elif option == "StartUp":
    selected_startup = st.sidebar.selectbox("Select a Startup", sorted(df['Startup'].dropna().unique()))
    if st.sidebar.button("Find StartUp Details"):
        load_startup_details(selected_startup)

elif option == "Compare Startups":
    s1 = st.selectbox("Select First Startup", sorted(df['Startup'].dropna().unique()), key="s1")
    s2 = st.selectbox("Select Second Startup", sorted(df['Startup'].dropna().unique()), key="s2")
    if st.button("Compare"):
        compare_startups(s1, s2)

elif option == "Best Startup by Year":
    year = st.sidebar.selectbox("Select Year", sorted(df['Year'].dropna().unique(), reverse=True))
    if st.sidebar.button("Find Best Startup"):
        find_best_startup(year)

elif option == "Investor":
    investor_list = sorted(set(sum(df['Investor'].dropna().str.split(','), [])))
    investor_list = [i.strip() for i in investor_list if i.strip()]
    selected_investor = st.sidebar.selectbox("Select an Investor", investor_list)
    if st.sidebar.button("Find Investor Details"):
        load_investor_details(selected_investor)
df['Month_Year'] = df['Date'].dt.to_period('M').astype(str)

# ================= OVERALL ANALYSIS SECTION ===================

if option == "Overall Analysis":
    st.title("📊 Overall Startup Funding Analysis")

    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Funding", f"₹{df['Amount'].sum():,.0f}  Cr")
    col2.metric("Max Single Round", f"₹{df['Amount'].max():,.0f} Cr")
    col3.metric("Average Round", f"₹{df['Amount'].mean():,.0f} Cr")
    col4.metric("Total Funded Startups", df['Startup'].nunique())

    # MoM Chart
   # 📅 Enhanced Dual-Axis Chart: Monthly Funding Amount vs Round Count
  
    st.subheader("💰 Monthly Funding Trend")

    # ✅ Ensure Month_Year is datetime
    df['Month_Year'] = pd.to_datetime(df['Month_Year'])

    # ✅ Extract components for calendar layout
    df['Year'] = df['Month_Year'].dt.year
    df['Month_Num'] = df['Month_Year'].dt.month
    df['Month_Name'] = df['Month_Year'].dt.strftime('%b')

    # ✅ Group by year and month
    calendar_df = df.groupby(['Year', 'Month_Num', 'Month_Name'])['Amount'].sum().reset_index()

    # ✅ Order months correctly
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    calendar_df['Month_Name'] = pd.Categorical(calendar_df['Month_Name'], categories=month_order, ordered=True)

    # ✅ Pivot the table for heatmap
    heatmap_data = calendar_df.pivot(index='Year', columns='Month_Name', values='Amount')

    # ✅ Create calendar-style heatmap
    fig = px.imshow(
        heatmap_data,
        text_auto=True,
        color_continuous_scale='Plasma',
        aspect="auto",
        title="💸 Calendar View of Monthly Funding"
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Year",
        template='plotly_white',
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📊 Monthly Number of Funding Rounds")

    # Aggregate number of rounds
    rounds_df = df.groupby('Month_Year')['Amount'].count().reset_index()
    rounds_df.rename(columns={'Amount': 'Number_of_Rounds'}, inplace=True)

    # Lollipop chart (scatter + vertical line)
    fig_rounds = go.Figure()

    # Add stems (lines)
    for i in range(len(rounds_df)):
        fig_rounds.add_shape(
            type="line",
            x0=rounds_df['Month_Year'][i],
            y0=0,
            x1=rounds_df['Month_Year'][i],
            y1=rounds_df['Number_of_Rounds'][i],
            line=dict(color="mediumpurple", width=2)
        )

    # Add markers
    fig_rounds.add_trace(go.Scatter(
        x=rounds_df['Month_Year'],
        y=rounds_df['Number_of_Rounds'],
        mode='markers+text',
        marker=dict(size=8, color='mediumpurple'),
        text=rounds_df['Number_of_Rounds'],
        textposition='top center',
        name="Funding Rounds"
    ))

    fig_rounds.update_layout(
        title="📈 Number of Funding Rounds per Month",
        xaxis_title="Month-Year",
        yaxis_title="Number of Rounds",
        template="plotly_white",
        height=450
    )

    st.plotly_chart(fig_rounds, use_container_width=True)


    # 🌡️ Enhanced Annotated Heatmap: City vs Year
    st.subheader("🧱 Annotated Heatmap: City vs Year")

    import plotly.graph_objects as go

    heatmap_data = pd.pivot_table(df, values='Amount', index='City', columns='Year', aggfunc='sum', fill_value=0)
    heatmap_data = heatmap_data.sort_values(heatmap_data.columns[-1], ascending=False).head(10)

    fig_heat = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='Viridis',
        hoverongaps=False,
        text=heatmap_data.values,
        texttemplate="%{text:.2s}",
        showscale=True
    ))
    fig_heat.update_layout(
        title="🔥 Top 10 Cities Funding by Year (with ₹ annotations)",
        xaxis_title="Year",
        yaxis_title="City",
        height=500,
        template='plotly_white'
    )

    st.plotly_chart(fig_heat, use_container_width=True)

    # Sector Analysis
    st.subheader("🏢 Sector-wise Analysis")
    col1, col2 = st.columns(2)
    with col1:
        top_sector_count = df['vertical'].value_counts().head(10)
        fig3 = px.bar(top_sector_count, x=top_sector_count.index, y=top_sector_count.values,
                     title="Top Sectors by Number of Investments", labels={'x': 'Sector', 'y': 'Count'})
        st.plotly_chart(fig3, use_container_width=True)
    with col2:
        top_sector_amount = df.groupby('vertical')['Amount'].sum().sort_values(ascending=False).head(10)
        fig4 = px.bar(top_sector_amount, x=top_sector_amount.index, y=top_sector_amount.values,
                     title="Top Sectors by Total Investment", labels={'x': 'Sector', 'y': 'Total Amount'})
        st.plotly_chart(fig4, use_container_width=True)

    # Type of Funding
    st.subheader("💼 Type of Funding")
    funding_type = df['Round'].value_counts().head(10)
    fig5 = px.pie(funding_type, values=funding_type.values, names=funding_type.index, title="Funding Types Distribution")
    st.plotly_chart(fig5, use_container_width=True)

    # City-wise Funding
    st.subheader("🏙️ City-wise Funding")
    top_cities = df.groupby('City')['Amount'].sum().sort_values(ascending=False).head(10)
    fig6 = px.bar(top_cities, x=top_cities.index, y=top_cities.values, title="Top 10 Cities by Funding",
                 labels={'x': 'City', 'y': 'Funding Amount'})
    st.plotly_chart(fig6, use_container_width=True)

    # Top Startups Year-wise
    st.subheader("🚀 Top Startups by Year")
    top_startups = df.groupby(['Year', 'Startup'])['Amount'].sum().reset_index()
    top_startups = top_startups.sort_values(['Year', 'Amount'], ascending=[True, False])
    top_startups = top_startups.groupby('Year').head(1)
    st.dataframe(top_startups.reset_index(drop=True))

    # Top Investors
    st.subheader("🏦 Top Investors")
    investors_exp = df.assign(Investor=df['Investor'].str.split(',')).explode('Investor')
    investors_exp['Investor'] = investors_exp['Investor'].str.strip()
    top_investors = investors_exp['Investor'].value_counts().head(10)
    fig7 = px.bar(top_investors, x=top_investors.index, y=top_investors.values, title="Top 10 Investors by Number of Investments",
                labels={'x': 'Investor', 'y': 'Investment Count'})
    st.plotly_chart(fig7, use_container_width=True)

