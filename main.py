import datetime
import tweepy
import os
import httpx
import requests
import pymysql
from enum import Enum
import logging

class Poll_result(Enum):
    Dog = 1
    Cat = 2
    Tie = 3

def logging_setup():
    # Create a "logs" directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Get today's date
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Configure the logging
    log_file_path = os.path.join("logs", f"bot_{today_date}.log")
    logging.basicConfig(filename=log_file_path, level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def get_credentials():
    credential_names = [
        "CONSUMER_KEY", "CONSUMER_SECRET", "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET",
        "DOG_API_KEY", "DB_HOST", "DB_PORT", "DB_USER", "DB_USER_PASS",
        "DB_NAME", "CERT_PATH"
    ]

    credentials = {}

    for name in credential_names:
        value = os.environ.get(name)
        if value is None:
            logging.error(f"Environment variable {name} is missing or not set.")
            exit(1)
        else:
            credentials[name.lower()] = value

    return credentials

# Get the result of the poll and return 1 if the dog wins or 0 if the cat wins.
def get_poll_result(tweet_id):
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
    }

    tweet_url = "https://cdn.syndication.twimg.com/tweet-result?id=" + tweet_id + "&lang=en&token=43o65d9fmio&lxvfuk=1akqhnn8ol4bf&m9qcvb=1su9o8cqfz9i&owvzoi=3ifhy8bwxy24&0am1nx=1sq878bh56qz&x8k65v=ld8ouhz6i76&raa2x0=gb8h79gke6nc&qtdsuj=1w58l0oopvpn&217cxh=57zl8ngu1mnj&k0bcu0=vbk8io7e8t3"
    
    try:
        with httpx.Client(http2=False, headers=HEADERS) as client:
            response = client.get(tweet_url)
            response.raise_for_status()  # Raises an exception if status code is not 200
            data = response.json()

            dog_count = int(data['card']['binding_values']['choice1_count']['string_value'])
            cat_count = int(data['card']['binding_values']['choice2_count']['string_value'])
            
            return dog_count, cat_count

    except httpx.HTTPError as http_error:
        logging.error("get_poll_result() HTTP error: %s", http_error)
        exit(1)

    except (KeyError, ValueError) as e:
        logging.error("get_poll_result() Error: %s", e)
        exit(1)


# Function to get a picture of a cat or dog and return the image's url
def get_cat_or_dog_picture(dog_api_key, poll_result):
    HEADERS = {
        'x-api-key': dog_api_key
    }
    url = ""

    if poll_result == Poll_result.Tie:
        return url

    if poll_result == Poll_result.Dog:
        url = "https://api.thedogapi.com/v1/images/search"
    else:
        url = "https://api.thecatapi.com/v1/images/search"

    with httpx.Client(http2=False, headers=HEADERS) as client:
        response = client.get(
            url,
        )
        try:
            assert response.status_code == 200
        except AssertionError as e:
            logging.error("get_cat_or_dog_picture() AssertionError: %s", response.status_code)
            exit(1)
        data = response.json()
    return data[0]['url']

# Download locally the picture from the url, then upload it on Twitter. Return the media_id
def upload_picture(consumer_key, consumer_secret, access_token, access_token_secret, url):
    try:
        auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        
        if url != "":
            # Download the image from the URL
            image_response = requests.get(url, stream=True)
            image_path = 'temp_image.jpg'  # Provide a filename to save the image temporarily
            with open(image_path, 'wb') as image_file:
                for chunk in image_response.iter_content(chunk_size=8192):
                    image_file.write(chunk)
        else:
            image_path = "tie.jpeg"

        # Upload the image to Twitter
        media = api.media_upload(image_path)
        return media.media_id

    except Exception as e:
        logging.error("upload_picture() Error: %s", e)
        exit(1)

def db_connect(db_host, db_port, db_user, db_user_pass, db_name, cert_path):
    try:
        db = pymysql.connect(
            host=db_host,
            port=int(db_port),
            user=db_user,
            passwd=db_user_pass,
            db=db_name,
            ssl={'ssl': {'ca': cert_path}}
        )
        return db
    except Exception as e:
        logging.error("db_connect() Error: %s", e)
        exit(1)

