
import streamlit as st
import pandas as pd
import requests
import json
import os

# --- Page Configuration ---
st.set_page_config(page_title="SuperKart Sales Prediction", layout="centered")
st.title("SuperKart Sales Prediction 📈")
st.markdown("Predict product sales for optimal inventory and strategic planning.")

# --- Backend API URL ---
# In Codespaces, this should be the service name if using Docker Compose, or the exposed port directly.
# For local testing, ensure your Flask backend is running on http://localhost:7860
backend_url = os.environ.get("BACKEND_URL", "http://backend:7860") # 'backend' is the service name in docker-compose
prediction_endpoint = f"{backend_url}/v1/predict"
batch_prediction_endpoint = f"{backend_url}/v1/predictbatch"

# --- Input Form ---
st.header("Single Product Sales Prediction")

with st.form("prediction_form"):
    st.write("Enter product and store details to predict sales:")

    # Product Details
    product_weight = st.number_input("Product Weight (kg)", min_value=0.1, max_value=50.0, value=12.66, step=0.01)
    product_mrp = st.number_input("Product MRP (₹)", min_value=1.0, max_value=500.0, value=117.08, step=0.01)
    product_allocated_area = st.number_input("Product Allocated Area Ratio", min_value=0.001, max_value=1.0, value=0.027, step=0.001, format="%.3f")

    product_sugar_content = st.selectbox(
        "Product Sugar Content",
        ('Low Sugar', 'Regular', 'No Sugar'),
        index=0
    )

    product_type = st.selectbox(
        "Product Type",
        ('Frozen Foods', 'Dairy', 'Canned', 'Baking Goods', 'Health and Hygiene',
         'Snack Foods', 'Meat', 'Household', 'Hard Drinks', 'Fruits and Vegetables',
         'Breads', 'Soft Drinks', 'Breakfast', 'Others', 'Starchy Foods', 'Seafood'),
        index=0
    )

    # Store Details
    store_size = st.selectbox(
        "Store Size",
        ('Small', 'Medium', 'High'),
        index=1
    )

    store_location_city_type = st.selectbox(
        "Store Location City Type",
        ('Tier 1', 'Tier 2', 'Tier 3'),
        index=1
    )

    store_type = st.selectbox(
        "Store Type",
        ('Supermarket Type1', 'Supermarket Type2', 'Departmental Store', 'Food Mart'),
        index=1
    )

    store_age_years = st.slider("Store Age (Years)", min_value=1, max_value=50, value=15)

    # Dummy/Placeholder features expected by the backend but not directly user-inputted
    # These were dropped during preprocessing but might be expected in initial payload structure
    product_id_char = "FD" # Example value
    product_type_category = "Non Perishables" # Example value

    submitted = st.form_submit_button("Predict Sales")
    if submitted:
        payload = {
            "Product_Weight": product_weight,
            "Product_Sugar_Content": product_sugar_content,
            "Product_Allocated_Area": product_allocated_area,
            "Product_Type": product_type, # Add Product_Type to payload
            "Product_MRP": product_mrp,
            "Store_Size": store_size,
            "Store_Location_City_Type": store_location_city_type,
            "Store_Type": store_type,
            "Product_Id_char": product_id_char, # Include for consistency with backend expectation
            "Store_Age_Years": store_age_years,
            "Product_Type_Category": product_type_category # Include for consistency with backend expectation
        }

        try:
            response = requests.post(prediction_endpoint, json=payload)
            if response.status_code == 200:
                prediction = response.json().get("Product_Store_Sales_Total_Predicted")
                st.success(f"Predicted Product Store Sales Total: ₹{prediction:,.2f}")
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the backend API. Please ensure the backend is running and accessible.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")


# --- Batch Prediction ---
st.header("Batch Sales Prediction (CSV Upload)")

uploaded_file = st.file_uploader("Upload a CSV file for batch prediction", type=["csv"])

if uploaded_file is not None:
    # Display uploaded data for user to verify
    st.subheader("Uploaded Data Preview")
    # Create a copy to prevent Streamlit from automatically re-reading if the user interacts with the widget again
    batch_df_preview = pd.read_csv(uploaded_file)
    st.write(batch_df_preview.head())

    if st.button("Run Batch Prediction"):
        try:
            # Reset file pointer to the beginning after reading for preview
            uploaded_file.seek(0)
            # Correctly pass the file with its name and content type
            files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            batch_response = requests.post(batch_prediction_endpoint, files=files)

            if batch_response.status_code == 200:
                predictions = batch_response.json()
                st.subheader("Batch Predictions")
                predictions_df = pd.DataFrame(predictions, columns=["Predicted Sales"]) # Ensure predictions is a list of numbers
                st.dataframe(predictions_df)

                csv = predictions_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Predictions CSV",
                    data=csv,
                    file_name="batch_predictions.csv",
                    mime="text/csv",
                )
            else:
                st.error(f"Batch Prediction Error: {batch_response.status_code} - {batch_response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the backend API. Please ensure the backend is running and accessible.")
        except Exception as e:
            st.error(f"An unexpected error occurred during batch prediction: {e}")
