import tweepy
import os
import httpx

consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
}

# Function to post a picture of a cat or dog
def post_cat_or_dog_picture():
    # Replace 'cat.jpg' and 'dog.jpg' with your actual image files
    api.update_status('Here\'s a picture of a cat 🐱')

# Function to create a poll for the next day's picture
def create_poll():
    poll_question = 'What should be the next day\'s picture?'
    poll_options = ['Cat', 'Dog']
    poll = api.create_poll(question=poll_question, options=poll_options, end_datetime=None)
    return poll.id

# Main loop for running the bot
def main():
    client = tweepy.Client(consumer_key=consumer_key,
                        consumer_secret=consumer_secret,
                        access_token=access_token,
                        access_token_secret=access_token_secret)

    # Replace the text with whatever you want to Tweet about
    response = client.create_tweet(poll_options = ['Cat', 'Dog'], poll_duration_minutes=60, text='hello world 2')

    #response = client.get_tweet(1683743570098896896)

    print(response)

    HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
}


# retrieve embed HTML
with httpx.Client(http2=False, headers=HEADERS) as client:
    response = client.get(
        "https://cdn.syndication.twimg.com/tweet-result?id=1683800803968942080&lang=en",
    )
    assert response.status_code == 200
    data = response.json()
    print(data['card']['binding_values']['choice2_count'])

# Run the bot
if __name__ == "__main__":
    main()