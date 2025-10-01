"""
Chart components for data visualization.
"""

import pandas as pd
import plotly.express as px
import streamlit as st
from typing import Dict, Any, List


def render_department_pie_chart(dept_data: Dict[str, Any]):
    """Render department distribution pie chart."""
    fig_pie = px.pie(
        values=dept_data['values'],
        names=dept_data['names'],
        title=dept_data['title']
    )
    fig_pie.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        marker=dict(colors=px.colors.qualitative.Set3)
    )
    st.plotly_chart(fig_pie, use_container_width=True)


def render_salary_box_chart(df_salary: pd.DataFrame):
    """Render salary distribution box chart."""
    if not df_salary.empty:
        fig_box = px.box(
            df_salary, 
            x='Department', 
            y='Salary',
            title="Salary Distribution by Department",
            color='Department'
        )
        fig_box.update_layout(showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)


def render_years_of_service_histogram(years_data: List[float]):
    """Render years of service histogram."""
    fig_hist = px.histogram(
        x=years_data,
        title="Years of Service Distribution",
        labels={'x': 'Years of Service', 'y': 'Number of Employees'},
        nbins=20
    )
    st.plotly_chart(fig_hist, use_container_width=True)


def render_status_bar_chart(status_data: Dict[str, int]):
    """Render status distribution bar chart."""
    fig_status = px.bar(
        x=list(status_data.keys()),
        y=list(status_data.values()),
        title="Employee Status Distribution",
        labels={'x': 'Status', 'y': 'Count'},
        color=list(status_data.keys())
    )
    st.plotly_chart(fig_status, use_container_width=True)
