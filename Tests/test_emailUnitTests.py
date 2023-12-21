import data.config as config
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

    hill1 = {
            '#': 1,
            'Summit or Place': 'Hill1',
            'Latitude': 0.0,
            'Longitude': 0.0,
            'DoneBool': True,
            }
    
    hill2 = {
            '#': 2,
            'Summit or Place': 'Hill2',
            'Latitude': 0.0,
            'Longitude': 0.0,
            'DoneBool': True,
            }
    
    hill3 = {
            '#': 3,
            'Summit or Place': 'Hill3',
            'Latitude': 0.0,
            'Longitude': 0.0,
            'DoneBool': False,
            }

    activityhills = [Hill(hill1), Hill(hill2)]
    allhills = [Hill(hill1), Hill(hill2), Hill(hill3)]
    activity = getActivityById(testData.ActivityWithHills)
    html = composeMail(html, activity, activityhills, allhills)
    sendEmail(html, testData.TestEmail, 'Test')

    assert mock_SMTP.return_value.__enter__.return_value.login.call_count == 1
    assert mock_SMTP.return_value.__enter__.return_value.sendmail.call_count == 1


def test_sendFollowupEmail(mocker):

    # mock the smtplib.SMTP_SSL object
    mock_SMTP = mocker.MagicMock(name="library.smtp.smtplib.SMTP_SSL")
    mocker.patch("library.smtp.smtplib.SMTP_SSL", new=mock_SMTP)

    html = config.getEmailTemplate('FollowUpEmail.html')
    html = composeFollowupEmail(html, testData.ActivityWithHills)
    sendEmail(html, testData.TestEmail, 'Test')

    assert mock_SMTP.return_value.__enter__.return_value.login.call_count == 1
    assert mock_SMTP.return_value.__enter__.return_value.sendmail.call_count == 1