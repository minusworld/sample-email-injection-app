# NOTICE

!!! This is a sample application that demonstrates bad email use. Do not use this. !!!

## And now, your regularly scheduled program

A quick-and-dirty app for coordinating shared rooms for events! The app uses a style like classified ads; or the more modern variant, [Craigslist](www.craigslist.org). Hosts can post availability and seekers can post seekability.

## Installation

This is a Flask app, designed to be deployed anywhere a Flask app can go! When this was live, it was hosted using AWS's Elastic Beanstalk.

## Development

I do, however, have instructions for development!

1. Run DynamoDB locally.
1. Initialize the virtual environment using `pipenv` and install dependendies.
1. Set up environment variables.
1. Run the app!

### Run DynamoDB locally.

This app uses `pynamodb` which uses an ORM-like syntax for working with [AWS's DynamoDB](https://aws.amazon.com/dynamodb/). AWS provides a [really convinient Docker image](https://hub.docker.com/r/amazon/dynamodb-local/) for testing integration with DynamoDB locally.

If you don't have Docker installed, [install Docker](https://docs.docker.com/get-docker/).

Pull and run the DynamoDB docker container:

```bash
$ docker pull amazon/dynamodb-local
$ docker run -p 8000:8000 amazon/dynamodb-local
Initializing DynamoDB Local with the following configuration:
Port:   8000
InMemory:       true
DbPath: null
SharedDb:       false
shouldDelayTransientStatuses:   false
CorsParams:     *
```

The local instance of DynamoDB is now running. To use the local instance of DynamoDB, you'll need to set the `app_env` environment variable. More on this is in "Set up environment variables."

### Initialize the virtual environment using `pipenv` and install dependendies.

This app uses `pipenv` to manage dependencies. You'll need:
- flask
- flask-talisman
- pynamodb

Install `pipenv` if you don't have it:

```bash
$ pip install pipenv
```

On Mac, `brew` also works:

```bash
$ brew install pipenv
```

Drop into a `pipenv shell` and install dependendies.

```bash
$ pipenv shell
(roomshare) $ pipenv install
```

### Set up environment variables.

This app needs a few things from you to run properly.
1. The app will send emails to sign-ups on your behalf, so it will need to know the SMTP server information and a login.
1. The app will also need to know its base URL to generate links.
1. Lastly, the app needs to know if it is running locally or in production.

You'll need to set the folloing environment variables:

```bash
export base_url="http://localhost:5000"
export smtp_sender_email=""
export smtp_server=""
export smtp_username=""
export smtp_password=""
export app_env="LOCAL"
```

`smtp_sender_email` is the email that will be put in the `FROM:` field of emails.

`smtp_server` is the SMTP server address. For example, Gmail's address is `smtp.gmail.com`.

`smtp_username` is the username login for the SMTP server.

`smtp_password` is the password for the username on the SMTP server.

You can see how to set this up in Gmail at [this link](https://stackabuse.com/how-to-send-emails-with-gmail-using-python/).

`app_env` is optional. If it is `LOCAL` it will use the local instance of DynamoDB running on port 8000. If ommitted, it will try to use your AWS credentials to create a DynamoDB table.

### Run the app!

```bash
(roomshare) $ python application.py
```
