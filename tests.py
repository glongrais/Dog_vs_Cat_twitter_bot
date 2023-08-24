import pytest
from unittest.mock import Mock, call, patch, ANY
from main import *

# Mock fixtures
@pytest.fixture
def mock_httpx_client_get():
    with patch('httpx.Client.get') as mock_get:
        yield mock_get

@pytest.fixture
def mock_tweepy_client():
    with patch('tweepy.Client.create_tweet') as mock_create_tweet, \
         patch('tweepy.API.media_upload') as mock_media_upload:
        yield mock_create_tweet, mock_media_upload

@pytest.fixture
def mock_pymysql_connect():
    with patch('pymysql.connect') as mock_connect:
        mock_db = Mock()
        mock_db.cursor.return_value = Mock()
        mock_connect.return_value = mock_db
        yield mock_connect

@pytest.fixture
def mock_requests_get():
    with patch('requests.get') as mock_request:
        yield mock_request

@pytest.fixture
def mock_db_connect():
    with patch('main.db_connect') as mock_connect:
        mock_db = Mock()
        mock_db.cursor.return_value = Mock()
        mock_connect.return_value = mock_db
        yield mock_connect

def test_get_poll_result(mock_httpx_client_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'card': {
            'binding_values': {
                'choice1_count': {'string_value': '12'},
                'choice2_count': {'string_value': '10'}
            }
        }
    }
    mock_httpx_client_get.return_value = mock_response

    dog_count, cat_count = get_poll_result('1234567890')

    assert dog_count == 12
    assert cat_count == 10

def test_get_last_poll_id(mock_pymysql_connect):
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = [1234567890]
    mock_pymysql_connect.cursor.return_value = mock_cursor

    last_poll_id = get_last_poll_id(mock_pymysql_connect)

    assert last_poll_id == 1234567890

def test_update_poll_Dog_Win(mock_pymysql_connect):
    mock_cursor = Mock()
    mock_pymysql_connect.cursor.return_value = mock_cursor

    update_poll(mock_pymysql_connect, 1234567890, 12, 10)

    mock_cursor.execute.assert_called_once_with("UPDATE Polls SET dog_votes = %s, cat_votes = %s, winner = %s WHERE poll_id = %s", (12, 10, 'Dog', 1234567890))

def test_update_poll_Cat_Win(mock_pymysql_connect):
    mock_cursor = Mock()
    mock_pymysql_connect.cursor.return_value = mock_cursor

    update_poll(mock_pymysql_connect, 1234567890, 12, 15)

    mock_cursor.execute.assert_called_once_with("UPDATE Polls SET dog_votes = %s, cat_votes = %s, winner = %s WHERE poll_id = %s", (12, 15, 'Cat', 1234567890))

def test_update_poll_Tie(mock_pymysql_connect):
    mock_cursor = Mock()
    mock_pymysql_connect.cursor.return_value = mock_cursor

    update_poll(mock_pymysql_connect, 1234567890, 15, 15)

    mock_cursor.execute.assert_called_once_with("UPDATE Polls SET dog_votes = %s, cat_votes = %s, winner = %s WHERE poll_id = %s", (15, 15, 'Tie', 1234567890))

def test_get_total_number_polls(mock_pymysql_connect):
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = [42]
    mock_pymysql_connect.cursor.return_value = mock_cursor

    total_number_polls = get_total_number_polls(mock_pymysql_connect)

    assert total_number_polls == 42

def test_get_win_streak(mock_pymysql_connect):
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = [3]  # Simulating 3 days of win streak
    mock_pymysql_connect.cursor.return_value = mock_cursor

    win_streak = get_win_streak(mock_pymysql_connect, 'Dog')

    assert win_streak == 3

def test_get_win_streak_no_results(mock_pymysql_connect):
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = None  # Simulating no results for win streak
    mock_pymysql_connect.cursor.return_value = mock_cursor

    win_streak = get_win_streak(mock_pymysql_connect, 'Cat')

    assert win_streak == 0

