import streamlit as st
import pandas as pd

# Function to fill missing values for each record id
def autofill(df, columns):
    for column in columns:
        df[column] = df.groupby('record_id')[column].ffill().bfill()
    return df

# Function to count non-null observations for each variable at each timepoint
def longitudinal_filter(df, timepoint_col, variables):
    # Assuming timepoint_col is a column in your dataset that denotes the timepoint
    grouped = df.groupby(timepoint_col)
    result = {}
    
    for timepoint, group_data in grouped:
        counts = {}
        for var in variables:
            counts[var] = group_data[var].notna().sum()
        result[timepoint] = counts
    
    return result

# Main Streamlit app code
def main():
    st.title("Longitudinal Data Counter")  # Title
    st.write("This app counts non-blank record counts for variables at each timepoint.")

    # Upload dataset
    data = pd.read_excel("PRODRSOMDashboardDat_DATA_2024-06-04_1845.xlsx")

    # Print column names for debugging
    st.write("Columns in data:", data.columns)

    # Function to autofill missing values for specified columns
    data = autofill(data, ['sex_dashboard', 'graft_dashboard2', 'prior_aclr'])

    # Example variables (replace with your actual list of variables)
    variables = [
        "insurance_dashboard_use", "ikdc", "pedi_ikdc", "marx", "pedi_fabs", "koos_pain", 
        "koos_sx", "koos_adl", "koos_sport", "koos_qol", "acl_rsi", "tsk", "rsi_score", 
        "rsi_emo", "rsi_con", "sh_lsi", "th_lsi", "ch_lsi", "lsi_ext_mvic_90", 
        "lsi_ext_mvic_60", "lsi_flex_mvic_60", "lsi_ext_isok_60", "lsi_flex_isok_60", 
        "lsi_ext_isok_90", "lsi_flex_isok_90", "lsi_ext_isok_180", "lsi_flex_isok_180", 
        "rts", "reinjury"
    ]

    # Ask for filter criteria (e.g., timepoint column)
    timepoint_col = st.selectbox("Select timepoint column", options=data.columns)
    if timepoint_col:
        # Calculate counts for each variable at each timepoint
        longitudinal_counts = longitudinal_filter(data, timepoint_col, variables)

        # Display results in a table format
        st.write("Counts of Non-Null Observations for Variables at Each Timepoint:")
        for timepoint, counts in longitudinal_counts.items():
            st.subheader(f"Timepoint: {timepoint}")
            df_counts = pd.DataFrame.from_dict(counts, orient='index', columns=['Count'])
            st.write(df_counts)

# Run the main function
if __name__ == "__main__":
    main()
