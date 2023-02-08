import os
import random
import sys
import time
import yaml
from flask import Flask, request
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import threading
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
# Configure the logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('bot.log', maxBytes=10000, backupCount=5)
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler(sys.stdout))


# Load the preconfigured messages from the messages.yaml file
with open("messages.yaml") as f:
    messages = yaml.safe_load(f)
news_posts = []
# Initialize the Slack client
client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
# Route for handling the /news command
@app.route("/news", methods=["POST"])
def news():
    # Get the channel and user information from the request
    channel = request.form["channel_id"]
    user = request.form["user_id"]

    # Send a message to the channel
    try:
        for i in range(len(news_posts)):
            client.chat_postMessage(
                channel=channel,
                text=get_formatted_news(news_posts[i])
            )
    except SlackApiError as e:
        logger.error("Error : {}".format(e))

    return "News posted!"

# Route for handling the /post command
@app.route("/post", methods=["POST"])
def post():
    # Get the text, date, and link from the request
    text = request.form["text"]
    link = request.form["link"]
    user = request.form["user_id"]

    # Add the news to the array
    news_item = {
        "text": text,
        "link": link
    }
    if news_posts.count(news_item) < 10:
        news_posts.append(news_item)
        logger.info("News added by user {}".format(user))
    return "News added!"

# Route for handling the /sensibilisation command
@app.route("/sensibilisation", methods=["POST"])
def sensibilisation():
    # Get the channel and user information from the request
    channel = request.form["channel_id"]
    user = request.form["user_id"]
    logger.info("Sensibilisation requested by user {}".format(user))
    # Send a message to the channel
    try:
        client.chat_postMessage(
            channel=channel,
            text=get_formatted_message(random.choice(messages))
        )
    except SlackApiError as e:
        logger.error("Error : {}".format(e))
    return "Sensibilisation posted!"

# Function for sending messages every day between 9:00 and 10:00
def send_messages():
    while True:
        current_time = time.localtime()
        if(current_time.tm_hour ==0 and current_time.tm_min == 0) :
            news_posts.clear() 
            logger.info("News cleared")
        if  current_time.tm_hour == 9 and current_time.tm_wday not in [5, 6]:
            # Wait for a random number of seconds between 0 and 3600 (1 hour)
            wait_time = random.randint(0, 3600)
            time.sleep(wait_time)
        
            # Send a message to the channel
            logger.info("Sending message...")
            try:
                client.chat_postMessage(
                    channel=os.environ["SLACK_ANNOUNCMENT_CHANNEL"],
                    text=get_formatted_message(random.choice(messages))
                )
            except SlackApiError as e:
                logger.error("Error : {}".format(e))

        # Sleep for 1 minutes
        time.sleep(60)
def get_formatted_message(message):
    return f"*{message['Subject']}*\n{message['Message']}"
def get_formatted_news(news):
    return f"{news['text']}\n{news['link']}"
# Run the Flask app in a local development server
if __name__ == "__main__":
    # Start the message sending loop in a separate thread
    t = threading.Thread(target=send_messages)
    t.start()

    app.run(port=3000)
