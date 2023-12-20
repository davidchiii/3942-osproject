import pytest

import db.db as db

FAKE_DB = "helloworld"
db.db = FAKE_DB
COLLECTION = "users"
FAKE_ID = "test"


@pytest.fixture(scope="function")
def temp_rec():
    db.connect_db(True)
    db.client[FAKE_DB][COLLECTION].insert_one({FAKE_ID: FAKE_ID})
    yield
    db.client[FAKE_DB][COLLECTION].delete_one({FAKE_ID: FAKE_ID})


def test_fetch_one(temp_rec):
    ret = db.client[FAKE_DB][COLLECTION].find_one({FAKE_ID: FAKE_ID})
    assert ret is not None


def test_bad_fetch_one(temp_rec):
    ret = db.client[FAKE_DB][COLLECTION].find_one({FAKE_ID: "BROKEN"})
    assert ret is None
