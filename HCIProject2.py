import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt
import streamlit as st
import python_forex_quotes
import requests
import datetime

client = python_forex_quotes.ForexDataClient("pnMq15vimGeiNubXJOqC40NViDWMysHF")

st.set_page_config(page_title="Forex Quotes",
                   initial_sidebar_state="expanded")

#Settings
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False


with st.sidebar:
    st.header("Settings")
    st.radio("Do you want your selectbox labels hidden?",
             key="visibility",
             options=["visible", "hidden", "collapsed"])


#Everything else
st.title("Forex Quotes")
st.subheader("Check over 700 pairs of foreign exchange rates from 1Forge.")
st.divider()

isMarketOpen = client.marketIsOpen()
if isMarketOpen == True:
    st.subheader("The Market is now: Open")
else:
    st.subheader("The market is now: Closed")

st.divider()


df = pd.read_json("data.json")

st.subheader("Exchange Rates")
pairList = client.getSymbols()
st.write("Select An Exchange Pair:")
ratePair = st.selectbox("Exchange Rates", pairList, index=None, placeholder="Select an exchange pair", label_visibility=st.session_state.visibility)

if ratePair:
    st.write(f"You selected:{ratePair}")
    baseCoin = ratePair[0:3]
    quoteCoin = ratePair[4:7]
else:
    st.info("You with get the base exchange rate, when you press Submit")

if st.button("Request Quote"):
    if not ratePair:
        st.warning("You need to select an exchange pair to continue")
    else:
        quote = client.getQuotes([ratePair])
        st.success(f"Every {baseCoin} is worth {quote[0]['b']} {quoteCoin}")
        df1 = pd.DataFrame(
            {
                "pair": [ratePair],
                "b": [baseCoin],
                "c": [quoteCoin],
                "t": [datetime.datetime.fromtimestamp(quote[0]["t"] / 1000).strftime('%Y-%m-%d %H:%M:%S')],
            }
        )
        df = pd.concat([df1, df], ignore_index=True)
        st.dataframe(
            df.head(10),
            column_config={
                "pair": "Pair",
                "b": "Base Coin",
                "c": "Quote Coin",
                "t": st.column_config.DatetimeColumn("Time")
            }
            )
        df.to_json("data.json")




st.divider()

st.subheader("Conversion")
currencyNames = []
for pair in pairList:
    if pair[0:3] not in currencyNames:
        currencyNames.append(pair[0:3])
    elif pair[4:6] not in currencyNames:
        currencyNames.append(pair[4:7])
st.write("Select two currencies:")
convert = st.multiselect("Conversions", currencyNames, default=None, placeholder="Select two currencies", label_visibility=st.session_state.visibility, max_selections=2)
if not convert:
    st.info("Select the base currency, and then the currency you want to convert to.")
elif len(convert) == 1:
    st.write("You selected:")
    for i in convert:
        st.write(i)
else:
    st.write("You selected:")
    for i in convert:
        st.write(i)

    if f"{convert[0]}/{convert[1]}" not in pairList:
        st.warning("This conversion is not available, you may want to select another one.")

    amount = st.number_input("Input how much you want to convert", label_visibility=st.session_state.visibility)
    c = st.button("Convert")
    if c and amount:
        if f"{convert[0]}/{convert[1]}" not in pairList:
            st.error("I'm sorry, this conversion is not available, please select another one.")
        else:
            conversion = client.convert(convert[0], convert[1], amount)
            st.success(conversion["text"] + ".")




st.divider()

st.subheader("Chili")

st.write("In this section, you will show your interest in Chili.")
chili = st.checkbox("Select if you want Chili.")
if not chili:
    st.info("If you do not check this box, you won't get Chili.")

wantChili = st.button("Get Chili")
if wantChili and chili == True:
    df = pd.DataFrame(
        {
            "col1": [44.626900],
            "col2": [-90.356400],
        }
    )
    st.map(df, latitude="col1", longitude="col2")
elif wantChili and chili == False:
    st.error("You did not check the box for Chili, you don't get Chili :(")






# Show Request Usage
st.divider()
st.subheader("API Usage")
if st.button("Get Request Usage"):
    usage = client.quota()
    quotaRemaining = usage["quota_remaining"]
    quotaLimit = usage["quota_limit"]
    timeUntilReset = usage["hours_until_reset"]
    chart_data = pd.DataFrame(
        {
            "Requests": ["quota_used", "quota_limit"],
            "Number": [usage["quota_used"], quotaLimit]
        }
    )
    st.write(f"The number of Requests you have left are {quotaRemaining}, and the time until reset is {timeUntilReset} hours")
    st.bar_chart(chart_data, y="Number", x="Requests", color="Requests")
