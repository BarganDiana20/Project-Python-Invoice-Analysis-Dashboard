import pandas as pd
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px

df = pd.read_csv("invoice_data.csv")
df['Data factura'] = pd.to_datetime(df['Data factura'], dayfirst=True)

app = dash.Dash(__name__, external_stylesheets=[
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css'
])

# Layout application
app.layout = html.Div(className='container py-4', children=[

    html.H1("📊 Invoice Analysis Dashboard",
            className='text-center mb-4',
            style={'font-family': 'Arial', 'color': '#2c3e50', 'fontWeight': 'bold', 'textShadow': '1px 1px #bdc3c7'}),

    html.H5( "by Bargan Diana Georgiana",
        className='text-center mt-1',
        style={'font-family': 'Arial','color': '#34495e','fontWeight': 'bold',
            'margin-left': '20px', 'textAlign': 'right',  'fontStyle': 'italic'}),

    html.Div(className='row mb-4 p-3', style={'backgroundColor': '#dce8f2', 'borderRadius': '10px'}, children=[
        html.Div(className='col-md-3 mb-2', children=[
            html.Label("Year:", className='form-label', style={'fontWeight': 'bold', 'color': '#34495e'}),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': str(y), 'value': y} for y in df['Data factura'].dt.year.unique()],
                value=df['Data factura'].dt.year.max(),
                className='form-select'
            )
        ]),
        html.Div(className='col-md-3 mb-2', children=[
            html.Label("Supplier:", className='form-label', style={'fontWeight': 'bold', 'color': '#34495e'}),
            dcc.Dropdown(
                id='supplier-dropdown',
                options=[{'label': s, 'value': s} for s in df['Furnizor'].unique()],
                multi=True,
                className='form-select'
            )
        ]),
        html.Div(className='col-md-3 mb-2', children=[
            html.Label("Type of Document:", className='form-label', style={'fontWeight': 'bold', 'color': '#34495e'}),
            dcc.Dropdown(
                id='doc-type-dropdown',
                options=[{'label': t, 'value': t} for t in df['Tip document'].unique()],
                multi=True,
                className='form-select'
            )
        ]),
        html.Div(className='col-md-3 mb-2', children=[
            html.Label("Range Sum:", className='form-label', style={'fontWeight': 'bold', 'color': '#34495e'}),
            dcc.RangeSlider(
                id='sum-range-slider',
                min=df['Suma factura (lei)'].min(),
                max=df['Suma factura (lei)'].max(),
                step=1000,
                marks={i: str(i) for i in range(0, int(df['Suma factura (lei)'].max()) + 1, 5000)},
                value=[df['Suma factura (lei)'].min(), df['Suma factura (lei)'].max()],
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ])
    ]),

    # Statistics
    html.Div(className='row mb-4', children=[
       html.Div(id='data-statistics', className='col-12 d-flex justify-content-around flex-wrap')
    ]),

    # First three plots
    html.Div(className='row mb-4', children=[
        html.Div(dcc.Graph(id='bar-chart'), className='col-md-6 mb-3'),
        html.Div(dcc.Graph(id='pie-chart'), className='col-md-6 mb-3'),
        html.Div(dcc.Graph(id='line-chart'), className='col-12 mb-3')
    ]),

    # Grafic Top 10 clienti
    html.Div(className='row mb-4', children=[
        html.Div(dcc.Graph(id='top-clients-chart'), className='col-12 mb-3')
    ]),

    # The first two graphs with TVA
    html.Div(className='row mb-4', children=[
        html.Div(dcc.Graph(id='tva-supplier-chart'), className='col-md-6 mb-3'),
        html.Div(dcc.Graph(id='tva-scatter-chart'), className='col-md-6 mb-3')
    ]),

    html.Div(className='row mb-4', children=[
        html.Div(dcc.Graph(id='tva-yearly-chart'), className='col-12 mb-3')
    ]),

    # Interactive table
    html.Div(dash_table.DataTable(
        id='data-table',
        columns=[{"name": i, "id": i} for i in df.columns],
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_header={'backgroundColor': '#f0f0f0', 'fontWeight': 'bold'},
        style_cell={'textAlign': 'left', 'padding': '5px'}
    ))
])

