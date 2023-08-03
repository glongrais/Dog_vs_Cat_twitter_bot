import datetime
import tweepy
import os
import httpx
import requests
import pymysql

consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")

dog_api_key = os.environ.get("DOG_API_KEY")

db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("DB_PORT")
db_user = os.environ.get("DB_USER")
db_user_pass = os.environ.get("DB_USER_PASS")
db_name = os.environ.get("DB_NAME")

cert_path = os.environ.get("CERT_PATH")

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

        try:
            dog_count = int(data['card']['binding_values']['choice1_count']['string_value'])
            cat_count = int(data['card']['binding_values']['choice2_count']['string_value'])
        except KeyError as e:
            dog_count = 0
            cat_count = 0
        
        return dog_count, cat_count

# Function to get a picture of a cat or dog and return the image's url
def get_cat_or_dog_picture(is_dog):
    HEADERS = {
        'x-api-key': dog_api_key
    }
    url = ""

    if is_dog:
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

def db_connect():
    db = pymysql.connect(host=db_host, port=int(db_port), user=db_user, passwd=db_user_pass, db=db_name, ssl={'ssl':{'ca': cert_path}})

    return db

def get_last_poll_id(db):
    cursor = db.cursor()
    cursor.execute('SELECT poll_id FROM Polls WHERE id = (SELECT MAX(id) FROM Polls as latest_id)')
    data = cursor.fetchone()[0]

    return data

def update_poll(db, poll_id, dog_count, cat_count):
    winner = ""

    if dog_count > cat_count:
        winner = "Dog"
    elif cat_count > dog_count:
        winner = "Cat"
    else:
        winner = "Tie"

    cursor = db.cursor()
    cursor.execute('UPDATE Polls SET dog_votes = %s, cat_votes = %s, winner = %s  WHERE poll_id = %s', (dog_count, cat_count, winner, poll_id))
    db.commit()
    
def create_poll(db, poll_id):
    cursor = db.cursor()
    cursor.execute('''
    INSERT INTO Polls (date, poll_id, cat_votes, dog_votes, winner) VALUES (%s, %s, 0, 0, '')
    ''', (datetime.datetime.now(), poll_id))
    db.commit()

def get_total_number_polls(db):
    cursor = db.cursor()
    cursor.execute("SELECT count(*) FROM Polls")
    data = cursor.fetchone()[0]

    return data

def get_win_streak(db, winner):
    cursor = db.cursor()
    cursor.execute("SET @count=0")
    cursor.execute("SELECT @count:=IF(a.winner = b.winner, @count + 1, 1) as Streak, a.id FROM Polls AS a LEFT JOIN Polls AS b on a.id = b.id + 1 WHERE a.winner = '"+winner+"' ORDER BY a.date DESC")
    data = cursor.fetchone()[0]

    return data
# Main loop for running the bot
def main():

    db = db_connect()
    tweet_id = get_last_poll_id(db)

    client = tweepy.Client(consumer_key=consumer_key,
                        consumer_secret=consumer_secret,
                        access_token=access_token,
                        access_token_secret=access_token_secret)
    
    dog_count, cat_count = get_poll_result(tweet_id)
    is_dog = dog_count > cat_count

    update_poll(db, tweet_id, dog_count, cat_count)

    image_url = get_cat_or_dog_picture(is_dog)
    media_id = upload_picture(image_url)

    winner = ""

    if is_dog:
        winner = 'Dog'
    else:
        winner = 'Cat'
    
    streak = get_win_streak(db, winner)
    poll_number = get_total_number_polls(db)

    text = winner + " wins for the " + str(streak) + " days in a row!\nVote for tomorrow's winner in the first reply ↓ ! #"+ str(poll_number)
    
    response = client.create_tweet(media_ids=[media_id], text=text)

    image_tweet_id = response.data['id']
    response = client.create_tweet(poll_options=['Dog', 'Cat'], poll_duration_minutes=1380, text='Who is the best?', in_reply_to_tweet_id=image_tweet_id)

    create_poll(db, response.data['id'])

    print(response)

    db.close()

# Run the bot
if __name__ == "__main__":

    print(db_host)
    print(get_cat_or_dog_picture(True))
