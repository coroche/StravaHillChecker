from library import StravaAPI
from library import activityFunctions
from data.config import getUnkudosedNotifications
from data.userDAO import getUser
from Tests.testdata import getTestData
from pytest import fixture
from pytest_mock import MockerFixture
from collections import Counter

testData = getTestData()

@fixture(autouse=True)
def mock_WriteNotification(mocker: MockerFixture):
    mocked_writeNotification = mocker.patch('library.activityFunctions.config.writeNotification')
    return mocked_writeNotification

def test_processActivityWithHills():

    count = len(getUnkudosedNotifications())

    user = getUser(userId=testData.UserId)
    hasHills, hills = activityFunctions.processActivity(testData.ActivityWithHills, user, ignoreTimeDiff=True)
    assert hasHills
    hillNames = [x.name for x in hills]
    assert Counter(hillNames) == Counter(testData.Hills)
    activity = StravaAPI.getActivityById(user, testData.ActivityWithHills)
    for hillName in testData.Hills:
        assert hillName in activity.description

    #assert no notifications have been added
    assert len(getUnkudosedNotifications()) == count


def test_processActivityWithoutHills():

    count = len(getUnkudosedNotifications())

    user = getUser(userId=testData.UserId)
    hasHills, hills = activityFunctions.processActivity(testData.ActivityWithoutHills, user)
    assert not hasHills
    assert len(hills) == 0

    #assert no notifications have been added
    assert len(getUnkudosedNotifications()) == count


def test_processActivity():   

    count = len(getUnkudosedNotifications())

    user = getUser(userId=testData.UserId)
    activityFunctions.processActivity(testData.ActivityID, user)

    #assert no notifications have been added
    assert len(getUnkudosedNotifications()) == count


def test_bullyRecipients():

    activityFunctions.bullyRecipients()
