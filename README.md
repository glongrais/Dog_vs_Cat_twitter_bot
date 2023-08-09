# Dog vs Cat Twitter Bot

Source code for the Twitter bot [@DogvsCat_Fight](https://twitter.com/DogvsCat_Fight) 

This repository contains a Python script for a Twitter bot that posts daily pictures of cats and dogs, runs polls, and keeps track of the winning streaks.

## Features

- Fetches poll results from Twitter.
- Retrieves cat or dog pictures using external APIs.
- Uploads images to Twitter.
- Keeps track of the winning streaks.
- Runs daily polls for users to vote on the next day's picture.

## Prerequisites

Before running the script, ensure you have the following:

- Python > 3.8
- Twitter API credentials (```CONSUMER_KEY```, ```CONSUMER_SECRET```, ```ACCESS_TOKEN```, ```ACCESS_TOKEN_SECRET```).
- Dog API key (```DOG_API_KEY```).
- MySQL database credentials (```DB_HOST```, ```DB_PORT```, ```DB_USER```, ```DB_USER_PASS```, ```DB_NAME```).
- Path to SSL certificate (```CERT_PATH```). [Optional]

## Configuration

Set up your environment variables:
```Bash
CONSUMER_KEY=your_consumer_key
CONSUMER_SECRET=your_consumer_secret
ACCESS_TOKEN=your_access_token
ACCESS_TOKEN_SECRET=your_access_token_secret
DOG_API_KEY=your_dog_api_key
DB_HOST=your_db_host
DB_PORT=your_db_port
DB_USER=your_db_user
DB_USER_PASS=your_db_user_pass
DB_NAME=your_db_name
CERT_PATH=path_to_ssl_certificate
```

## Contributions

Contributions are welcome! If you find any issues or want to add features, feel free to open a pull request.

## License

This project is licensed under the [MIT License](https://github.com/glongrais/Dog_vs_Cat_twitter_bot/blob/main/LICENSE).
