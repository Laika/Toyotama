from flask import Flask
from flask.sessions import SecureCookieSessionInterface


def session_falsification(data, secret_key: bytes):
    """Falsify a Flask session cookie with the given data and secret key.

    Args:
        data: The session data to encode.
        secret_key (bytes): The secret key used to sign the session.

    Returns:
        str: The signed session cookie value.
    """
    app = Flask(__name__)
    app.secret_key = secret_key
    session_interface = SecureCookieSessionInterface()
    serializer = session_interface.get_signing_serializer(app)
    if not serializer:
        raise RuntimeError("Invalid signing serializer")
    return serializer.dumps(data)
