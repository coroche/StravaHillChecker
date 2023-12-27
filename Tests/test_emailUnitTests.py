from data import config
from Tests.testdata import getTestData, asdict
from library.activityFunctions import composeMail, composeFollowupEmail
from library.googleSheetsAPI import Hill
from library.smtp import sendEmail
from library.StravaAPI import getActivityById

testData = getTestData()
settings = config.getConfig()

def test_sendEmail(mocker):

    # mock the smtplib.SMTP_SSL object
    mock_SMTP = mocker.MagicMock(name="library.smtp.smtplib.SMTP_SSL")
    mocker.patch("library.smtp.smtplib.SMTP_SSL", new=mock_SMTP)

    html = config.getEmailTemplate('Email.html')

    hill1 = Hill(1, 'Hill1', 0.0, 0.0, True, 'Area1', True, 1000)
    hill2 = Hill(2, 'Hill2', 0.0, 0.0, True, 'Area2', True, 1000)
    hill3 = Hill(3, 'Hill3', 0.0, 0.0, False, 'Area3', False, 1000)

    activityhills = [hill1, hill2]
    allhills = [hill1, hill2, hill3]
    activity = getActivityById(testData.ActivityWithHills)
    html = composeMail(html, activity, activityhills, allhills)
    sendEmail(html, testData.TestEmail, 'Test')

    assert mock_SMTP.return_value.__enter__.return_value.login.call_count == 1
    assert mock_SMTP.return_value.__enter__.return_value.sendmail.call_count == 1
    assert mock_SMTP.return_value.__enter__.return_value.sendmail.call_args.args[1] == testData.TestEmail


def test_sendFollowupEmail(mocker):

    # mock the smtplib.SMTP_SSL object
    mock_SMTP = mocker.MagicMock(name="library.smtp.smtplib.SMTP_SSL")
    mocker.patch("library.smtp.smtplib.SMTP_SSL", new=mock_SMTP)

    html = config.getEmailTemplate('FollowUpEmail.html')
    html = composeFollowupEmail(html, testData.ActivityWithHills)
    sendEmail(html, testData.TestEmail, 'Test')

    assert mock_SMTP.return_value.__enter__.return_value.login.call_count == 1
    assert mock_SMTP.return_value.__enter__.return_value.sendmail.call_count == 1
    assert mock_SMTP.return_value.__enter__.return_value.sendmail.call_args.args[1] == testData.TestEmail