def test_get_cat_or_dog_picture_dog(mock_httpx_client_get):
    mock_httpx_client_get.return_value.status_code = 200
    mock_httpx_client_get.return_value.json.return_value = [{'url': 'https://dog.example.com/image.jpg'}]

    dog_url = get_cat_or_dog_picture('fake_dog_api_key', Poll_result.Dog)

    assert dog_url == 'https://dog.example.com/image.jpg'

def test_get_cat_or_dog_picture_cat(mock_httpx_client_get):
    mock_httpx_client_get.return_value.status_code = 200
    mock_httpx_client_get.return_value.json.return_value = [{'url': 'https://cat.example.com/image.jpg'}]

    cat_url = get_cat_or_dog_picture('fake_dog_api_key', Poll_result.Cat)

    assert cat_url == 'https://cat.example.com/image.jpg'

def test_upload_picture(mock_requests_get, mock_tweepy_client):
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.iter_content.return_value = [b'some', b'content']

    mock_media = Mock()
    mock_media.media_id = '1234567890'
    mock_tweepy_client[1].return_value = mock_media

    media_id = upload_picture("consumer_key", "consumer_secret", "access_token", "access_token_secret",'https://example.com/image.jpg')

    assert media_id == '1234567890'

def test_create_poll(mock_pymysql_connect):
    mock_cursor = Mock()
    mock_pymysql_connect.cursor.return_value = mock_cursor
    mock_cursor.execute.return_value = 0

    create_poll(mock_pymysql_connect, '1234567890')

    assert mock_cursor.execute.called

    expected_call = call('''INSERT INTO Polls (date, poll_id, cat_votes, dog_votes, winner) VALUES (%s, %s, 0, 0, '')''', (ANY, '1234567890'))
    
    mock_cursor.execute.assert_has_calls([expected_call])

# Test the main function
@patch('os.environ.get', side_effect=lambda key: {
    "DOG_API_KEY": "fake_dog_api_key",
    "CONSUMER_KEY": 'fake_key',
    "CONSUMER_SECRET": 'fake_secret',
    "ACCESS_TOKEN": 'fake_token',
    "ACCESS_TOKEN_SECRET": 'fake_token_secret',
    "DB_HOST": 'fake_host',
    "DB_PORT": 0,
    "DB_USER": 'fake_user',
    "DB_USER_PASS": 'fake_pass',
    "DB_NAME": 'fake_name',
    "CERT_PATH": '/fake/path'}.get(key, None)) 
def test_main_function(mock_env_get, mock_httpx_client_get, mock_tweepy_client, mock_requests_get, mock_db_connect):
    # Mock data and behaviors for httpx
    mock_httpx_client_get.return_value.status_code = 200
    # Define a side effect function that returns different values based on the URL
    def httpx_side_effect(*args, **kwargs):
        mock_response = Mock()
        if 'https://cdn.syndication.twimg.com/tweet-result?id=1234567890&lang=en' in args[0]:
            mock_response.json.return_value =  {
                'card': {
                    'binding_values': {
                        'choice1_count': {'string_value': '12'},
                        'choice2_count': {'string_value': '10'}
                    }
                }
            }
            mock_response.status_code = 200
            return mock_response
        elif args[0] == 'https://api.thedogapi.com/v1/images/search':
            mock_response.json.return_value = [{'url': 'https://example.url.com'}]
            mock_response.status_code = 200
            return mock_response
        else:
            raise ValueError("Unexpected URL: " + args[0])

    # Set up httpx_client.get to use the custom side effect function
    mock_httpx_client_get.side_effect = httpx_side_effect

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.iter_content.return_value = [b'some', b'content']
    mock_requests_get.return_value = mock_response

    # Mock data and behaviors for tweepy
    mock_create_tweet, mock_media_upload = mock_tweepy_client
    mock_create_tweet.return_value.data = {'id': '12345'}
    mock_media_upload.return_value.media_id = '67890'

    # Mock data and behaviors for pymysql
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = ["1234567890"]
    mock_db_connect.return_value.cursor.return_value = mock_cursor

    # Run the main bot logic
    main()

    # Add assertions to verify expected behaviors
    assert mock_create_tweet.called
    assert mock_media_upload.called