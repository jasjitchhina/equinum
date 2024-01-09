import openai
from openai import OpenAI
import streamlit as st
import os

# Instantiate the OpenAI client
client = openai.Client(api_key=st.secrets["OPENAI_API_KEY"])

def analyze_10k_filing(file_path):
    # Read the content of the 10-K filing
    with open(file_path, 'r') as file:
        content = file.read()

    # Prompt for the GPT model to analyze the document
    prompt = (
        "I need a detailed executive summary of the key financial and strategic insights from "
        "the following 10-K filing document. Highlight critical data points like revenue growth, "
        "profitability, risk factors, management discussion, market competition, future outlook, "
        "and any significant changes from the previous year. Please provide the information in a structured "
        "format with clear headings for each section:\n\n" + content
    )

    # Making a call to the OpenAI API with the prompt using the chat completions endpoint
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": prompt}]
    )

    # The analysis from the model
    analysis = response.choices[0].message.content.strip()

    return analysis

if __name__ == "__main__":
    # Path to the 10-K text file
    file_path = 'AAPL_10K.txt'
    
    # Get the analysis
    analysis_result = analyze_10k_filing(file_path)
    
    # Print the analysis
    print("Analysis of 10-K Filing:")
    print(analysis_result)
