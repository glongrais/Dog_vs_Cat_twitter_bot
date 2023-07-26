import tweepy
import os
import httpx
import requests

consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")

# Get the result of the poll and return 1 if the dog wins or 0 if the cat wins.
def get_poll_result(tweet_id):

    HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    }

    tweet_url = "https://cdn.syndication.twimg.com/tweet-result?id="+ tweet_id +"&lang=en"
    # retrieve embed HTML
    with httpx.Client(http2=False, headers=HEADERS) as client:
        response = client.get(tweet_url)
        assert response.status_code == 200
        data = response.json()

        dog_count = int(data['card']['binding_values']['choice1_count']['string_value'])
        cat_count = int(data['card']['binding_values']['choice2_count']['string_value'])
        
        return dog_count > cat_count

# Function to get a picture of a cat or dog and return the image's url
def get_cat_or_dog_picture(isDog):
    HEADERS = {
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
    return data[0]['url']

# Download locally the picture from the url, then upload it on Twitter. Return the media_id
def upload_picture(url):

    # Using the Twitter API 1.1 to upload the image as it is not supported yet by the API 2 

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    # Download the image from the URL
    image_response = requests.get(url, stream=True)
    image_path = 'temp_image.jpg'  # Provide a filename to save the image temporarily
    with open(image_path, 'wb') as image_file:
        for chunk in image_response.iter_content(chunk_size=8192):
                image_file.write(chunk)

    # Upload the image to Twitter
    media = api.media_upload(image_path)
    return media.media_id

# Main loop for running the bot
def main():

    tweet_id = '1684173990145785856'

    client = tweepy.Client(consumer_key=consumer_key,
                        consumer_secret=consumer_secret,
                        access_token=access_token,
                        access_token_secret=access_token_secret)
    
    isDog = get_poll_result(tweet_id)

    image_url = get_cat_or_dog_picture(isDog)

    media_id = upload_picture(image_url)
    
    response = client.create_tweet(media_ids=[media_id])

    image_tweet_id = response.data['id']

    response = client.create_tweet(poll_options=['Dog', 'Cat'], poll_duration_minutes=300, text='Who is the best?', in_reply_to_tweet_id=image_tweet_id)

    poll_tweet_id = response.data['id']

    print(response)

# Run the bot
if __name__ == "__main__":

    main()
