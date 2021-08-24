import requests
import json
import pandas as pd
from time import sleep
import streamlit as st
# interact with FastAPI endpoint
backend = "http://127.0.0.1:8000/recommendation"


def process(num, server_url: str):

    data = json.dumps({"portfolio_val": num})

    r = requests.post(
        server_url, data=data, timeout=8000, verify=False
    )
    sleep(1)

    return r.json()


# construct UI layout
st.title("Stock Portfolio Recommendation")

st.subheader(
    """Obtain recomendation of stocks on the basis of Portfolio Optimization Techniques."""
)  # description and instructions

input_number = st.number_input("Enter the amount in $", format="%d")
num = int(input_number)

if st.button("Get Recommended Portfolio"):

    if input_number:
        output = process(num, backend)
        
        df = pd.json_normalize(output)
        portfolio_df = df.T
        portfolio_df = portfolio_df.reset_index()
        portfolio_df.columns = ['Ticker Symbol', 'Company_Name', 'Number of shares']
        st.dataframe(portfolio_df)

    else:
        st.write("Insert an numeric value in dollars!")