import streamlit as st 
import pandas as pd 
import altair as alt
import plotly.express as px 
import plotly.graph_objects as go

import pymongo
import numpy as np
import yfinance as yf
from dotenv import load_dotenv
load_dotenv()
import os
import time
from datetime import datetime
import personal_portfolio.scrap as scrap


risk_free_rate = 0.07
user_name = os.getenv('username')
pswd = os.getenv('password')

st.markdown("<h1 style='text-align: center;'>Personal Portfolio</h1>", unsafe_allow_html=True)
# uri = f'mongodb+srv://{user_name}:{pswd}@cluster0.2ynjkbv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
uri = 'mongodb+srv://sahil45:Sahil8733@cluster0.2ynjkbv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
client = pymongo.MongoClient(uri)

try:
    client.admin.command('ping')
    print('Pinged your deployment')
except Exception as e:
    print(e)

db = client['stocks']
stocks_info = db['stocks_info']
trades = db['trades']
portfolio = db['portfolio']
#get all the stocks list
stocks_list = []
invested_stocks = []
results = stocks_info.find({},{'Ticker':1,'_id':0})
invested_stocks_res = trades.find({},{'Ticker':1,'_id':0})

placeholder1=st.empty()
#Function to extract info about new equity entered by user
def extract_info(ticker):
  yf_ticker = yf.Ticker(ticker)
  info = yf_ticker.info
  dividends = pd.DataFrame(yf_ticker.dividends)
  dividends.reset_index(inplace=True)
  stocks_info.insert_one({'Ticker':ticker,'Industry':info.get('industry','NA'),'Sector':info.get('sector','NA'),'DividendRate':info.get('dividendRate','NA'),
                          'DividendYield':info.get('dividendYield','NA'),
                          'Last_Dividend_Date':datetime.fromtimestamp(info.get('lastDividendDate',0)).strftime('%Y-%m-%d'),
                          'Last_Dividend':info.get('lastDividendValue','NA'),'PE_Ratio':info.get('trailingPE','NA'),'BookValue':info.get('bookValue','NA'),'MarketCap':info.get('marketCap','NA'),
                          'PB_Ratio':info.get('priceToBook','NA'),'EPS':info.get('trailingEps','NA'),'Revenue':info.get('revenueGrowth','NA'),'ProfitMargin':info.get('profitMargins','NA'),
                          'DebtToEquity':info.get('debtToEquity','NA')
                          })
#To check the entire equity list
for result in results:
    stocks_list.append(result.get('Ticker'))
while '' in stocks_list:
    ind = stocks_list.index('')
    stocks_list.pop(ind)
#To keep check of the invested stocks
stocks_list = list(set(stocks_list))
print(stocks_list)
for invested_stock in invested_stocks_res:
    invested_stocks.append(invested_stock.get('Ticker'))
    


col1, col2, col3= st.columns(3)
with col1:
    ticker = st.text_input(label = '**Stock Ticker**',placeholder='Example-SAIL.NS for SAIL',key = 'ticker')

    # if ticker not in stocks_list:
    #     extract_info(ticker)
with col2:
    num_stock = st.number_input(label = '**Number of stocks purchased**',placeholder='Eg.: -5 for sell',key = 'num_stock',value = None)
with col3:
    avg_value = st.number_input(label= '**Average Buy/Sell Price**',value = None,step = 0.05)
if ticker and num_stock and avg_value:
    col21, col22 = st.columns([2,1])
    with col21:
        if st.button(':green[Buy]',key='buy'):
            trades.insert_one({'Ticker':ticker,'no._shares':num_stock,'avg_value':avg_value})
            with st.spinner("Loading..."):
                time.sleep(3.5)
            st.write("Trade Saved :white_check_mark:") 

        
    with col22:
        if st.button(':red[Sell]',key='sell'):
            trades.insert_one({'Ticker':ticker,'no._shares':-num_stock,'avg_value':avg_value})
            with st.spinner("Loading..."):
                time.sleep(3.5)
            st.write("Trade Saved :white_check_mark:") 


# def handle_submit():
    
#     if ticker and num_stock and avg_value and (st.session_state.buy) :
#         trades.insert_one({'Ticker':ticker,'no._shares':num_stock,'avg_value':avg_value})
#         # st.session_state.ticker = ''
        
        
#     elif ticker and num_stock and avg_value and (st.session_state.sell) :
#         trades.insert_one({'Ticker':ticker,'no._shares':-num_stock,'avg_value':avg_value})
#         # st.session_state.ticker = ''
    
        
#     else:
#         # st.write('Please Enter all 3 inputs')
#         # st.session_state.ticker=''
        
