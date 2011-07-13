import Acquisition

class MockRequest:
    ACTUAL_URL = "http://nohost/"
    def __init__(self):
        self.form=dict(SESSION=dict())
        self.RESPONSE = {}

    def __getitem__(self, key):
        return self.form.get(key)


class MockPAS(Acquisition.Implicit):
    def __init__(self):
        self.REQUEST=MockRequest()

    def updateCredentials(self, request, response, user_id, new_pw):
        pass

    def getUserById(self, identity):
        return MockUser(identity)


class MockSite(Acquisition.Implicit):

    def absolute_url(self):
        return "http://nohost/"


class MockUser:
    def __init__(self, user_id):
        self.user_id = user_id

    def getId(self):
        return self.user_id
