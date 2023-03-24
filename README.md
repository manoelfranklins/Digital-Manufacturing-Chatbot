# Digital-Manufacturing-Chatbot

This is a Chatbot for SAP Digital Manufacturing that retrieves releasable orders for a given production plant and allow you to release orders.
It uses APIs to interact with SAP DM.

## Features

- View available orders for a specific plant
- Release specific orders in full

## Getting Started

These instructions will help you set up the project on your local machine for development and testing purposes.

### Prerequisites

This Chatbot uses the following libraries:

- random
- requests
- re
- spacy
- nltk
- json
- datetime
- SentimentIntensityAnalyzer (from nltk.sentiment)

To install the necessary libraries, you can use the following pip commands:

pip install requests
pip install spacy
pip install nltk

After installing the spacy library, you will also need to download the English language model by running:

python -m spacy download en_core_web_sm

Note that the libraries `random`, `re`, `json`, and `datetime` are part of Python's standard library and do not require separate installation.

### Installation

1. Clone the repository: 
git clone https://github.com/manoelfranklins/Digital-Manufacturing-Chatbot.git

2. Navigate to the project directory:
cd Digital-Manufacturing-Chatbot

3. Install the required dependencies:
pip install -r requirements.txt
Then run:
python -m spacy download en_core_web_sm

4. Run the chatbot:
python chatbot.py

## Usage

To interact with the chatbot, simply type your message in the terminal and press Enter. The chatbot will respond to your query or command.

Sample commands are:
- What are the available orders for XXXX plant?
- Release order 9999999999

## Samples

![Sample Image 1](https://github.com/manoelfranklins/Digital-Manufacturing-Chatbot/blob/master/Sample1.png?raw=true)
![Sample Image 2](https://github.com/manoelfranklins/Digital-Manufacturing-Chatbot/blob/master/Sample2.png?raw=true)

