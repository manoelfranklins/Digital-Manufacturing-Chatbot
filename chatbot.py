import random
import requests
import re
import spacy
import nltk
import json
from datetime import datetime
from nltk.sentiment import SentimentIntensityAnalyzer

# Global vars
last_order_summary = None

# Your API and OAuth credentials
api_base_url = 'https://API_URL/order/v1/orders/list'
client_id = 'CLIENT_ID'
client_secret = 'CLIENT_SECRET'
token_url = 'https://SUBACCOUNT.authentication.eu10.hana.ondemand.com/oauth/token'

# Function to obtain an access token using client credentials
def get_access_token():
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post(token_url, data=payload)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception('Failed to obtain an access token.')

# Load the SpaCy model
nlp = spacy.load("en_core_web_sm")

# Download the NLTK VADER lexicon and initialize SentimentIntensityAnalyzer
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

# Process Message Functions
def process_message(message, access_token):
    entities = extract_entities(message)
    intent = classify_intent(message)
    sentiment = analyze_sentiment(message)
    
    # Check if the user's intent is to get available orders
    if intent == "get_available_orders":
        plant = entities.get("PLANT")
        if plant:
            response = get_available_orders(access_token, plant)
            ## print(f"Last order summary: {last_order_summary}")  # Add this line to check the value of last_order_summary
        else:
            response = "Please provide a plant code."
    elif intent == "release_order":
        order_id = entities.get("ORDER")
        if order_id:
            response = release_order(access_token, order_id)
        else:
            response = "Please provide an order ID."
    else:
        response = "I'm sorry, I didn't understand your request. Can you please rephrase it?"

    return response

def extract_entities(text):
    doc = nlp(text)
    entities = {ent.label_: ent.text for ent in doc.ents}
    
    # Check if the user's input contains a plant-related keyword
    plant_keywords = ["plant", "factory", "location", "site"]
    if any(keyword in text.lower() for keyword in plant_keywords):
        # Extract plant code using a more flexible regular expression pattern
        plant_code_pattern = r'\b[A-Za-z]{0,1}\d{3,4}\b'
        plant_code_match = re.search(plant_code_pattern, text)
        if plant_code_match:
            entities['PLANT'] = plant_code_match.group()
    
    # Extract order ID using a regular expression pattern
    order_id_pattern = r'\b\d{7}\b'
    order_id_match = re.search(order_id_pattern, text)
    if order_id_match:
        entities['ORDER'] = order_id_match.group()

    return entities

def classify_intent(text):
    # Check for keywords related to getting available orders
    order_keywords = [
        "available orders",
        "production orders",
        "orders for plant",
        "existing process orders",
        "list orders",
        "show me orders",
        "current orders",
        "pending orders",
        "active orders",
        "open orders",
        "tell me orders",
        "display orders",
        "report orders",
        "get orders",
    ]
    release_order_keywords = [
        "release order",
        "release production order",
        "activate order",
        "start order",
    ]

    if any(keyword in text.lower() for keyword in order_keywords):
        return "get_available_orders"
    elif any(keyword in text.lower() for keyword in release_order_keywords):
        return "release_order"
    return None

def analyze_sentiment(text):
    sentiment_scores = sia.polarity_scores(text)
    return sentiment_scores

# Function to call the API for available orders
def get_available_orders(access_token, plant):
    
    global last_order_summary

    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'plant': plant
    }
    response = requests.get(api_base_url, headers=headers, params=params)

    if response.status_code == 200:
        orders = response.json()['content']
        ##print(f"Orders from API: {orders}")

	 # Print the JSON response in a readable format
        ##print("JSON Response:")
        ##print(json.dumps(orders, indent=2))

        # Filter out orders with "DONE", "DISCARDED", or "CLOSED" status
        filtered_orders = [order for order in orders if order['releaseStatus'] not in ('RELEASED', 'DONE', 'DISCARDED', 'CLOSED')]

        # Sort orders by plannedStartDate
        sorted_orders = sorted(filtered_orders, key=lambda x: x['plannedStartDate'])

        order_summary = ''
        for order in sorted_orders:
            # Format dates as dd/MM/YYYY HH:mm:ss
            planned_start_date = datetime.fromisoformat(order['plannedStartDate'].replace('Z', '+00:00')).strftime('%d/%m/%Y %H:%M:%S')
            planned_completion_date = datetime.fromisoformat(order['plannedCompletionDate'].replace('Z', '+00:00')).strftime('%d/%m/%Y %H:%M:%S')

            # Create a summary string for each order with the specified fields
            order_summary += f"Order: {order['order']}, Plant: {order['plant']}, Status: {order['status']}, Material: {order['material']['material']}, " \
                             f"Build Quantity: {order['buildQuantity']} {order['erpUnitOfMeasure']}, " \
                             f"Planned Start Date: {planned_start_date}, " \
                             f"Planned Completion Date: {planned_completion_date}\n"
            
        last_order_summary = order_summary  # Update the last_order_summary variable
        return order_summary

    else:
        raise Exception('Failed to fetch available orders.')

responses = {
    'greetings': ['Hello!', 'Hi there!', 'Hey!', 'Hi!', 'Welcome!'],
    'goodbyes': ['Goodbye!', 'See you later!', 'Bye!', 'Farewell!'],
    'how_are_you': ['I\'m doing great, thanks!', 'I\'m doing well, how about you?', 'I\'m good, and you?'],
    'unknown': ['I\'m not sure how to respond to that.', 'I don\'t quite understand.', 'Can you rephrase that?']
}

def release_order(access_token, order_id):
    global last_order_summary
    api_release_url = 'https://api.eu10.dmc.cloud.sap/order/v1/orders/release'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Find the order with the specified ID in last_order_summary
    target_order = None
    if last_order_summary:
        order_lines = last_order_summary.strip().split('\n')
        for line in order_lines:
            if f"Order: {order_id}" in line:
                target_order = line
                break

    if not target_order:
        return f"Order {order_id} not found."

    print(f"Target order: {target_order}")  # Add this line to print the target_order string
    # Extract the plant and quantity values from the target_order
    plant_pattern = r'Plant: (\w+)'

    # Extract the plant and quantity values from the target_order
    plant_pattern = r'Plant: (\w+)'
    quantity_pattern = r'Build Quantity: (\d+\.?\d*)'

    # Check if the plant pattern is found in the target_order
    plant_match = re.search(plant_pattern, target_order)
    if plant_match:
        plant = plant_match.group(1)
    else:
        return f"Unable to find plant for order {order_id}."

    # Extract the build quantity value
    quantity_to_release = float(re.search(quantity_pattern, target_order).group(1))

    data = {
        'order': order_id,
        'plant': plant,
        'quantityToRelease': quantity_to_release
    }
    response = requests.post(api_release_url, headers=headers, json=data)

    if response.status_code == 200:
        return f"Order {order_id} has been released successfully."
    else:
        raise Exception(f"Failed to release order {order_id}.")


def respond_to_message(message):
    message = message.lower()
    
    if 'hello' in message or 'hi' in message:
        return random.choice(responses['greetings'])
    elif 'bye' in message or 'goodbye' in message:
        return random.choice(responses['goodbyes'])
    elif 'how are you' in message:
        return random.choice(responses['how_are_you'])
    else:
        return random.choice(responses['unknown'])

def main():
    access_token = get_access_token()

    while True:
        message = input("Supervisor: ")
        if message.lower() == "quit":
            break
        response = process_message(message, access_token)
        print(f"Chatbot: {response}")

if __name__ == '__main__':
    main()