# Callback for update dashboard
@app.callback(
    [Output('data-statistics', 'children'),
     Output('bar-chart', 'figure'),
     Output('pie-chart', 'figure'),
     Output('line-chart', 'figure'),
     Output('top-clients-chart', 'figure'),
     Output('tva-supplier-chart', 'figure'),
     Output('tva-scatter-chart', 'figure'),
     Output('tva-yearly-chart', 'figure'),
     Output('data-table', 'data')],
    [Input('year-dropdown', 'value'),
     Input('supplier-dropdown', 'value'),
     Input('doc-type-dropdown', 'value'),
     Input('sum-range-slider', 'value')]
)
def update_dashboard(year, suppliers, doc_types, sum_range):
    filtered_df = df[df['Data factura'].dt.year == year]

    if suppliers:
        filtered_df = filtered_df[filtered_df['Furnizor'].isin(suppliers)]
    if doc_types:
        filtered_df = filtered_df[filtered_df['Tip document'].isin(doc_types)]
    filtered_df = filtered_df[(filtered_df['Suma factura (lei)'] >= sum_range[0]) &
                              (filtered_df['Suma factura (lei)'] <= sum_range[1])]

    # Statistics
    if filtered_df.empty:
        statistics = [html.Div("Nu există date pentru selecția aleasă.", className='text-danger')]
        bar_fig = px.bar(title="Nicio informație")
        pie_fig = px.pie(title="Nicio informație")
        table_data = []
    else:
        statistics = [
            html.Div(f"Number of records: {len(filtered_df)}",
                     className='card p-2 m-1',
                     style={'backgroundColor': '#d1ecf1', 'color': '#0c5460', 'fontWeight': 'bold'}),
            html.Div(f"The total sum: {filtered_df['Suma factura (lei)'].sum():.2f} lei",
                     className='card p-2 m-1',
                     style={'backgroundColor': '#d4edda', 'color': '#155724', 'fontWeight': 'bold'}),
            html.Div(f"Average of sums: {filtered_df['Suma factura (lei)'].mean():.2f} lei",
                     className='card p-2 m-1',
                     style={'backgroundColor': '#f2e5bb', 'color': '#856404', 'fontWeight': 'bold'})
        ]
        bar_fig = px.bar(filtered_df, x='Furnizor', y='Suma factura (lei)',
                         title='Sum of invoices per supplier',
                         labels={"Furnizor": "Supplier", "Suma factura (lei)": "Invoice amount (lei)"})

        bar_fig.update_layout(title_font = dict(weight = 'bold', family = "Arial", color = "black", size = 20),
                              paper_bgcolor="#fce3c5",
                              xaxis=dict(title_font=dict(family="Arial", size=16, color="black", weight="bold")),
                              yaxis=dict(title_font=dict(family="Arial", size=16, color="black", weight="bold")),
                              xaxis_tickfont=dict(family="Arial", size=12, color="black", weight="bold"),
                              yaxis_tickfont=dict(family="Arial", size=12, color="black", weight="bold")
                              )

        pie_fig = px.pie(filtered_df, names='Furnizor', values='Suma factura (lei)',
                         title='Distribution of amounts per supplier')

        pie_fig.update_layout(title_font=dict(weight='bold', family="Arial", color="black", size=20),
                              paper_bgcolor="#f7eed0")

        table_data = filtered_df.to_dict('records')

    if not filtered_df.empty:
        filtered_df['Month'] = filtered_df['Data factura'].dt.to_period('M').astype(str)
        monthly_sum = filtered_df.groupby('Month')['Suma factura (lei)'].sum().reset_index()
        line_fig = px.line(monthly_sum, x='Month', y='Suma factura (lei)',
                           title='Monthly invoice sum',
                           labels={'Month': 'Month', 'Suma factura (lei)': 'Sum (lei)'},
                           color_discrete_sequence=["red"],
                           markers = True)
    else:
        line_fig = px.line(title="No data")

    line_fig.update_traces(marker=dict(color="black", size=8))
    line_fig.update_layout(title_font=dict(weight='bold', family="Arial", color="black", size=20),
                           paper_bgcolor="#d5ebf7", plot_bgcolor = "#f2f2f0",
                           xaxis=dict(title_font=dict(family="Arial", size=16, color="black", weight="bold")),
                           yaxis=dict(title_font=dict(family="Arial", size=16, color="black", weight="bold")),
                           xaxis_tickfont=dict(family="Arial", size=12, color="black", weight="bold"),
                           yaxis_tickfont=dict(family="Arial", size=12, color="black", weight="bold")
                           )

    # --- Top 10 customers ---
    if not filtered_df.empty:
        top_clients = filtered_df.groupby('Furnizor')['Suma factura (lei)'].sum().nlargest(10).reset_index()
        top_clients_fig = px.bar(top_clients, x='Furnizor', y='Suma factura (lei)',
                                 title='Top 10 Suppliers by Invoice Sum',
                                 labels={'Furnizor': 'Supplier', 'Suma factura (lei)': 'Sum (lei)'},
                                 text='Suma factura (lei)',
                                 color_discrete_sequence=["#aee649"]
                                 )
        top_clients_fig.update_traces(texttemplate='%{text:.2f}', textposition='inside',
                                      textfont=dict(family="Arial", size=14, color="black", weight="bold")
                                      )
    else:
        top_clients_fig = px.bar(title="No data")

    top_clients_fig.update_layout(title_font=dict(weight='bold', family="Arial", color="black", size=20),
                                  paper_bgcolor="#f7eed0", plot_bgcolor = "#f2f2f0",
                                  xaxis=dict(title_font=dict(family="Arial", size=16, color="black", weight="bold")),
                                  yaxis=dict(title_font=dict(family="Arial", size=16, color="black", weight="bold")),
                                  xaxis_tickfont=dict(family="Arial", size=12, color="black", weight="bold"),
                                  yaxis_tickfont=dict(family="Arial", size=12, color="black", weight="bold")
                                  )

    # --- TVA charts ---
    if not filtered_df.empty:
        # 1. Total TVA per Supplier
        tva_supplier = filtered_df.groupby('Furnizor')['Valoare TVA (lei)'].sum().reset_index()
        tva_supplier_fig = px.bar(tva_supplier, x='Furnizor', y='Valoare TVA (lei)',
                                  title='Total TVA per Supplier',
                                  labels={'Furnizor': 'Supplier', 'Valoare TVA (lei)': 'TVA (lei)'},
                                  color_discrete_sequence=["#ff7f0e"])

        # 2. TVA vs Invoice Amount
        tva_scatter_fig = px.scatter(filtered_df, x='Suma factura (lei)', y='Valoare TVA (lei)',
                                     color='Furnizor',
                                     title='TVA vs Invoice Amount',
                                     labels={'Suma factura (lei)': 'Invoice Amount (lei)',
                                             'Valoare TVA (lei)': 'TVA (lei)'})
    else:
        tva_supplier_fig = px.bar(title="No data")
        tva_scatter_fig = px.scatter(title="No data")

    tva_supplier_fig.update_layout(title_font=dict(weight='bold', family="Arial", color="black", size=20),
                          paper_bgcolor="#fce3c5",
                          xaxis=dict(title_font=dict(family="Arial", size=16, color="black", weight="bold")),
                          yaxis=dict(title_font=dict(family="Arial", size=16, color="black", weight="bold")),
                          xaxis_tickfont=dict(family="Arial", size=12, color="black", weight="bold"),
                          yaxis_tickfont=dict(family="Arial", size=12, color="black", weight="bold")
                          )
    tva_scatter_fig.update_layout(title_font=dict(weight='bold', family="Arial", color="black", size=20),
                          paper_bgcolor="#eee3fa", plot_bgcolor="#f7f5fa",
                          xaxis=dict(title_font=dict(family="Arial", size=16, color="black", weight="bold")),
                          yaxis=dict(title_font=dict(family="Arial", size=16, color="black", weight="bold")),
                          xaxis_tickfont=dict(family="Arial", size=12, color="black", weight="bold"),
                          yaxis_tickfont=dict(family="Arial", size=12, color="black", weight="bold")
                          )

    #3. TVA Evolution per Year
    if not filtered_df.empty:
        tva_yearly = df.groupby(df['Data factura'].dt.year)['Valoare TVA (lei)'].sum().reset_index()
        tva_yearly_fig = px.bar(tva_yearly, x='Data factura', y='Valoare TVA (lei)',
                                text='Valoare TVA (lei)', title='TVA Evolution per Year',
                                labels={'Data factura': 'Year', 'Valoare TVA (lei)': 'TVA (lei)'},
                                color_discrete_sequence=["#a26fd9"])
        tva_yearly_fig.update_traces(texttemplate='%{text:.2f}', textposition='inside',
                                      textfont=dict(family="Arial", size=16, color="black", weight="bold")
                                      )
    else:
        tva_yearly_fig = px.bar(title="No data")

    #design
    tva_yearly_fig.update_layout(title_font=dict(weight='bold', family="Arial", color="black", size=20),
                  paper_bgcolor="#f7eed0", plot_bgcolor="#f2f2f0",
                  xaxis=dict(title_font=dict(family="Arial", size=16, color="black", weight="bold")),
                  yaxis=dict(title_font=dict(family="Arial", size=16, color="black", weight="bold")),
                  xaxis_tickfont=dict(family="Arial", size=14, color="black", weight="bold"),
                  yaxis_tickfont=dict(family="Arial", size=14, color="black", weight="bold")
                  )

    return statistics, bar_fig, pie_fig, line_fig, top_clients_fig, \
       tva_supplier_fig, tva_scatter_fig, tva_yearly_fig, table_data

if __name__ == '__main__':
    app.run(debug=True, port=8050)
