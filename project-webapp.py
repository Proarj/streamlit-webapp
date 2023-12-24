import streamlit as st
import pandas as pd
import altair as alt
import requests


def log_data(prompt, model):
    data_payload = {'user_prompt': prompt, 'model': model}
    response = requests.post('https://nestjs-backend-production-a269.up.railway.app/api/logData', json=data_payload)
    if response.status_code in {200, 201}:
        st.toast("Your prompt was successfully logged to the database")

def filter_and_display_data(model_value, total_token_operator, total_token_value, prompt_token_operator, prompt_token_value):
    data_payload = {
        'filter_model': model_value if model_value is not None else "",
        'filter_model': model_value if model_value is not None else "",
        'filter_operator_total_token': total_token_operator if total_token_operator is not None else "",
        'filter_total_tokens': total_token_value if total_token_value is not None else "",
        'filter_operator_prompt_token': prompt_token_operator if prompt_token_operator is not None else "",
        'filter_prompt_tokens': prompt_token_value if prompt_token_value is not None else ""
    }
    response = requests.post('https://nestjs-backend-production-a269.up.railway.app/api/DisplayFilterData', json=data_payload)
    if response.status_code in {200, 201}:
        filtered_data = pd.DataFrame(response.json())
        st.markdown(""" ## Filtered Data""")
        st.write(filtered_data)

def aggregate_data(aggregateMetric, start_datetime, end_datetime, aggregateMethod):
    data_payload = {
        'aggregate_metric': aggregateMetric,
        'start_datetime': start_datetime,
        'end_datetime': end_datetime,
        'aggregate_method': aggregateMethod if aggregateMethod is not None else ""
    }
    response = requests.post('https://nestjs-backend-production-a269.up.railway.app/api/AggregateValues', json=data_payload)
    if response.status_code in {200, 201}:
        st.markdown("""## aggregated value""")
        aggregated_data = pd.DataFrame(response.json())
        if(aggregateMetric == "Number Of Requests"):
            aggregated_value = aggregated_data['num_request'].iloc[0]
            st.write(f"Count = {aggregated_value}")
        else:
            aggregated_value = aggregated_data['aggregated_value'].iloc[0]
            st.write(f"{aggregateMethod} = {aggregated_value}")

import altair as alt

def visualize_data(time_period):
    response = requests.post('https://nestjs-backend-production-a269.up.railway.app/api/DisplayFilterData', json={})
    
    if response.status_code not in {200, 201}:
        st.write("Failed to fetch data")
        return
    
    df = pd.DataFrame(response.json())
    df['generated_at'] = pd.to_datetime(df['generated_at'])
    
    time_periods = {
        'Last 5 minutes': pd.Timedelta(minutes=5),
        'Last 30 minutes': pd.Timedelta(minutes=30),
        'Last 1 hour': pd.Timedelta(hours=1),
        'Last 6 hours': pd.Timedelta(hours=6),
        'Last 1 day': pd.Timedelta(days=1),
        'Last 2 days': pd.Timedelta(days=2)
    }
    
    if time_period not in time_periods:
        st.write("Invalid time period selection")
        return
    
    time_filtered = df[df['generated_at'] >= pd.Timestamp.now() - time_periods[time_period]]
    
    if time_filtered.empty:
        st.write("No data available for the selected time period")
        return

    # Plotting Requests per Second
    requests_per_second = time_filtered.resample('S', on='generated_at').size().reset_index()
    requests_per_second = requests_per_second.rename(columns={'generated_at': 'Time', 0: 'Requests per Second'})
    st.write('### Requests per Second')
    st.altair_chart(alt.Chart(requests_per_second).mark_line().encode(
        x='Time',
        y='Requests per Second',
        tooltip=['Time', 'Requests per Second']
    ), use_container_width=True)
    
    # Create a new DataFrame for plotting with time as the index
    filtered_data = time_filtered.set_index('generated_at')
    
    # Plotting other metrics
    metrics_to_plot = ['latency', 'total_tokens', 'completion_tokens']
    for metric in metrics_to_plot:
        if metric in filtered_data:
            st.write(f'### {metric.replace("_", " ").title()}')
            st.altair_chart(alt.Chart(filtered_data.reset_index()).mark_bar().encode(
                x='generated_at:T',
                y=alt.Y(f'{metric}:Q', axis=alt.Axis(title=metric.replace("_", " ").title())),
                tooltip=[alt.Tooltip('generated_at:T', title='Time'), alt.Tooltip(f'{metric}:Q', title=metric.replace("_", " ").title())]
            ), use_container_width=True)



            

