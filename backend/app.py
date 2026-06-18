from flask import Flask, jsonify, request
import requests
from flask_cors import CORS  
import pandas as pd
import os

# Import your custom RAG retrieval function
from rag_engine import query_rag_system

app = Flask(__name__)
# Enable CORS so your frontend can fetch data from this backend
CORS(app)

# Helper function to load and clean data
def load_data():
    """
    Dynamically loads the dataset from the repository's data folder relative 
    to this file's position, ensuring it works for any user on any machine.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Assuming your project folder structure puts the dataset inside an adjacent 'data' folder
    csv_path = os.path.join(base_dir, '../data/Employee_Insurance_and_Benefits_Dataset.csv')
    
    # Fallback backup check in case the user named it simply 'insurance_data.csv'
    if not os.path.exists(csv_path):
        csv_path = os.path.join(base_dir, '../data/insurance_data.csv')
        
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Critical dataset not found in the repository data folder.")
        
    df = pd.read_csv(csv_path)
    
    # Clean up accidental double spaces or trailing spaces in the CSV column headers
    df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True)
    return df
    #return pd.read_csv(r"C:\Users\sanje\MISC_\Downloads\MAHE\Study_Material\Xceedance\data\Employee_Insurance_and_Benefits_Dataset.csv")
    

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    try:
        df = load_data()

        # 1. Bar Chart Data: Average Claim Amount by Department
        dept_claims = df.groupby('Department')['Total Claim Amount ($)'].mean().round(2)
        bar_chart_data = {
            "labels": dept_claims.index.tolist(),
            "values": dept_claims.values.tolist()
        }

        #2. Pie Chart Data: Insurance Plan Tier Counts
        tier_counts = df['Insurance Plan Tier'].value_counts()
        pie_chart_data={
            "labels": tier_counts.index.tolist(),
            "values": tier_counts.values.tolist()
        }

        # 3. Histogram Data: Binned Wellness Stipend Distribution
        # We group stipends into $100 ranges (bins) to count how many employees fall into each range
        stipend_series = df['Wellness Stipend Used ($)']
        bins = [0, 100, 200, 300, 400, 500, 600]
        # labels define the ranges visually: "0-100", "101-200", etc.
        labels = [f"${bins[i]}-${bins[i+1]}" for i in range(len(bins)-1)]
        binned_stipends = pd.cut(stipend_series, bins=bins, labels=labels, include_lowest=True).value_counts().sort_index()
        
        histogram_data = {
            "labels": binned_stipends.index.tolist(),
            "values": binned_stipends.values.tolist()
        }

        # 4. Scatter Plot Data: {x: Premium, y: Claim}
        # Chart.js scatter plots expect data structured as a list of dictionaries: [{'x': 1, 'y': 2}]
        scatter_data = []
        for _, row in df.iterrows():
            scatter_data.append({
                'x': float(row['Annual Premium ($)']),
                'y': float(row['Total Claim Amount ($)']),
                'label': str(row['Employee Name']) # Passing name so we can show it on hover tooltip
            })

        #Insights

        insights = []
        
        # Insight 1: Highest spending department
        highest_dept = dept_claims.idxmax()
        highest_val = dept_claims.max()
        insights.append(f"<strong>Financial Exposure:</strong>&nbsp; The&nbsp;<strong>{highest_dept}</strong>&nbsp; department represents the highest organizational risk, averaging&nbsp; <strong>${highest_val:,.2f}</strong>&nbsp;in insurance claims YTD.")
        
        # Insight 2: Scatter plot outliers (High Claims vs Premiums)
        outliers_count = len(df[df['Total Claim Amount ($)'] > df['Annual Premium ($)']])
        insights.append(f"<strong>Risk Analysis:</strong>&nbsp;Outlier detection identifies&nbsp; <strong>{outliers_count} employees</strong>&nbsp;whose total claim amounts have exceeded their annual premiums, driving up corporate liability."
)
        
        # Insight 3: Wellness engagement gap from Histogram
        # Count how many employees used less than $100 of their stipend
        low_engagement = len(df[df['Wellness Stipend Used ($)'] <= 100])
        engagement_pct = (low_engagement / len(df)) * 100
        insights.append(f"<strong>Benefits Optimization:</strong>&nbsp; Roughly&nbsp; <strong>{engagement_pct:.1f}%</strong>&nbsp; of the workforce utilized $100 or less of their wellness stipend. HR should initiate an internal awareness campaign to drive engagement.")

        # Combine all processed data into one clean JSON response
        payload = {
            "status": "success",
            "barChart": bar_chart_data,
            "pieChart": pie_chart_data,
            "histogram": histogram_data,
            "scatterPlot": scatter_data,
            "insights": insights
        }

        return jsonify(payload), 200
    
    except Exception as e: 
        # If any error occurs during data processing, return an error message
        return jsonify({"status": "error", "message": str(e)}), 500
    
#Chatbot endpoint to relay messages to Ollama
# @app.route('/api/chat', methods=['POST'])
# def chat_with_ollama():
#     """
#     Relays frontend messages to a local Ollama instance. 
#     Includes a connection fallback to keep the app shareable for others.
#     """
#     try:
#         user_data = request.json
#         user_prompt = user_data.get("message", "")
        
#         # Local Ollama default port network link
#         ollama_url = "http://localhost:11434/api/generate"
        
#         payload = {
#             "model": "llama3.2",  # Popular, ultra-lightweight open model
#             "prompt": f"You are a helpful insurance data assistant for an Xceedance dashboard. Keep your answer brief and under 3 sentences. User question: {user_prompt}",
#             "stream": False
#         }
        
#         # 2-second timeout prevents the server from hanging if Ollama isn't running
#         response = requests.post(ollama_url, json=payload, timeout=2)
#         response_data = response.json()
        
#         bot_response = response_data.get("response", "I'm having trouble processing that right now.")
#         return jsonify({"status": "success", "reply": bot_response}), 200

#     except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
#         # THE GENTLE FALLBACK: This keeps your repository public-friendly!
#         instructions = (
#             "**Local AI Assistant is currently offline.**\n\n"
#             "To use this chatbot, other users simply need to:\n"
#             "1. Download Ollama from https://ollama.com\n"
#             "2. Open a terminal and run: `ollama run llama3.2`\n\n"
#             "Once running, refresh this page to chat for free with no API keys!"
#         )
#         return jsonify({"status": "offline", "reply": instructions}), 200
        
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500
    


#Chat with RAG system endpoint
@app.route('/api/chat', methods=['POST'])
def chat_with_rag():
    """
    Accepts user inquiries, feeds them through the local vector store, 
    and returns a contextual response generated by Groq Cloud.
    """
    try:
        user_data = request.json
        user_prompt = user_data.get("message", "")
        
        if not user_prompt:
            return jsonify({"status": "error", "message": "Empty message string received."}), 400
            
        # Route the question directly through your RAG script logic
        bot_response = query_rag_system(user_prompt)
        
        # Return the response back cleanly to your frontend app.js handler
        return jsonify({"status": "success", "reply": bot_response}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True, port=5000)  # Run the Flask app on localhost:5000   