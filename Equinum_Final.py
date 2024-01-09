import yfinance as yf
import streamlit as st
import plotly.graph_objs as go
from datetime import datetime
import pytz
from Analysis_Alpha import analyze_10k_filing 
from SEC_Scrape_Alpha import scrape_sec_filings

def get_historical_data(ticker, period='1d', interval='1m'):
    stock = yf.Ticker(ticker)
    if period == '1d':
        data = stock.history(period=period, interval='15m')
    else:
        data = stock.history(period=period)
    return data

def plot_stock_data(data, title):
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                                         open=data['Open'],
                                         high=data['High'],
                                         low=data['Low'],
                                         close=data['Close'])])
    fig.layout.update(title=title, xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)

def display_stock_info(stock):
    info = stock.info
    
    # Display key stock information in a more structured format
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("General Info")
        st.write(f"**Ticker**: {info['symbol']}")
        st.write(f"**Name**: {info['longName']}")
        st.write(f"**Sector**: {info['sector']}")
        st.write(f"**Industry**: {info['industry']}")
        st.write(f"**Website**: [Link]({info['website']})")
        st.write(f"**Phone**: {info['phone']}")

    with col2:
        st.subheader("Financial Info")
        st.write(f"**Market Cap**: {info.get('marketCap', 'N/A')}")
        st.write(f"**Dividend Rate**: {info.get('dividendRate', 'N/A')}")
        st.write(f"**Dividend Yield**: {info.get('dividendYield', 'N/A')}")
        st.write(f"**P/E Ratio**: {info.get('trailingPE', 'N/A')}")
        st.write(f"**Beta**: {info.get('beta', 'N/A')}")

    # Display additional information in an expander with better formatting
    with st.expander("More Info"):
        st.write(f"**Address**: {info['address1']}, {info['city']}, {info['state']}, {info['zip']}, {info['country']}")
        st.write(f"**Full-Time Employees**: {info['fullTimeEmployees']}")
        st.write("### Company Officers")
        for officer in info['companyOfficers']:
            st.write(f"- {officer['name']}, {officer['title']}")

        st.write("### Financial Highlights")
        st.write(f"**Previous Close**: {info['previousClose']}")
        st.write(f"**Open**: {info['open']}")
        st.write(f"**Day's Low**: {info['dayLow']}")
        st.write(f"**Day's High**: {info['dayHigh']}")
        # Add more fields as needed

def display_latest_news(stock):
    news_items = stock.news
    try: 
        if news_items:
            st.sidebar.header(f"Latest News for {stock.info['shortName']}")
            for news in news_items[:5]:  # Display up to 5 news items
                publish_time = datetime.fromtimestamp(news['providerPublishTime'], tz=pytz.timezone('UTC'))
                readable_time = publish_time.strftime('%Y-%m-%d %H:%M:%S %Z')

                st.sidebar.subheader(news['title'])
                st.sidebar.caption(f"Published by {news['publisher']} on {readable_time}")
                st.sidebar.markdown(f"[Read more]({news['link']})", unsafe_allow_html=True)
                st.sidebar.write("---")  # Separator line
        else:
           st.sidebar.write("No news available.")
    
    except Exception as e:
        st.sidebar.write(f"Error fetching news: {e}")



def main():
    st.title('Equinum - Analytics for Everyone')
    ticker = st.text_input("Enter the stock ticker symbol:", 'AAPL')

    if ticker:
        stock = yf.Ticker(ticker)

        # Check if the ticker symbol is valid
        if not valid_ticker(stock):
            st.error("Invalid stock ticker symbol. Please enter a correct ticker.")
            return  # Stop further execution for invalid ticker

        display_latest_news(stock)


        # Time frame selection for historical data
        time_frame = st.selectbox("Select Time Frame", ['1d', '5d', '1mo', 'ytd'])
        if time_frame == '1d':
            data = get_historical_data(ticker, period=time_frame, interval='15m')
        else:
            data = get_historical_data(ticker, period=time_frame)

        # Plotting the stock price data
        if not data.empty:
            plot_stock_data(data, f"{ticker} Stock Price - {time_frame.upper()}")
        
        # Display stock information after the chart
        display_stock_info(stock)

        if st.button('Analyze Latest 10-K Filing'):
            with st.spinner('Fetching and analyzing 10-K filing...'):
                try:
                    file_path, filing_url = scrape_sec_filings(ticker)
                    if file_path and filing_url:
                        analysis_result = analyze_10k_filing(file_path)
                        st.subheader("10-K Filing Analysis:")
                        st.markdown(f"[View SEC Filing]({filing_url})", unsafe_allow_html=True)
                        st.text_area("Analysis Result", analysis_result, height=300)
                    else:
                        st.error("Failed to retrieve the 10-K filing.")
                except Exception as e:
                    st.error(f"Error during analysis: {e}")
def valid_ticker(stock):
    """
    Check if the given stock ticker is valid.
    """
    try:
        # Try fetching a simple attribute to test validity
        _ = stock.info['symbol']
        return True
    except (KeyError, ValueError, Exception):
        return False


if __name__ == "__main__":
    main()