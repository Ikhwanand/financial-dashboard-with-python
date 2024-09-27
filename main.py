import math 
import datetime as dt 

import numpy as np 
import yfinance as yf 

from bokeh.io import curdoc 
from bokeh.plotting import figure 
from bokeh.layouts import column, row
from bokeh.models import TextInput, Button, DatePicker, MultiChoice


def load_data(ticker1, ticker2, start, end):
    """ 
    Load stock data from Yahoo Finance for two tickers within a specific time range.

    Parameters
    ----------
    ticker1 : str
        The first ticker symbol to download.
    ticker2 : str
        The second ticker symbol to download.
    start : str
        The start date in 'YYYY-MM-DD' format.
    end : str
        The end date in 'YYYY-MM-DD' format.

    Returns
    -------
    df1, df2 : pandas.DataFrame
        DataFrames of historical market data for the two tickers.
    """
    df1 = yf.download(ticker1, start=start, end=end)
    df2 = yf.download(ticker2, start=start, end=end)
    return df1, df2 


def plot_data(data, indicators, sync_axis=None):
    """
    Plot stock data as candlestick plot with given indicators.

    Parameters
    ----------
    data : pandas.DataFrame
        DataFrame of historical market data.
    indicators : List[str]
        List of indicators to include in the plot.
    sync_axis : bokeh.plotting.Figure, optional
        If given, the x-axis range of the returned figure is synchronized with the given figure.

    Returns
    -------
    bokeh.plotting.Figure
        Figure of the stock data with given indicators.
    """
    df = data.copy()
    gain = df.Close > df.Open
    loss = df.Close < df.Open
    width = 12 * 60 * 60 * 1000  # half day in ms
    
    if sync_axis:
        p = figure(x_axis_type='datetime', tools='pan, wheel_zoom, box_zoom, reset, save', width=1000,
                   x_range=sync_axis)
    else:
        p = figure(x_axis_type='datetime', tools='pan, wheel_zoom, box_zoom, reset, save', width=1000)
    
    p.xaxis.major_label_orientation = math.pi / 4
    p.grid.grid_line_alpha = .25
    
    p.segment(df.index, df.High, df.index, df.Low, color='black')
    p.vbar(df.index[gain], width, df.Open[gain], df.Close[gain], fill_color='#00ff00', line_color='#00ff00')
    p.vbar(df.index[loss], width, df.Open[loss], df.Close[loss], fill_color='#ff0000', line_color='#ff0000')
    
    for indicator in indicators:
        if indicator == '30 Day SMA':
            df['SMA30'] = df['Close'].rolling(30).mean()
            p.line(df.index, df.SMA30, color='purple', legend_label='30 Day SMA')
        elif indicator == '100 Day SMA':
            df['SMA100'] = df['Close'].rolling(30).mean()
            p.line(df.index, df.SMA100, color='blue', legend_label='100 Day SMA')
        elif indicator == 'Linear Regression Line':
            per = np.polyfit(range(len(df.index.values)), df.Close.values, 1, full=True)
            slope = per[0][0]
            intercept = per[0][1]
            y_pred = [slope * i + intercept for i in range(len(df.index.values))]
            p.segment(df.index[0], y_pred[0], df.index[-1], y_pred[-1], legend_label='Linear Regression', color='red')
        
        p.legend.location = 'top_left'
        p.legend.click_policy = 'hide'
    
    return p


def on_button_click(ticker1, ticker2, start, end, indicators):
    
    """
    Callback for button click.

    Loads data for two tickers between two dates, plots the data, and displays the plots.

    Args:
        ticker1 (str): The first ticker to load.
        ticker2 (str): The second ticker to load.
        start (str): The start date in 'YYYY-MM-DD' format.
        end (str): The end date in 'YYYY-MM-DD' format.
        indicators (List[str]): A list of indicators to include in the plots.
    """
    df1, df2 = load_data(ticker1, ticker2, start, end)
    p1 = plot_data(df1, indicators)
    p2 = plot_data(df2, indicators, sync_axis=p1.x_range)
    curdoc().clear()
    curdoc().add_root(layout)
    curdoc().add_root(row(p1, p2))
    


stock1_text = TextInput(title='Stock 1')
stock2_text = TextInput(title='Stock 2')
date_picker_from = DatePicker(title='Start Date', 
                              value='2020-01-01', 
                              min_date='2000-01-01', 
                              max_date=dt.datetime.now().strftime('%Y-%m-%d')
                              )
date_picker_to = DatePicker(title='End Date', 
                              value='2020-01-01', 
                              min_date='2000-01-01', 
                              max_date=dt.datetime.now().strftime('%Y-%m-%d')
                              )

indicator_choice = MultiChoice(options=['100 Day SMA', '30 Day SMA', 'Linear Regression Line'])

load_button = Button(label='Load Data', button_type='success')
load_button.on_click(lambda: on_button_click(stock1_text.value,
                                             stock2_text.value,
                                             date_picker_from.value,
                                             date_picker_to.value,
                                             indicator_choice.value))

layout = column(stock1_text, stock2_text, date_picker_from, date_picker_to, indicator_choice, load_button)

curdoc().clear()
curdoc().add_root(layout)

