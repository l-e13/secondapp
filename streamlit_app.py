import streamlit as st
import pandas as pd
import hmac

# Password function
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # deletes password 
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    # Ask user for password
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False

if not check_password():
    st.stop()  # Do not continue if password is wrong

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

# Function to apply basic filters and count non-blank records
def filter_count(df, cols, variables):
    filtered_df = df.copy()
    for column, values in cols.items():  # Iterates through each filter
        if column in ['age', 'tss']:
            filtered_df = filtered_df[filtered_df[column].between(values[0], values[1])]
        elif values:  # Only apply filter if values are not empty
            filtered_df = filtered_df[filtered_df[column].isin(values)]

    # Count non-blank records for each variable
    non_blank_counts = {var: filtered_df[var].notna().sum() for var in variables} 
        
    return non_blank_counts, filtered_df

# Function to perform longitudinal filtering
def longitudinal_filter(data, timepoints, variables):
    results = {}

    for tp_name, tp_range in timepoints.items():
        # Filter data for each timepoint range
        tp_data = data[data['tss_dashboard'].isin(tp_range)]
        counts = {var: tp_data[var].notna().sum() for var in variables}
        results[tp_name] = counts

    return results

# Main function for Streamlit app
def main():
    # Streamlit title and subtitle
    st.title("ARROW Data Counter with Longitudinal Filtering")
    st.write("This app counts non-blank record counts for variables given specified criteria and longitudinal timepoints.")

    # Replace with your file path or URL
    file_path = "PRODRSOMDashboardDat_DATA_2024-06-04_1845.xlsx"
    
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

    # Ask for filter criteria
    st.subheader("Enter criteria:")
    cols = {}

    # Filters with subgroups
    filter_columns = {
        "Participant Sex": ["Female", "Male"],
        "Graft Type": ["Allograft", "BTB autograft", "HS autograft", "Other", "QT autograft"],
        "Prior ACL?": ["Yes", "No"]
    }

    # Make drop-down selections for each filter
    for column, options in filter_columns.items():
        if column == "Prior ACL?":
            selected_values = st.multiselect(f"Select value/s for '{column}'", options) 
            selected_values = [1 if v == "Yes" else 0 for v in selected_values]  # Converting yes/no to 1/0
            if selected_values:  # Only add to cols if not empty
                cols['prior_aclr'] = selected_values  # Correct column name
        elif column == "Participant Sex":
            selected_values = st.multiselect(f"Select value/s for '{column}'", options)
            if selected_values:  # Only add to cols if not empty
                cols['sex_dashboard'] = selected_values  # Correct column name
        elif column == "Graft Type":
            selected_values = st.multiselect(f"Select value/s for '{column}'", options)
            if selected_values:  # Only add to cols if not empty
                cols['graft_dashboard2'] = selected_values  # Correct column name

    # Add age range slider
    age_min = int(data['age'].min())  # Min age in dataset
    age_max = int(data['age'].max())  # Max age in dataset
    age_range = st.slider("Select age range", min_value=age_min, max_value=age_max, value=(age_min, age_max), step=1)  # Slider widget with integer step
    cols['age'] = age_range

    # Add tss range slider
    tss_min = int(data['tss'].min())  # Min tss in dataset
    tss_max = int(data['tss'].max())  # Max tss in dataset
    tss_range = st.slider("Select time since surgery range", min_value=tss_min, max_value=tss_max, value=(tss_min, tss_max), step=1)
    cols['tss'] = tss_range

    # Call the function for basic filtering
    if st.button("Apply Filters"):
        basic_counts, filtered_data = filter_count(df=data, cols=cols, variables=variables)
        
        # Display basic filtering results
        st.write("Counts of Non-Blank Records for Variables (Basic Filtering):")
        for var, count in basic_counts.items():
            st.write(f"{var}: {count}")

        # Longitudinal filtering
        st.subheader("Longitudinal Filtering Results:")
        
        # Define timepoints based on tss_dashboard groups
        timepoints = {
            '3-4 months': ["3 to 4 months"],
            '5-7 months': ["5 to 7 months"],
            '8-12 months': ["8 to 12 months"]
            # Add more timepoint ranges as needed
        }

        # Call longitudinal filtering function
        longitudinal_results = longitudinal_filter(data=filtered_data, timepoints=timepoints, variables=variables)

        # Display longitudinal filtering results
        st.write("Counts of Non-Blank Records for Variables (Longitudinal Filtering):")
        for tp, counts in longitudinal_results.items():
            st.write(f"Timepoint: {tp}")
            for var, count in counts.items():
                st.write(f"{var}: {count}")

# Run the app
if __name__ == "__main__":
    main()
