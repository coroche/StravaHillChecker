from library import StravaAPI
from library import activityFunctions
from data.config import getUnkudosedNotifications
from Tests.testdata import getTestData
from pytest import fixture
from pytest_mock import MockerFixture

testData = getTestData()

@fixture(autouse=True)
def mock_WriteNotification(mocker: MockerFixture):
    mocked_writeNotification = mocker.patch('library.activityFunctions.config.writeNotification')
    return mocked_writeNotification

def test_processActivityWithHills():

    count = len(getUnkudosedNotifications())

    hasHills, hills = activityFunctions.processActivity(testData.ActivityWithHills, ignoreTimeDiff=True)
    assert hasHills
    hillNames = [x.name for x in hills]
    assert hillNames == testData.Hills
    activity = StravaAPI.getActivityById(testData.ActivityWithHills)
    for hillName in testData.Hills:
        assert hillName in activity.description

    #assert no notifications have been added
    assert len(getUnkudosedNotifications()) == count


def test_processActivityWithoutHills():

    count = len(getUnkudosedNotifications())

    hasHills, hills = activityFunctions.processActivity(testData.ActivityWithoutHills)
    assert not hasHills
    assert len(hills) == 0

    #assert no notifications have been added
    assert len(getUnkudosedNotifications()) == count


def test_processActivity():   

    count = len(getUnkudosedNotifications())

    activityFunctions.processActivity(testData.ActivityID)

    #assert no notifications have been added
    assert len(getUnkudosedNotifications()) == count


def test_bullyRecipients():

    activityFunctions.bullyRecipients()