#         return False
    
    

# col21, col22 = st.columns([2,1])
# with col21:
#     if st.button(':green[Buy]',on_click = handle_submit,key='buy'):
#         with st.spinner("Loading..."):
#             time.sleep(3.5)
#         st.write("Trade Saved :white_check_mark:") 

    
# with col22:
#     if st.button(':red[Sell]',on_click = handle_submit,key='sell'):
#         with st.spinner("Loading..."):
#             time.sleep(3.5)
#         st.write("Trade Saved :white_check_mark:") 


# st.markdown('</div>', unsafe_allow_html=True)



# # Display the selected option

def aggregated_trades():
    pipeline = [
        {
            '$group':{
                '_id':'$Ticker',
                'hold_shares':{'$sum':{'$getField':'no._shares'}},
                'average_value':{'$sum':{'$multiply':[{'$getField':'no._shares'},'$avg_value']}}
            }
        },
        {
            '$match':{'hold_shares':{'$gt':0}}
        },
        {
            '$project':{
                '_id':0,
                'Ticker':'$_id',
                'hold_shares':1,
                'average_value':{
                    '$divide':['$average_value','$hold_shares']
                }
            }
        }
    ]
    aggregated_data = list(trades.aggregate(pipeline))
   
    if aggregated_data:
        portfolio.delete_many({})
        portfolio.insert_many(aggregated_data)


def invested():
    res = trades.aggregate([
    {
        '$group':{
            '_id':'$Ticker',
            'hold_shares':{'$sum':{'$getField':'no._shares'}},
            'invested':{'$sum':{'$multiply':[{'$getField':'no._shares'},'$avg_value']}}
        }},
    {
         '$match':{'hold_shares':{'$gt':0}}
    },
    {
        '$group':{
            '_id':None,
            'total_invested':{'$sum':'$invested'}
        }
    }
    ])
    res = list(res)
    return res[0].get('total_invested',0)

total_invested = invested()
def weights_calc(total_invested):
    port_res = portfolio.find({})
    weights_p = {}
    for i in port_res:
        tot_invest = i['hold_shares']*i['average_value']
        weights_p[i['Ticker']] = round(tot_invest/total_invested,2)
    return weights_p

weights = weights_calc(total_invested)
def func_sharpe_ratio(weights,risk_free_rate,start_date,end_date):
    equity = list(weights.keys())
    f_data = yf.download(equity,start = start_date,end = end_date)['Adj Close']
    returns = f_data.pct_change().dropna()
    p_weights = list(weights.values())
    portfolio_returns = (returns*p_weights).sum(axis = 1)
    portfolio_mean_return = portfolio_returns.mean()
    portfolio_std_return = portfolio_returns.std()
    f_sharpe_ratio = (portfolio_mean_return - risk_free_rate)/(portfolio_std_return)
    return f_sharpe_ratio

sharpe_ratio = func_sharpe_ratio(weights,risk_free_rate,'2018-01-01',datetime.today())
def diversification_ratio(weights,start_date,end_date):
    equity = list(weights.keys())
    d_data = yf.download(equity,start = start_date,end = end_date)['Adj Close']
    returns = d_data.pct_change().dropna()
    volatilities = returns.std()*np.sqrt(252)
    p_weights = np.array(list(weights.values()))
    weighted_vol = np.dot(p_weights,volatilities)
    cov_matrix = returns.cov()*252
    portfolio_volatility = np.sqrt(np.dot(p_weights.T,np.dot(cov_matrix,p_weights)))
    diversification_ratio = round(weighted_vol/portfolio_volatility,2)
    return [diversification_ratio,portfolio_volatility]

diverse_ratio,portfolio_volatility = diversification_ratio(weights,'2018-01-01',datetime.today())


# from streamlit_card import card

# def curr_price(stock_list):
#     stock_list = list(set(stock_list))
#     curr_price = db['curr_price']
#     for stock in stock_list:
#         yf_ticker = yf.Ticker(stock)
#         ctp = yf_ticker.info.get('currentPrice',0)
#         curr_price.insert_one({'Ticker':ticker,'currentPrice':ctp})
# if ticker:
#     curr_price(stocks_list)
aggregated_trades()
def profit():
    res = portfolio.find({},{'Ticker':1,'hold_shares':1,'average_value':1})
    profit = 0
    for i in res:
        ticker = i['Ticker']
        yf_ticker = yf.Ticker(ticker)
        p = yf_ticker.history('1d')
        d = p['Close'].to_list()
        curr_price=round(d[0],2)
        avg_value = i['average_value']
        
        profit+=(curr_price-avg_value)*i['hold_shares']
    return profit
