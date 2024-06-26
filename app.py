import os
import requests
import dash
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
import yfinance as yf

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # Defining the server attribute
selected_points = []

def fetch_stock_data(stock_symbol, timeframe="1d", start_date=None, end_date=None):
    try:
        stock_data = yf.download(stock_symbol, start=start_date, end=end_date, interval=timeframe)
        return stock_data
    except Exception as e:
        print("Error fetching stock data:", str(e))
        return None


# Calculate Wavetrend
def calculate_wavetrend(data, n1=10, n2=21):
    # Typical Price
    data['TP'] = (data['High'] + data['Low'] + data['Close']) / 3
    # Exponential Moving Averages
    data['esa'] = data['TP'].ewm(span=n1, adjust=False).mean()
    data['d'] = abs(data['TP'] - data['esa']).ewm(span=n1, adjust=False).mean()
    # Commodity Channel Index
    data['ci'] = (data['TP'] - data['esa']) / (0.015 * data['d'])
    # Wavetrend
    data['WT1'] = data['ci'].ewm(span=n2, adjust=False).mean()
    data['WT2'] = data['WT1'].rolling(window=4).mean()
    return data

# Calculate RSI
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rsi = 100 - (100 / (1 + (gain / loss)))
    data['RSI'] = rsi
    return data

# Calculate profit based on buy/sell strategy
def calculate_profit(data, start_index, end_index):
    holdings = 1000  # Initial investment of $1000
    buy_price = data.iloc[start_index]['Close']
    quantity = holdings / buy_price
    
    for i in range(start_index, end_index + 1):
        if data.iloc[i]['Close'] > data.iloc[i]['Upper_band'] and (data.iloc[i]['WT1'] > 60 or data.iloc[i]['WT2'] > 60):
            sell_price = data.iloc[i]['Close']
            quantity_sold = quantity * 0.2
            holdings += quantity_sold * sell_price
            quantity -= quantity_sold
        elif data.iloc[i]['Close'] < data.iloc[i]['Lower_band'] and (data.iloc[i]['WT1'] < -60 or data.iloc[i]['WT2'] < -60):
            buy_price = data.iloc[i]['Close']
            quantity_bought = holdings * 0.2 / buy_price
            holdings -= quantity_bought * buy_price
            quantity += quantity_bought

    final_price = data.iloc[end_index]['Close']
    final_value = quantity * final_price + holdings
    profit = final_value - 1000  # Subtract initial investment
    return profit

