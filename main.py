import tweepy
import os
import httpx
import requests

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
def post_cat_or_dog_picture(isDog):
    HEADER = {
        'x-api-key':'live_82nyRlMQqVDBMc4VJzyiPlXjviQJPaL9sqtLwE3R6DAHUUBsg3VgDpb6YT7nw4ce'
    }
    url = ""

    if isDog:
        url = "https://api.thedogapi.com/v1/images/search"
    else:
        url = "https://api.thecatapi.com/v1/images/search"
    with httpx.Client(http2=False, headers=HEADERS) as client:
        response = client.get(
            url,
        )
        assert response.status_code == 200
        data = response.json()
    return data['url']

# Function to create a poll for the next day's picture
def create_poll():
    poll_question = 'What should be the next day\'s picture?'
    poll_options = ['Cat', 'Dog']
    poll = api.create_poll(question=poll_question, options=poll_options, end_datetime=None)
    return poll.id

# Main loop for running the bot
def main():
        # authorization of consumer key and consumer secret
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    
    # set access to user's access key and access secret 
    auth.set_access_token(access_token, access_token_secret)

    path = 'images.jpg'
    get_picture("https://cdn2.thecatapi.com/images/aap.jpg", path)
    
    # calling the api 
    api = tweepy.API(auth)
                # Download the image from the URL
    image_response = requests.get("https://cdn2.thecatapi.com/images/aap.jpg", stream=True)
    image_path = 'temp_image.jpg'  # Provide a filename to save the image temporarily
    with open(image_path, 'wb') as image_file:
        for chunk in image_response.iter_content(chunk_size=8192):
                image_file.write(chunk)

        # Upload the image to Twitter
    media = api.media_upload(image_path)
    client = tweepy.Client(consumer_key=consumer_key,
                        consumer_secret=consumer_secret,
                        access_token=access_token,
                        access_token_secret=access_token_secret)

    # Replace the text with whatever you want to Tweet about
    response = client.create_tweet(media_ids=[media.media_id])

    #response = client.get_tweet(1683743570098896896)

    print(response)

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