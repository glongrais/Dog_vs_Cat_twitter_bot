import pytest
from unittest.mock import Mock, patch
from main import *

@pytest.fixture
def httpx_mock():
    with patch('httpx.Client.get') as mock_get:
        yield mock_get

@pytest.fixture
def tweepy_mock():
    with patch('tweepy.API.media_upload') as mock_media_upload, \
         patch('requests.get') as mock_requests_get:
        yield mock_media_upload, mock_requests_get

@pytest.fixture
def pymysql_mock():
    with patch('pymysql.connect') as mock_connect:
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