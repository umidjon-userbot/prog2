HEROKU = False  # NOTE Make it false if you're not deploying on heroku.

# NOTE these values are for heroku.
if HEROKU:
    from os import environ

    API_ID = int(environ["API_ID"])
    API_HASH = environ["API_HASH"]
    SESSION_STRING = environ["SESSION_STRING"]  # Check Readme for session
    ARQ_API_KEY = environ["ARQ_API_KEY"]

# NOTE Fill this if you are not deploying on heroku.
if not HEROKU:
    API_ID =  1142474
    API_HASH = "d69d7397d46403cec4de1babe63ef35b"
    ARQ_API_KEY = "DDNBVO-XADJDI-GEFBDV-YFEGHV-ARQ"
    SUDOERS = [660086073]
# don't make changes below this line
ARQ_API = "https://thearq.tech"
