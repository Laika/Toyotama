from flask import Flask
from flask.sessions import SecureCookieSessionInterface


def session_falsification(data, secret_key: bytes):
    class App(Flask):
        def __init__(self, secret_key):
            self.secret_key = secret_key

    app = App(secret_key)
    session_interface = SecureCookieSessionInterface()
    serializer = session_interface.get_signing_serializer(app)
    if not serializer:
        raise RuntimeError("Invalid signing serializer")
    data = serializer.dumps(data)
    return data
