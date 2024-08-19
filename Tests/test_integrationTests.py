from library import StravaAPI
from library import activityFunctions
from data.config import getUnkudosedNotifications
from Tests.testdata import getTestData
from pytest_mock import MockerFixture

testData = getTestData()

def test_processActivityWithHills(mocker: MockerFixture):
    
    # mock the smtplib.SMTP_SSL object
    mock_SMTP = mocker.MagicMock(name="library.smtp.smtplib.SMTP_SSL")
    mocker.patch("library.smtp.smtplib.SMTP_SSL", new=mock_SMTP)

    #mock writing notifications
    mocker.patch('library.activityFunctions.config.writeNotification')
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


def test_processActivityWithoutHills(mocker: MockerFixture):
    
    # mock the smtplib.SMTP_SSL object
    mock_SMTP = mocker.MagicMock(name="library.smtp.smtplib.SMTP_SSL")
    mocker.patch("library.smtp.smtplib.SMTP_SSL", new=mock_SMTP)

    #mock writing notifications
    mocker.patch('library.activityFunctions.config.writeNotification')
    count = len(getUnkudosedNotifications())

    hasHills, hills = activityFunctions.processActivity(testData.ActivityWithoutHills)
    assert not hasHills
    assert len(hills) == 0

    #assert no notifications have been added
    assert len(getUnkudosedNotifications()) == count


def test_processActivity(mocker: MockerFixture):   

    # mock the smtplib.SMTP_SSL object
    mock_SMTP = mocker.MagicMock(name="library.smtp.smtplib.SMTP_SSL")
    mocker.patch("library.smtp.smtplib.SMTP_SSL", new=mock_SMTP)

    #mock writing notifications
    mocker.patch('library.activityFunctions.config.writeNotification')
    count = len(getUnkudosedNotifications())

    activityFunctions.processActivity(testData.ActivityID)

    #assert no notifications have been added
    assert len(getUnkudosedNotifications()) == count


def test_bullyRecipients(mocker: MockerFixture):

    # mock the smtplib.SMTP_SSL object
    mock_SMTP = mocker.MagicMock(name="library.smtp.smtplib.SMTP_SSL")
    mocker.patch("library.smtp.smtplib.SMTP_SSL", new=mock_SMTP)

    activityFunctions.bullyRecipients()