st.markdown("""# Truefoundary Backend-Intern Assignment""")
with st.sidebar:
    st.markdown("## Filter Data")
    model_value = None
    total_token_operator = None
    total_token_value = None
    prompt_token_operator = None
    prompt_token_value = None 
    filter_model_check_box = st.checkbox("Model")
    if filter_model_check_box:
        model_value = st.selectbox("Name of the model", 
                     ('text-ada-001',
                      'text-babbage-001',
                      'text-curie-001',
                      'text-davinci-001',
                      'text-davinci-002',
                      'text-davinci-003',
                      'gpt-3.5-turbo-instruct'), placeholder="Model")

    filter_total_tokens_box = st.checkbox("Total Tokens")
    if filter_total_tokens_box:
        total_token_operator = st.selectbox("Total Token Operator", options=['<', '>', '=', '>=', '<='])
        total_token_value = st.number_input("Total Token Value", min_value= 1)
    filter_prompt_tokens_box = st.checkbox("Prompt Tokens")
    if filter_prompt_tokens_box:
        prompt_token_operator = st.selectbox("Prompt Token Operator", options=['<', '>', '=', '>=', '<='])
        prompt_token_value = st.number_input("Prompt Token Value", min_value= 1)
    filterAndDisplay = st.button("Filter And Display")
    st.markdown("""### Visualisation""")
    time_period = st.sidebar.selectbox('Select Time Period', ['Last 5 minutes','Last 30 minutes', 'Last 1 hour', 'Last 6 hours', 
                                                              'Last 1 day', 'Last 2 days'])
    visual = st.button("visual")
prompt_section, model_selection_section, log_data_button = st.columns(3)
with prompt_section:
    prompt = st.text_input("Prompt(Press Enter to apply)", "")
with model_selection_section:
    model = st.selectbox("Choose which model to use", 
                     ('text-ada-001',
                      'text-babbage-001',
                      'text-curie-001',
                      'text-davinci-001',
                      'text-davinci-002',
                      'text-davinci-003',
                      'gpt-3.5-turbo-instruct'), placeholder="Model")
with log_data_button:
    logData = st.button("Log Data")   
st.markdown("## Aggregation Functions")
aggregate_method_section, timestamp_section = st.columns(2)

with aggregate_method_section:
    aggregateMethod = None
    aggregateMetric = st.selectbox("Select Aggregate Metric", options=["Number Of Requests", "prompt_tokens", "total_tokens", "latency"])
    if aggregateMetric in ["prompt_tokens", "total_tokens"]:
        aggregateMethod = st.selectbox("Select Aggregate Method", options=["SUM", "AVG"])
    elif aggregateMetric == 'latency':
        aggregateMethod = st.selectbox("Select Aggregate Method", options=["AVG"])
    aggregate = st.button("Aggregate")

with timestamp_section:
    start_date = st.date_input("Start Date")
    start_time = st.time_input("Start Time")
    end_date = st.date_input("End Date")
    end_time = st.time_input("End Time")


if logData:
    log_data(prompt, model)

if filterAndDisplay:
    filter_and_display_data(model_value, total_token_operator, total_token_value, prompt_token_operator, prompt_token_value)

            
if aggregate:
    start_datetime = str(pd.to_datetime(str(start_date) + " " + str(start_time)))
    end_datetime = str(pd.to_datetime(str(end_date) + " " + str(end_time)))
    aggregate_data(aggregateMetric, start_datetime, end_datetime, aggregateMethod)
    
if visual:
    visualize_data(time_period)