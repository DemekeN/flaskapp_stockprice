from flask import Flask,render_template,request, redirect
import requests
import os
import pandas as pd
from pandas import DataFrame,Series
from datetime import datetime
from datetime import timedelta
import bokeh
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models.annotations import Title
from bokeh.io import output_file, show


app = Flask(__name__)



def getdata(ticker): # Requsest a data from Alpha Vantage API and return dataframe and ticker symbol
    ticker=ticker.upper()
    key = os.environ.get('Api_key')
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={}&apikey={}'.format(ticker, key)
    response = requests.get(url).json() 
    name= response['Meta Data']['2. Symbol']
    response2 = response['Time Series (Daily)']
    data = pd.DataFrame.from_dict(response2, orient='index')
    df = data.rename(columns={'1. open':'open', '2. high':'high', '3. low':'low', '4. close':'close', '5. adjusted close':'adjusted close',
       '6. volume':'volume', '7. dividend amount':'dividend amount', '8. split coefficient':'split coefficient'})
    df.index = pd.to_datetime(df.index)
    df2 = df[df.index > datetime.today() - timedelta(days=32)]
    return(df2, name)

def makeplot(df2, tickerText): # input dataframe and ticker symbol and return plot script 
    p=figure(x_axis_type="datetime")
    p.line(df2.index, df2['close'],name ='Closing',line_color= "deepskyblue",line_width=2,legend_label= tickerText + "  closing price")
    #p.line(df2.index, df2['open'],name = "Opining price",line_color="blue",line_width=3,legend_label="Opening price")
    t = Title()
    t.text = 'Line graph of closing price of {} stock for the last 30 days'.format(tickerText)
    p.grid.grid_line_alpha=0.3
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Price'
    p.title = t
    bokeh.io.output_file('templates/graph.html')
    bokeh.io.save(p)
    script, div=components(p)
    return(script, div)
app.vars = {}

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/plotpage', methods=['post'])
def plotpage():
  tickstr = request.form['tickerText']
  app.vars['ticker']=tickstr.upper()
  df2,name=getdata(app.vars['ticker'])
  script,div=makeplot(df2,app.vars['ticker'])
  return render_template('graph.html', script=script, div=div, ticker=name)



if __name__ == '__main__':
  app.run(port=33507)