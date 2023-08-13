import pytest
from unittest.mock import Mock, patch
from main import *

# Mock fixture for httpx
@pytest.fixture
def httpx_mock():
    with patch('httpx.Client.get') as mock_get:
        yield mock_get

# Mock fixture for tweepy
@pytest.fixture
def tweepy_mock():
    with patch('tweepy.Client.create_tweet') as mock_create_tweet, \
         patch('tweepy.API.media_upload') as mock_media_upload:
        yield mock_create_tweet, mock_media_upload

# Mock fixture for pymysql
@pytest.fixture
def pymysql_mock():
    with patch('pymysql.connect') as mock_connect:
        mock_db = Mock()
        mock_db.cursor.return_value = Mock()
        mock_connect.return_value = mock_db
        yield mock_connect

@pytest.fixture
def requests_mock():
    with patch('requests.get') as mock_request:
        yield mock_request

@pytest.fixture
def db_mock():
    with patch('main.db_connect') as mock_connect:
        mock_db = Mock()
        mock_db.cursor.return_value = Mock()
        mock_connect.return_value = mock_db
        yield mock_connect

def test_get_poll_result(httpx_mock):
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
    httpx_mock.return_value = mock_response

    dog_count, cat_count = get_poll_result('1234567890')

    assert dog_count == 12
    assert cat_count == 10

def test_get_last_poll_id(pymysql_mock):
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = [1234567890]
    pymysql_mock.cursor.return_value = mock_cursor

    last_poll_id = get_last_poll_id(pymysql_mock)

    assert last_poll_id == 1234567890

def test_update_poll(pymysql_mock):
    mock_cursor = Mock()
    pymysql_mock.cursor.return_value = mock_cursor

    update_poll(pymysql_mock, 1234567890, 12, 10)

    mock_cursor.execute.assert_called_once_with(
        'UPDATE Polls SET dog_votes = %s, cat_votes = %s, winner = %s  WHERE poll_id = %s',
        (12, 10, 'Dog', 1234567890)
    )

def test_get_total_number_polls(pymysql_mock):
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = [42]
    pymysql_mock.cursor.return_value = mock_cursor

    total_number_polls = get_total_number_polls(pymysql_mock)

    assert total_number_polls == 42

def test_get_win_streak(pymysql_mock):
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = [3]  # Simulating 3 days of win streak
    pymysql_mock.cursor.return_value = mock_cursor

    win_streak = get_win_streak(pymysql_mock, 'Dog')

    assert win_streak == 3

def test_get_win_streak_no_results(pymysql_mock):
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = None  # Simulating no results for win streak
    pymysql_mock.cursor.return_value = mock_cursor

    win_streak = get_win_streak(pymysql_mock, 'Cat')

    assert win_streak == 0

# Test the main function
def test_main_function(httpx_mock, tweepy_mock, pymysql_mock, requests_mock, db_mock):
    # Mock data and behaviors for httpx
    httpx_mock.return_value.status_code = 200
    # Define a side effect function that returns different values based on the URL
    def httpx_side_effect(*args, **kwargs):
        mock_response = Mock()
        if args[0] == 'https://cdn.syndication.twimg.com/tweet-result?id=1234567890&lang=en':
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
    httpx_mock.side_effect = httpx_side_effect

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.iter_content.return_value = [b'some', b'content']
    requests_mock.return_value = mock_response

    # Mock data and behaviors for tweepy
    mock_create_tweet, mock_media_upload = tweepy_mock
    mock_create_tweet.return_value.data = {'id': '12345'}
    mock_media_upload.return_value.media_id = '67890'

    # Mock data and behaviors for pymysql
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = ["1234567890"]
    db_mock.return_value.cursor.return_value = mock_cursor

    # Run the main bot logic
    main()

    # Add assertions to verify expected behaviors
    assert mock_create_tweet.called
    assert mock_media_upload.called