# Create a live updating plot
def create_plot(data, stock_symbol):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.02, subplot_titles=('stock Price', 'Indicators'))

    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['Upper_band'] = data['MA20'] + 2 * data['Close'].rolling(window=20).std()
    data['Lower_band'] = data['MA20'] - 2 * data['Close'].rolling(window=20).std()

    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Close Price'), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['MA20'], name='20-Day MA'), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['Upper_band'], name='Upper Bollinger Band', line=dict(dash='dash', color='red')), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['Lower_band'], name='Lower Bollinger Band', line=dict(dash='dash', color='green')), row=1, col=1)

    data = calculate_rsi(data)
    fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], name='RSI', line=dict(color='blue')), row=2, col=1)
    fig.add_hline(y=70, line=dict(color='orange', dash='dash'), row=2, col=1)
    fig.add_hline(y=30, line=dict(color='purple', dash='dash'), row=2, col=1)

    data = calculate_wavetrend(data)
    fig.add_trace(go.Scatter(x=data.index, y=data['WT1'], name='Wavetrend WT1', line=dict(color='magenta')), row=2, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['WT2'], name='Wavetrend WT2', line=dict(color='cyan')), row=2, col=1)
    fig.add_hline(y=60, line=dict(color='red', dash='dash'), row=2, col=1)
    fig.add_hline(y=70, line=dict(color='red', dash='dash'), row=2, col=1)
    fig.add_hline(y=-60, line=dict(color='green', dash='dash'), row=2, col=1)
    fig.add_hline(y=-70, line=dict(color='green', dash='dash'), row=2, col=1)

    both_exceeded_x = []
    both_exceeded_y = []
    for index, row in data.iterrows():
        if row['Close'] > row['Upper_band'] and row['RSI'] > 70:
            both_exceeded_x.append(index)
            both_exceeded_y.append(row['Close'])
        elif row['Close'] < row['Lower_band'] and row['RSI'] < 30:
            both_exceeded_x.append(index)
            both_exceeded_y.append(row['Close'])

    fig.add_trace(go.Scatter(x=both_exceeded_x, y=both_exceeded_y, mode='markers', marker=dict(color='green', size=10), name='Both exceeded (Bollinger & RSI)'), row=1, col=1)

    both_exceeded_wt_x = []
    both_exceeded_wt_y = []
    for index, row in data.iterrows():
        if row['Close'] > row['Upper_band'] and (row['WT1'] > 60 or row['WT2'] > 60):
            both_exceeded_wt_x.append(index)
            both_exceeded_wt_y.append(row['Close'])
        elif row['Close'] < row['Lower_band'] and (row['WT1'] < -60 or row['WT2'] < -60):
            both_exceeded_wt_x.append(index)
            both_exceeded_wt_y.append(row['Close'])

    fig.add_trace(go.Scatter(x=both_exceeded_wt_x, y=both_exceeded_wt_y, mode='markers', marker=dict(color='red', size=10), name='Both exceeded (Bollinger & Wavetrend)'), row=1, col=1)

    fig.update_layout(height=800, title_text=f'{stock_symbol} Price and Indicators')

    return fig

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Stock Data Visualization")
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Input(
                id='stock-input',
                placeholder='Enter stock symbol (e.g., AAPL)',
                type='text',
                value='AAPL',
                style={'width': '50%'}
            ),
            dbc.Button("Submit", id='submit-stock', color="primary", className="mr-1", n_clicks=0)
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='stock-graph',
                config={'displayModeBar': True},
                style={'height': '70vh'}
            )
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id='selected-points', style={'marginTop': 20})
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Button("Calculate Profit", id='calculate-profit', color="primary", className="mr-1", n_clicks=0)
        ], width={'size': 2, 'offset': 5})
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Button("Clear Selection", id='clear-selection', color="secondary", className="mr-1", n_clicks=0)
        ], width={'size': 2, 'offset': 5})
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id='profit-output', style={'marginTop': 20})
        ], width=12)
    ])
], fluid=True)

@app.callback(
    Output('stock-graph', 'figure'),
    [Input('submit-stock', 'n_clicks')],
    [State('stock-input', 'value')]
)
def update_graph(n_clicks, stock_symbol):
    stock_data = fetch_stock_data(stock_symbol)
    if stock_data is not None:
        fig = create_plot(stock_data, stock_symbol)
        return fig
    else:
        return go.Figure()

@app.callback(
    Output('selected-points', 'children'),
    [Input('stock-graph', 'clickData'), Input('clear-selection', 'n_clicks')]
)
def update_selected_points(clickData, n_clicks):
    global selected_points

    # Get the context to determine which input triggered the callback
    ctx = dash.callback_context

    if not ctx.triggered:
        return [f"Selected points: {selected_points}"]

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'stock-graph':
        if clickData:
            selected_point = clickData['points'][0]
            selected_points.append(selected_point['pointIndex'])

    elif triggered_id == 'clear-selection':
        selected_points = []

    return [f"Selected points: {selected_points}"]

@app.callback(
    Output('profit-output', 'children'),
    [Input('calculate-profit', 'n_clicks')]
)
def calculate_profit_callback(n_clicks):
    global selected_points
    if n_clicks > 0 and len(selected_points) == 2:
        start_index, end_index = selected_points
        stock_data = fetch_stock_data("AAPL")

        # Calculate necessary columns for profit calculation
        stock_data['MA20'] = stock_data['Close'].rolling(window=20).mean()
        stock_data['Upper_band'] = stock_data['MA20'] + 2 * stock_data['Close'].rolling(window=20).std()
        stock_data['Lower_band'] = stock_data['MA20'] - 2 * stock_data['Close'].rolling(window=20).std()
        stock_data = calculate_wavetrend(stock_data)

        required_columns = ['Upper_band', 'Lower_band', 'WT1', 'WT2']
        if not all(col in stock_data.columns for col in required_columns):
            return "Required data columns are not available"

        profit = calculate_profit(stock_data, start_index, end_index)
        return f"Calculated profit: ${profit:.2f}"
    return "Select two points to calculate profit"


if __name__ == '__main__':
    app.run_server(debug=True)