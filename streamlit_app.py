import streamlit as st
import pandas as pd

# Function to read data and fill missing values
def read_data(file_path):
    data = pd.read_excel(file_path)
    return data

# Function to autofill missing values by record_id
def autofill(df, columns):
    for column in columns:
        df[column] = df.groupby('record_id')[column].ffill().bfill()
    return df

# Function to filter data and count non-blank records for each timepoint
def longitudinal_filter(data, timepoints, variables):
    results = {}

    for tp_name, tp_range in timepoints.items():
        tp_data = data[(data['days_since_surgery'] >= tp_range[0]) & (data['days_since_surgery'] <= tp_range[1])]
        counts = {var: tp_data[var].notna().sum() for var in variables}
        results[tp_name] = counts

    return results

# Main function to run Streamlit app
def main():
    # Streamlit title and subtitle
    st.title("Longitudinal Data Counter")
    st.write("This app counts non-blank record counts for variables across different timepoints.")

    # Load dataset and preprocess (replace with your file path)
    file_path = "path/to/your/PRODRSOMDashboardDat_DATA_2024-06-04_1845.xlsx"
    data = read_data(file_path)

    # Print column names for debugging
    st.write("Columns in data:", data.columns)

    # Autofill missing values by record_id
    data = autofill(data, ['sex_dashboard', 'graft_dashboard2', 'prior_aclr'])

    # Define variables to count non-blank records
    variables = [
        "insurance_dashboard_use", "ikdc", "pedi_ikdc", "marx", "pedi_fabs", "koos_pain",
        "koos_sx", "koos_adl", "koos_sport", "koos_qol", "acl_rsi", "tsk", "rsi_score",
        "rsi_emo", "rsi_con", "sh_lsi", "th_lsi", "ch_lsi", "lsi_ext_mvic_90",
        "lsi_ext_mvic_60", "lsi_flex_mvic_60", "lsi_ext_isok_60", "lsi_flex_isok_60",
        "lsi_ext_isok_90", "lsi_flex_isok_90", "lsi_ext_isok_180", "lsi_flex_isok_180",
        "rts", "reinjury"
    ]

    # Define timepoints
    timepoints = {
        '3-4 months': (90, 120),
        '5-7 months': (150, 210)
    }

    # Call longitudinal filtering function
    results = longitudinal_filter(data, timepoints, variables)

    # Display results in a table format
    st.subheader("Counts of Non-Blank Records for Variables:")
    results_df = pd.DataFrame(results).transpose()
    st.write(results_df)

# Run the app
if __name__ == "__main__":
    main()
