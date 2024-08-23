from data import config
from Tests.testdata import getTestData
from library.activityFunctions import composeMail, composeFollowupEmail
from library.googleSheetsAPI import Hill
from library.smtp import sendEmails, Email
from library.StravaAPI import getActivityById
from pytest_mock import MockerFixture

testData = getTestData()
settings = config.getConfig()

def test_sendEmail(mocker: MockerFixture):

    # mock the smtplib.SMTP_SSL object
    mock_SMTP = mocker.MagicMock(name="library.smtp.smtplib.SMTP_SSL")
    mocker.patch("library.smtp.smtplib.SMTP_SSL", new=mock_SMTP)

    html = config.getHTMLTemplate('Email.html')

    hill1 = Hill(id=1, name='Hill1', latitude=0.0, longitude=0.0, done=True, Area='Area1', Highest100=True, Height=1000)
    hill2 = Hill(id=2, name='Hill2', latitude=0.0, longitude=0.0, done=True, Area='Area2', Highest100=True, Height=1000)
    hill3 = Hill(id=3, name='Hill3', latitude=0.0, longitude=0.0, done=False, Area='Area3', Highest100=False, Height=1000)

    allHills = [hill1, hill2, hill3]
    activity = getActivityById(testData.ActivityWithHills)
    activity.hills = [hill1, hill2]
    html = composeMail(html, activity, allHills)
    sendEmails([Email(html= html, address= testData.TestEmail, subject= 'Test')
                ,Email(html= html, address= testData.TestEmail, subject= 'Test2')])

    assert mock_SMTP.return_value.__enter__.return_value.login.call_count == 1
    assert mock_SMTP.return_value.__enter__.return_value.sendmail.call_count == 2
    assert mock_SMTP.return_value.__enter__.return_value.sendmail.call_args.args[1] == testData.TestEmail


def test_sendFollowupEmail(mocker: MockerFixture):

    # mock the smtplib.SMTP_SSL object
    mock_SMTP = mocker.MagicMock(name="library.smtp.smtplib.SMTP_SSL")
    mocker.patch("library.smtp.smtplib.SMTP_SSL", new=mock_SMTP)

    html = config.getHTMLTemplate('FollowUpEmail.html')
    html = composeFollowupEmail(html, testData.ActivityWithHills)
    sendEmails([Email(html= html, address= testData.TestEmail, subject= 'Test')])

    assert mock_SMTP.return_value.__enter__.return_value.login.call_count == 1
    assert mock_SMTP.return_value.__enter__.return_value.sendmail.call_count == 1
    assert mock_SMTP.return_value.__enter__.return_value.sendmail.call_args.args[1] == testData.TestEmail
