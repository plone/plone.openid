import Acquisition

class MockRequest:
    ACTUAL_URL = "http://nohost/"
    def __init__(self):
        self.form=dict(SESSION=dict())

    def __getitem__(self, key):
        return self.form.get(key)


class MockPAS(Acquisition.Implicit):
    def __init__(self):
        self.REQUEST=MockRequest()


class MockSite(Acquisition.Implicit):

    def absolute_url(self):
        return "http://nohost/"