profit_got = profit()   

# col31, col32 = st.columns([1,5])
# with col31:
#     hasClicked = card(
#   title="Investment",
#   text=str(total_invested),
  
# )
# with col32:
#     hasClicked = card(
#     title="Profit",
#     text=str(profit_got),
    
#     )
# st.markdown("""
# <style>
#             [data-testid = 'stMetric']{
#             background-color: white;
#             text-align: center;
#             padding: 5% 5% 5% 10%;
#             left = 10%;
#             color: white;
#             justify-content:center
#             }
# </style>

# """, unsafe_allow_html=True
# )
# st.metric(label='**Invested**',value = total_invested)
metric_style = """
    <style>
    div[data-testid="metric-container"] {
        background-color: #343833; /* Background color */
        border: 1px solid #ddd;
        padding: 10px;
        border-radius: 5px;
        color: white; /* Font color for the container */
    }
    div[data-testid="metric-container"] > label,
    div[data-testid="metric-container"] > div > div {
        color: white; /* Font color for labels and values */
    }
    </style>
    """

# Display custom CSS
st.markdown(metric_style, unsafe_allow_html=True)
with placeholder1:
    col31, col32 = st.columns([3,1])
    with col31:
        st.metric(label="Investment(in ₹)", value=total_invested)
    with col32:
        st.metric(label="Profit", value=profit_got, delta=str(round((profit_got/total_invested)*100,2))+'%')
    # Example st.metric usage
    # st.metric(label="Investment", value=total_invested, delta="1.2°C")
    # st.metric(label="Profit", value=profit_got, delta=round((profit_got/total_invested)*100,2))
def count_sector():
    portfolio = db['portfolio']
    res = portfolio.aggregate([
        {
            '$lookup':{
                'from':'stocks_info',
                'localField':'Ticker',
                'foreignField':'Ticker',
                'as':'stocks_info'
            }
        },
        {
            '$unwind':{
                'path':'$stocks_info',
                'preserveNullAndEmptyArrays':True
            }
        },
        {
            '$project':{
                'Ticker':1,
                'Sector':'$stocks_info.Sector'
            }
        }
    ])
    ans = []
    for i in res:
        ans.append(i['Sector'])
    return ans
placeholder2 = st.empty()
with placeholder2:
    col51,col52,col53 = st.columns(3)
    with col51:
        st.metric(label = '**Sharpe Ratio**', value = round(sharpe_ratio,2))
    with col52:
        st.metric('**Annualised Volatility**',value = f'{round(portfolio_volatility*100,2)}%')
    with col53:
        st.metric('**Diversification Ratio**',value = round(diverse_ratio,2))
        with st.expander("More Info"):
            ans = count_sector()
            ans = list(set(ans))
            df = pd.DataFrame(ans,columns = ['Sector'])
            st.write(f"Sector : {len(ans)}")
            st.table(df)

def get_stock_data(selected_option,interval):
    data = yf.download(selected_option,interval = interval,progress = False)
    return data



def plot_candlestick(data):
    fig = go.Figure(data = [go.Candlestick(x = data.index,
                                           open = data['Open'],
                                           high = data['High'],
                                           low = data['Low'],
                                           close = data['Close'])])
    fig.update_layout(title = f'Candlestick Chart for {selected_option}',
                      xaxis_rangeslider_visible=True)
    st.plotly_chart(fig,use_container_width=True)

