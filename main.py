from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import os
import math
from flask_cors import CORS
app = Flask(__name__, static_folder='static')
app.debug=False
CORS(app)

# Function to generate data for the chart
def generate_chart_data(file_path, start_year, start_day, end_year, end_day):
    try:
        # Load the data from the selected Excel file
        df = pd.read_excel(file_path)

        # Filter the data based on user-provided parameters
        filtered_df = df[(df["YYYY"] >= start_year) & (df["YYYY"] <= end_year) &
                         (df["DAY"] >= start_day) & (df["DAY"] <= end_day)]

        if not filtered_df.empty:
            # Calculate values for the chart based on the filtered data
            years = filtered_df["YYYY"]
            values = filtered_df["a"] * filtered_df["b"] * np.log(filtered_df["f"] / (2 * math.pi)) + 7
            return years.tolist(), values.tolist()
        else:
            return None, None
    except Exception as e:
        return None, str(e)

# @app.route('/')
# def index():
#     return render_template('index.html')

@app.route('/api/chart_data')
def chart_data():
    try:
        # Get filter parameters from the query string
        start_year = request.args.get('start_year')
        end_year = request.args.get('end_year')
        start_day = request.args.get('start_day')
        end_day = request.args.get('end_day')
        data_source = request.args.get('source')  # Get the selected data source

        # Check if any of the query parameters are missing or not numeric
        if any(param is None or not param.isdigit() for param in [start_year, end_year, start_day, end_day]) or data_source is None:
            return jsonify({'error': 'One or more query parameters are missing or invalid'}), 400

        # Convert parameters to integers
        start_year = int(start_year)
        end_year = int(end_year)
        start_day = int(start_day)
        end_day = int(end_day)

        # Define the Excel file path based on the selected data source
        file_path = f'static/{data_source}.xlsx'

        # Generate chart data
        years, values = generate_chart_data(file_path, start_year, start_day, end_year, end_day)

        if years is not None and values is not None:
            return jsonify({'years': years, 'values': values})
        else:
            return jsonify({'error': 'No data found for the specified range'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
