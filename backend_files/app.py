
import os
import joblib
import pandas as pd
from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# --- Load the Model and Preprocessing Components ---
# The model file is copied directly into the /app directory (WORKDIR) inside the Docker container.
# Therefore, the path should be relative to the WORKDIR.
model_path = 'backend_files/superkart_model.joblib'
model = joblib.load(model_path)

# Define the order of columns expected by the model (excluding 'Store_Id')
# This order should match the columns in X_train after preprocessing
# We get this from the kernel state X_train.columns (26 columns)
# The original dataset had 'Product_Weight', 'Product_Sugar_Content', 'Product_Allocated_Area',
# 'Product_Type', 'Product_MRP', 'Store_Id', 'Store_Size', 'Store_Location_City_Type',
# 'Store_Type', 'Product_Store_Sales_Total', 'Store_Age_Years'
# After preprocessing: Product_Id and Store_Establishment_Year dropped.
# Product_Sugar_Content: reg -> Regular (done in app.py logic)
# Store_Age_Years: derived
# Store_Location_City_Type & Store_Size: Label Encoded
# Product_Type & Store_Type: One-hot encoded (drop_first=True)

# Based on the X_train structure, let's explicitly define the final feature set order
# Product_Id and Product_Type_Category in the payload are not used by the model

model_features = [
    'Product_Weight', 'Product_Allocated_Area', 'Product_MRP', 'Store_Size',
    'Store_Location_City_Type', 'Store_Age_Years',
    'Product_Type_Breads', 'Product_Type_Breakfast', 'Product_Type_Canned',
    'Product_Type_Dairy', 'Product_Type_Frozen Foods', 'Product_Type_Fruits and Vegetables',
    'Product_Type_Hard Drinks', 'Product_Type_Health and Hygiene', 'Product_Type_Household',
    'Product_Type_Meat', 'Product_Type_Others', 'Product_Type_Seafood',
    'Product_Type_Snack Foods', 'Product_Type_Soft Drinks', 'Product_Type_Starchy Foods',
    'Product_Sugar_Content_No Sugar', 'Product_Sugar_Content_Regular',
    'Store_Type_Food Mart', 'Store_Type_Supermarket Type1', 'Store_Type_Supermarket Type2'
]

# --- Preprocessing Function ---
def preprocess_input(data: pd.DataFrame) -> pd.DataFrame:
    # 1. Data Cleaning: Normalizing 'Product_Sugar_Content'
    data['Product_Sugar_Content'] = data['Product_Sugar_Content'].replace({
        'reg': 'Regular'
    })

    # 2. Feature Engineering: Create 'Store_Age_Years' if not already present
    # Note: For new inference data, 'Store_Establishment_Year' might not be provided
    # The payload implies 'Store_Age_Years' is directly provided, or we should assume current year - Est_Year
    # For this app, we expect Store_Age_Years to be present in the input payload directly.
    if 'Store_Establishment_Year' in data.columns:
        data['Store_Age_Years'] = 2024 - data['Store_Establishment_Year']
        data = data.drop(columns=['Store_Establishment_Year'])

    # 3. Drop 'Product_Id_char' and 'Product_Type_Category' if they exist in the input
    # These were mentioned in the example payload but not used in the training data X
    data = data.drop(columns=['Product_Id_char', 'Product_Type_Category'], errors='ignore')

    # 4. Label Encoding for ordinal categorical columns
    # Map 'Store_Location_City_Type' (Tier 1, 2, 3) to numerical values
    city_type_mapping = {'Tier 3': 0, 'Tier 2': 1, 'Tier 1': 2}
    data['Store_Location_City_Type'] = data['Store_Location_City_Type'].map(city_type_mapping)

    # Map 'Store_Size' (Small, Medium, High) to numerical values
    store_size_mapping = {'Small': 0, 'Medium': 1, 'High': 2}
    data['Store_Size'] = data['Store_Size'].map(store_size_mapping)

    # 5. One-Hot Encoding for nominal categorical columns
    nominal_cols_to_encode = ['Product_Type', 'Product_Sugar_Content', 'Store_Type']

    # Ensure 'Product_Type' exists in the input data frame before encoding
    # This is to handle cases where a single input might not have all types
    if 'Product_Type' not in data.columns:
        data['Product_Type'] = 'Unknown'

    data = pd.get_dummies(data, columns=nominal_cols_to_encode, drop_first=True)

    # Align columns to match the training data. This is crucial for consistent prediction.
    # Add missing columns with 0, and remove extra columns
    final_data = pd.DataFrame(columns=model_features)
    for col in model_features:
        if col in data.columns:
            final_data[col] = data[col]
        else:
            final_data[col] = 0 # Assume 0 for missing one-hot encoded features

    return final_data

# --- API Endpoints ---

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

# Single prediction endpoint
@app.route('/v1/predict', methods=['POST'])
def predict():
    try:
        json_payload = request.get_json(force=True)
        input_df = pd.DataFrame([json_payload])

        # Preprocess the input data
        processed_data = preprocess_input(input_df)

        # Make prediction
        prediction = model.predict(processed_data)[0]

        return jsonify({'Product_Store_Sales_Total_Predicted': prediction})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Batch prediction endpoint
@app.route('/v1/predictbatch', methods=['POST'])
def predict_batch():
    try:
        # Assuming the batch data is sent as a CSV file in the request files
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file and file.filename.endswith('.csv'):
            input_df = pd.read_csv(file)

            # Preprocess the input data
            processed_data = preprocess_input(input_df)

            # Make predictions
            predictions = model.predict(processed_data)

            return jsonify(predictions.tolist())
        else:
            return jsonify({'error': 'Invalid file format. Please upload a CSV.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    # For local testing, use app.run(debug=True)
    # For deployment, listen on all public IPs and specified port (e.g., 7860 for Codespaces)
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 7860))