with st.sidebar:
    selected_option = st.selectbox("**Explicit Stock View:**", stocks_list,index = None,placeholder='Explore Equity')
    timeframe = st.selectbox('Timeframe',['1m','2m','5m','1d','5d','1mo','6mo','1y','5y','max'],index = None)
    info = list(db.stocks_info.find({'Ticker':selected_option}))
    if info:
        html_template = """
<div style= padding: 10px; border-radius: 5px; display: inline-block; text-align: center;">
    <div style="font-size: 16px; color: black;">{label}</div>
    <div style="font-size: 24px; font-weight: bold; margin-top: 5px;">{value}</div>
    
</div>
"""
        def metric(label, value):
            html_content = html_template.format(label=label, value=value)
            st.markdown(html_content, unsafe_allow_html=True)
        col61,col62 = st.columns(2)
        with col61:
            metric(label = 'MarketCap(₹Crores)',value = round(info[0]['MarketCap']/10**7,2))
        with col62:
            metric(label = 'PE Ratio',value = round(info[0]['PE_Ratio'],2))
        col71,col72 = st.columns(2)
        with col71:
            metric(label = 'EPS',value = round(info[0]['EPS'],2))
        with col72:
            metric(label = 'Profit Margin',value = f'{round(info[0]['ProfitMargin']*100,2)}%')
        col81,col82 = st.columns(2)
        with col81:
            metric(label = 'Book Value',value = round(info[0]['BookValue'],2))
        with col82:
            metric(label = 'PB Ratio',value = round(info[0]['PB_Ratio'],2))
        col91,col92 = st.columns(2)
        with col91:
            if info[0]['DividendRate']=='NA' or type(info[0]['DividendRate'])==str:
                metric(label = 'Dividend Rate',value = info[0]['DividendRate'])
            else:
                metric(label = 'Dividend Rate',value = f'{round(info[0]['DividendRate'],2)}%')
        with col92:
            if info[0]['Last_Dividend']=='NA' or type(info[0]['Last_Dividend'])==str:
                metric(label = 'Last Dividend',value = info[0]['Last_Dividend'])
            else:
                metric(label = 'Last Dividend', value = f'₹{round(info[0]['Last_Dividend'],2)}')
        
        metric(label = 'Last Dividend Date',value = info[0]['Last_Dividend_Date'])
        
if selected_option and timeframe:
    data = get_stock_data(selected_option,timeframe)
    plot_candlestick(data)
    # stock_res = list(portfolio.find({'Ticker':selected_option}))
    # if stock_res:
    #     stock_res = stock_res[0]
    #     curr_price = round(yf.Ticker(selected_option).info['currentPrice'],2)
    #     invested_stock = stock_res['average_value']*stock_res['hold_shares']
    #     profit_stock = (curr_price-stock_res['average_value'])*stock_res['hold_shares']
    #     col41, col42, col43, col44 = st.columns(4)
    #     name = selected_option.replace('.NS','')
    #     with col41:
    #         st.metric(label = f'**CMP({name})**',value = curr_price)
    #     with col42:
    #         st.metric(label = f'**Shares Holded({name})**',value = stock_res['hold_shares'])
    #     with col43:
    #         st.metric(label="**Investment(in ₹)**", value=invested_stock)
    #     with col44:
    #         st.metric(label="Profit(in ₹)", value=profit_stock, delta=str(round((profit_got/total_invested)*100,2))+'%')

if selected_option:
    stock_res = list(portfolio.find({'Ticker':selected_option}))
    if stock_res:
        stock_res = stock_res[0]
        curr_price = round(yf.Ticker(selected_option).info['currentPrice'],2)
        invested_stock = stock_res['average_value']*stock_res['hold_shares']
        profit_stock = (curr_price-stock_res['average_value'])*stock_res['hold_shares']
        col41, col42, col43, col44 = st.columns(4)
        name = selected_option.replace('.NS','')
        with col41:
            st.metric(label = f'**CMP({name})**',value = curr_price)
        with col42:
            st.metric(label = f'**Shares Holded({name})**',value = stock_res['hold_shares'])
        with col43:
            st.metric(label="**Investment(in ₹)**", value=invested_stock)
        with col44:
            st.metric(label="Profit(in ₹)", value=profit_stock, delta=str(round((profit_stock/invested_stock)*100,2))+'%')
    
    name = yf.Ticker(selected_option).info['longName']
    st.title('Latest News for'+' '+name)
    news_articles = scrap.google_scrape(name)
    for k,v in news_articles.items():
        url = v[1]
        text = v[0]
        st.write(text,"[link](%s)" % url)
html_template = """
<div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; display: inline-block; text-align: center;">
    <div style="font-size: 16px; color: grey;">{label}</div>
    <div style="font-size: 24px; font-weight: bold; margin-top: 5px;">{value}</div>
    <div style="font-size: 16px; color: {delta_color}; margin-top: 5px;">{delta}</div>
</div>
"""

def metric(label, value, delta, delta_color="green"):
    html_content = html_template.format(label=label, value=value, delta=delta, delta_color=delta_color)
    st.markdown(html_content, unsafe_allow_html=True)
