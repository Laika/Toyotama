def session_falsification(data, secret_key):
    import flask.sessions

    class App:
        def __init__(self, secret_key):
            self.secret_key = secret_key

    app = App(secret_key)
    si = flask.sessions.SecureCookieSessionInterface()
    s = si.get_signing_serializer(app)
    data = s.dumps(data)
    return data
