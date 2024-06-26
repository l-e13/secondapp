import streamlit as st
import pandas as pd

# Function to read data and fill missing values
def read_data(file_path):
    try:
        data = pd.read_excel(file_path)
        return data
    except FileNotFoundError:
        st.error(f"File not found at path: {file_path}")
        return None
    except Exception as e:
        st.error(f"Error occurred while reading file: {e}")
        return None

# Function to autofill missing values by record_id
def autofill(df, columns):
    for column in columns:
        df[column] = df.groupby('record_id')[column].ffill().bfill()
    return df

# Function to filter data and count non-blank records for each timepoint
def longitudinal_filter(data, timepoints, variables):
    results = {}

    for tp_name, tp_range in timepoints.items():
        # Filter data for each timepoint range
        tp_data = data[(data['tss_dashboard'].isin(tp_range))]
        counts = {var: tp_data[var].notna().sum() for var in variables}
        results[tp_name] = counts

    return results

# Main function to run Streamlit app
def main():
    # Streamlit title and subtitle
    st.title("Longitudinal Data Counter")
    st.write("This app counts non-blank record counts for variables across different timepoints.")

    # Replace with your file path or URL
    file_path = "path/to/your/PRODRSOMDashboardDat_DATA_2024-06-04_1845.xlsx"
    
    # Load dataset and preprocess
    data = read_data(file_path)
    
    if data is None:
        return
    
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

    # Define timepoints based on tss_dashboard groups
    timepoints = {
        '3-4 months': ["3 to 4 months"],
        '5-7 months': ["5 to 7 months"],
        '8-12 months': ["8 to 12 months"],
        '13-24 months': ["13 to 24 months"]
        # Add more timepoint ranges as needed
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
