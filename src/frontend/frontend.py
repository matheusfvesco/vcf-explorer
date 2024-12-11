import streamlit as st
import requests
import os
import time

API_BASE_URL = os.getenv("API_BASE_URL")

# Function to check API availability
def check_api_status():
    while True:
        try:
            response = requests.get(f"{API_BASE_URL}/")
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException:
            time.sleep(2)  # Wait for 2 seconds before retrying


# Function to fetch data from API
def fetch_data(endpoint, params=None):
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
        return None


# Map original column names to user-friendly names
COLUMN_MAPPING = {
    "freq": "Global Frequency",
    "male_freq": "Male Frequency",
    "female_freq": "Female Frequency",
    "dp": "Depth",
}

OP_MAPPING = {"gt": "Greater than", "eq": "Equal to", "lt": "Less than"}


# Main Streamlit app
def main():
    st.set_page_config(
        layout="wide",
        page_icon=":dna:",
    )

    st.title("Variants Explorer")

    with st.spinner("Waiting for files to be processed..."):
        check_api_status()

    # Sidebar setup
    st.sidebar.title("Filter Options")

    # Fetch metadata
    meta = fetch_data("/meta")
    if not meta:
        return

    # Sidebar filters
    parameter = st.sidebar.radio(
        "Select column to filter by:",
        ["freq", "male_freq", "female_freq", "dp"],
        index=0,
        format_func=lambda x: COLUMN_MAPPING.get(
            x, x
        ),
    )
    operator = st.sidebar.radio(
        "Select operation:",
        ["gt", "lt", "eq"],
        index=0,
        format_func=lambda x: OP_MAPPING.get(x, x),
    )

    # Extract min and max values from metadata
    min_value = float(meta[parameter][0])
    max_value = float(meta[parameter][1])

    # Add a text input for manual entry
    manual_value = st.sidebar.text_input(
        "Manually enter value:", value=f"{min_value:.10f}"
    )
    try:
        manual_value_float = float(manual_value)
        # Ensure manual value is within the expected range
        if min_value <= manual_value_float <= max_value:
            value = manual_value_float
        else:
            st.sidebar.error(f"Value must be between {min_value} and {max_value}.")
            value = min_value
    except ValueError:
        value = min_value

    page = st.sidebar.number_input("Page number:", min_value=1, value=1, step=1)
    page_size = st.sidebar.number_input("Page size:", min_value=1, value=10, step=1)

    # Apply Filter button
    if st.sidebar.button("Apply Filter"):
        st.session_state["filtered"] = fetch_data(
            f"/filter/{parameter}/{operator}/{value}",
        )

    # Metadata display
    st.sidebar.markdown("---")
    st.sidebar.header("Metadata (min, max)")
    st.sidebar.json(meta, expanded=False)

    if "filtered" not in st.session_state:
        all_data = fetch_data("/variants")
        if all_data:
            st.session_state["filtered"] = all_data

    filtered_data = st.session_state.get("filtered", [])

    st.header("Variants")
    if filtered_data:
        total_records = len(filtered_data)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_data = filtered_data[start_idx:end_idx]

        if paginated_data:
            st.dataframe(
                paginated_data,
                use_container_width=True,
                width=2000,
                height=400,
                column_config={
                    "freq": st.column_config.NumberColumn(
                        format="%.10f", disabled=True
                    ),
                    "male_freq": st.column_config.NumberColumn(
                        format="%.10f", disabled=True
                    ),
                    "female_freq": st.column_config.NumberColumn(
                        format="%.10f", disabled=True
                    ),
                },
            )  # Makes the dataframe take up more space
            st.write(f"Showing records {start_idx + 1} to {end_idx} of {total_records}")
        else:
            st.write("No data available for the selected page.")
    else:
        st.write("No data to display. Please apply a filter.")


if __name__ == "__main__":
    main()