def get_last_poll_id(db):
    try:
        cursor = db.cursor()
        cursor.execute('SELECT poll_id FROM Polls WHERE id = (SELECT MAX(id) FROM Polls as latest_id)')
        data = cursor.fetchone()[0]
        return data
    except Exception as e:
        logging.error("get_last_poll_id() Error: %s", e)
        exit(1)

def update_poll(db, poll_id, dog_count, cat_count):
    try:
        winner = "Dog" if dog_count > cat_count else ("Cat" if cat_count > dog_count else "Tie")

        cursor = db.cursor()
        cursor.execute('UPDATE Polls SET dog_votes = %s, cat_votes = %s, winner = %s WHERE poll_id = %s', (dog_count, cat_count, winner, poll_id))
        db.commit()
    except Exception as e:
        logging.error("update_poll() Error: %s", e)
    
def create_poll(db, poll_id):
    try:
        cursor = db.cursor()
        cursor.execute('''INSERT INTO Polls (date, poll_id, cat_votes, dog_votes, winner) VALUES (%s, %s, 0, 0, '')''', (datetime.datetime.now(), poll_id))
        db.commit()
    except Exception as e:
        logging.error("create_poll() Error: %s", e)
        exit(1)

def get_total_number_polls(db):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT count(*) FROM Polls")
        data = cursor.fetchone()[0]
        return data
    except Exception as e:
        logging.error("get_total_number_polls() Error: %s", e)
        exit(1)

def get_win_streak(db, winner):
    try:
        cursor = db.cursor()
        cursor.execute("SET @count=0")
        cursor.execute(
            "SELECT @count:=IF(a.winner = b.winner, @count + 1, 1) as Streak, a.id FROM Polls AS a "
            "LEFT JOIN Polls AS b on a.id = b.id + 1 WHERE a.winner = %s ORDER BY a.date DESC",
            (winner,)
        )
        data = cursor.fetchone()

        if data is not None:
            return data[0]
        else:
            return 0
    except Exception as e:
        logging.error("get_win_streak() Error: %s", e)
        exit(1)

# Main loop for running the bot
def main():

    logging_setup()

    credentials = get_credentials()
    db = db_connect(credentials['db_host'], credentials['db_port'], credentials['db_user'], credentials['db_user_pass'], credentials['db_name'], credentials['cert_path'])
    tweet_id = get_last_poll_id(db)

    client = tweepy.Client(consumer_key=credentials['consumer_key'],
                        consumer_secret=credentials['consumer_secret'],
                        access_token=credentials['access_token'],
                        access_token_secret=credentials['access_token_secret'])
    
    dog_count, cat_count = get_poll_result(tweet_id)
    
    if dog_count > cat_count:
        poll_result = Poll_result.Dog
    elif cat_count > dog_count:
        poll_result = Poll_result.Cat
    else:
        poll_result = Poll_result.Tie 

    update_poll(db, tweet_id, dog_count, cat_count)

    image_url = get_cat_or_dog_picture(credentials['dog_api_key'], poll_result)
    media_id = upload_picture(credentials['consumer_key'], credentials['consumer_secret'], credentials['access_token'], credentials['access_token_secret'], image_url)
    
    streak = get_win_streak(db, poll_result.name)
    poll_number = get_total_number_polls(db)

    if poll_result == Poll_result.Tie:
        text = "It's a tie! No one won today ...\n\nVote for tomorrow's winner in the first reply ↓ ! #"+ str(poll_number)+"\n\n#dog #cat #fight"
    else:
        text = poll_result.name + " wins for the " + str(streak) + " days in a row!\n\nVote for tomorrow's winner in the first reply ↓ ! #"+ str(poll_number)+"\n\n#dog #cat #fight"
    
    response = client.create_tweet(media_ids=[media_id], text=text)

    image_tweet_id = response.data['id']
    response = client.create_tweet(poll_options=['Dog', 'Cat'], poll_duration_minutes=1380, text='Who is the best?', in_reply_to_tweet_id=image_tweet_id)

    create_poll(db, response.data['id'])

    print(response)

    db.close()

# Run the bot
if __name__ == "__main__":
    
    main()

