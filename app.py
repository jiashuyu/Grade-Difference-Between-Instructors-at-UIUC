# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import plotly.express as px

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# load data
gpa = pd.read_csv('https://raw.githubusercontent.com/wadefagen/datasets/master/gpa/uiuc-gpa-dataset.csv')
gpa = gpa[~gpa['Primary Instructor'].isnull()]

subject_list = gpa['Subject'].unique()
subject_list.sort()


app.layout = html.Div([
    html.H6("Please choose from the following subjects and their available course numbers:"),
    html.Div([

        html.Div([
            dcc.Dropdown(
                id='subject',
                options=[{'label': i, 'value': i} for i in subject_list],
                value='STAT'
            )
        ],
        style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='course_number'
            )
        ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),
    html.Br(),
    html.Br(),
    html.H6("Grouped Bar Chart for the Grade Distribution of Each Instructor of the chosen course"),
    dcc.Graph(id='grade_distribution_graph_1'),
    html.Br(),
    html.Br(),
    html.H6("Stacked Bar Chart for Letter Grade Percentages of Each Instructor of the chosen course"),
    dcc.Graph(id='grade_distribution_graph_2')
])


@app.callback(
    Output('course_number', 'options'),
    Input('subject', 'value'))
def set_course_number_options(selected_subject):
    course_list = gpa[gpa['Subject'] == selected_subject]['Number'].unique()
    course_list.sort()
    return [{'label': i, 'value': i} for i in course_list]


@app.callback(
    Output('course_number', 'value'),
    Input('course_number', 'options'))
def set_course_number_value(available_options):
    return available_options[0]['value']


@app.callback(
    Output('grade_distribution_graph_1', 'figure'),
    Input('subject', 'value'),
    Input('course_number', 'value'))
def update_graph_1(selected_subject, selected_course):
    selected_gpa = gpa[(gpa['Subject'] == selected_subject) & (gpa['Number'] == selected_course)]
    group_gpa = selected_gpa.groupby('Primary Instructor')['A+','A','A-','B+','B','B-','C+','C','C-','D+','D','D-','F'].sum().reset_index()
    group_gpa['A_range'] = group_gpa['A+'] + group_gpa['A'] + group_gpa['A-']
    group_gpa['B_range'] = group_gpa['B+'] + group_gpa['B'] + group_gpa['B-']
    group_gpa['C_range'] = group_gpa['C+'] + group_gpa['C'] + group_gpa['C-']
    group_gpa['D_range'] = group_gpa['D+'] + group_gpa['D'] + group_gpa['D-']
    group_gpa.drop(['A+','A','A-','B+','B','B-','C+','C','C-','D+','D','D-'], axis = 1, inplace=True)
    group_gpa.rename({'A_range':'A', 'B_range':'B', 'C_range':'C', 'D_range':'D'}, axis=1, inplace=True)

    fig = px.bar(group_gpa, x="Primary Instructor", y=['A','B','C','D','F'], barmode="group")
    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest',barmode='group')

    return fig


@app.callback(
    Output('grade_distribution_graph_2', 'figure'),
    Input('subject', 'value'),
    Input('course_number', 'value'))
def update_graph_2(selected_subject, selected_course):
    selected_gpa = gpa[(gpa['Subject'] == selected_subject) & (gpa['Number'] == selected_course)]
    group_gpa = selected_gpa.groupby('Primary Instructor')['A+','A','A-','B+','B','B-','C+','C','C-','D+','D','D-','F'].sum().reset_index()
    group_gpa['A_range'] = group_gpa['A+'] + group_gpa['A'] + group_gpa['A-']
    group_gpa['B_range'] = group_gpa['B+'] + group_gpa['B'] + group_gpa['B-']
    group_gpa['C_range'] = group_gpa['C+'] + group_gpa['C'] + group_gpa['C-']
    group_gpa['D_range'] = group_gpa['D+'] + group_gpa['D'] + group_gpa['D-']
    group_gpa['total'] = group_gpa['A_range'] + group_gpa['B_range'] + group_gpa['C_range'] + group_gpa['D_range'] + group_gpa['F']
    group_gpa['percentage_A'] = round(group_gpa['A_range'] / group_gpa['total'], 3)
    group_gpa['percentage_B'] = round(group_gpa['B_range'] / group_gpa['total'], 3)
    group_gpa['percentage_C'] = round(group_gpa['C_range'] / group_gpa['total'], 3)
    group_gpa['percentage_D'] = round(group_gpa['D_range'] / group_gpa['total'], 3)
    group_gpa['percentage_F'] = round(group_gpa['F'] / group_gpa['total'], 3)

    gpa_percentage = group_gpa[['Primary Instructor','percentage_A', 'percentage_B', 'percentage_C', 'percentage_D', 'percentage_F']]
    long_gpa = pd.wide_to_long(gpa_percentage, stubnames='percentage', i='Primary Instructor', j='grade',
                    sep='_', suffix='\w+').reset_index()

    fig = px.bar(long_gpa, x="Primary Instructor", y="percentage", color="grade", text='percentage')
    # fig.update_traces(texttemplate='%{text:.2s}')
    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)