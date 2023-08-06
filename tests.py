import unittest
from unittest.mock import Mock, patch
from main import *

class TestBotFunctions(unittest.TestCase):

    @patch('httpx.Client.get')
    def test_get_poll_result(self, mock_get):
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
        mock_get.return_value = mock_response

        dog_count, cat_count = get_poll_result('1234567890')

        self.assertEqual(dog_count, 12)
        self.assertEqual(cat_count, 10)

    @patch('httpx.Client.get')
    def test_get_cat_or_dog_picture(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{'url': 'https://example.com/image.jpg'}]
        mock_get.return_value = mock_response

        cat_url = get_cat_or_dog_picture(False)
        dog_url = get_cat_or_dog_picture(True)

        self.assertEqual(cat_url, 'https://example.com/image.jpg')
        self.assertEqual(dog_url, 'https://example.com/image.jpg')

    @patch('tweepy.API.media_upload')
    @patch('requests.get')
    def test_upload_picture(self, mock_get, mock_media_upload):
        mock_get.return_value.status_code = 200
        mock_get.return_value.iter_content.return_value = [b'some', b'content']

        mock_media = Mock()
        mock_media.media_id = '1234567890'
        mock_media_upload.return_value = mock_media

        media_id = upload_picture('https://example.com/image.jpg')

        self.assertEqual(media_id, '1234567890')

    @patch('pymysql.connect')
    def test_db_connect(self, mock_connect):
        db = db_connect()

        self.assertIsNotNone(db)

    @patch('pymysql.connect')
    def test_get_last_poll_id(self, mock_connect):
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = [1234567890]
        mock_connect.return_value.cursor.return_value = mock_cursor

        last_poll_id = get_last_poll_id(mock_connect)

        self.assertEqual(last_poll_id, 1234567890)

    @patch('pymysql.connect')
    def test_update_poll(self, mock_connect):
        mock_cursor = Mock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        update_poll(mock_connect, 1234567890, 12, 10)

        mock_cursor.execute.assert_called_once_with(
            'UPDATE Polls SET dog_votes = %s, cat_votes = %s, winner = %s  WHERE poll_id = %s',
            (12, 10, 'Dog', 1234567890)
        )

    # ... Add more test cases for other functions ...

if __name__ == '__main__':
    unittest.main()
