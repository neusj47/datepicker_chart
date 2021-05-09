# -*- coding: utf-8 -*-

# 특정 종목 가격을 기간별로 확인할 수 있는 함수
# 대상 기간과 관심 TICKER를 입력합니다.
# date.picker의 기간을 입력합니다. (1차)
# dropdown의 indicagto를 입력합니다 (2차)
# 입력된 기간과, indicator에 해당하는 데이터를 호출 후 Graph를 산출합니다. (3차)

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas_datareader.data as web
import datetime
from datetime import date
import pandas as pd

# TICKER를 입력합니다.
TICKER = ['AAPL','TSLA','MSFT','AMZN','GOOGL','FB']

start = date(2016, 1, 1)
end = datetime.datetime.now()

# 수익률, 거래량 데이터를 산출합니다.
dfs = web.DataReader(TICKER[0], 'yahoo', start, end)
dfs.reset_index(inplace=True)
dfs.set_index("Date", inplace=True)
dfs['Return'] = (dfs['Close'] / dfs['Close'].shift(1)) - 1
dfs['Return(cum)'] = (1 + dfs['Return']).cumprod()
dfs = dfs.dropna()
dfs.loc[:,'TICKER'] = TICKER[0]
df = dfs

for i in range(1,len(TICKER)):
    start = date(2016, 1, 1)
    end = datetime.datetime.now()
    dfs = web.DataReader(TICKER[i], 'yahoo', start, end)
    dfs.reset_index(inplace=True)
    dfs.set_index("Date", inplace=True)
    dfs['Return'] = (dfs['Close'] / dfs['Close'].shift(1)) - 1
    dfs['Return(cum)'] = (1 + dfs['Return']).cumprod()
    dfs = dfs.dropna()
    dfs.loc[:,'TICKER'] = TICKER[i]
    df = df.append(dfs)

# 데이터타입(Date)변환 문제로 csv 저장 후, 다시 불러옵니다. (파일 경로 설정 필요!!)
df = df.reset_index().rename(columns={"index": "id"})
df.to_csv('pricevolume.csv', index=False, encoding='cp949')
df = pd.read_csv('..../pricevolume.csv')

availble_TICKER = df['TICKER'].unique()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H2(children='PRICE-CHART by date'),
    dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=date(1995, 8, 5),
        max_date_allowed=date(2030, 9, 19),
        initial_visible_month=date(2020, 1, 1),
        start_date=date(2019, 1, 1),
        end_date=date(2020, 1, 1),
        display_format = 'YYYY/MM/DD'
    ),
    html.Div(id='output-container-date-picker-range'),
    html.Div(children='''    
    Select your TICKER !!
    '''),
    dcc.Dropdown(
        id='cell-name-TICKER-column',
        options=[{'label': i, 'value': i} for i in availble_TICKER],
        value='AAPL'
    ),
    dcc.Dropdown(
        id='cell-name-indicator-column',
        options=[{'label': s, 'value': s} for s in ['Volume','Return(cum)','Close']],
        value='Volume'
    ),
    dcc.Graph(
        style={'height': 500},
        id='my-graph'
    ),
    html.Hr()
])

@app.callback(
    Output('my-graph', 'figure'),
    [Input('cell-name-TICKER-column', 'value'),
     Input('cell-name-indicator-column', 'value'),
     Input('my-date-picker-range', 'start_date'),
     Input('my-date-picker-range', 'end_date')])
def update_graph(TICKER_column_name, indicator, start_date, end_date):
    dff = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    return {
        'data': [dict(
            x=dff['Date'],
            y=dff[dff['TICKER'] == TICKER_column_name][indicator],
            mode='line'
        )],
    }

if __name__ == '__main__':
    app.run_server(debug=True)