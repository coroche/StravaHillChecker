from data import config, userDAO
from Tests.testdata import getTestData
from library.activityFunctions import composeMail, composeFollowupEmail
from library.googleSheetsAPI import Hill
from library.smtp import sendEmails, Email
from library.StravaAPI import Activity, getPrimaryActivityPhoto

testData = getTestData()
settings = config.getConfig()


def test_sendEmail(mock_SMTP):
    user = userDAO.getUser(userId=testData.UserId)
    html = config.getHTMLTemplate('Email.html')

    hill1 = Hill(id=1, name='Hill1', latitude=0.0, longitude=0.0, done=True, Area='Area1', Highest100=True, Height=1000)
    hill2 = Hill(id=2, name='Hill2', latitude=0.0, longitude=0.0, done=True, Area='Area2', Highest100=True, Height=1000)
    hill3 = Hill(id=3, name='Hill3', latitude=0.0, longitude=0.0, done=False, Area='Area3', Highest100=False, Height=1000)

    allHills = [hill1, hill2, hill3]
    activity = Activity(id=12345, name='Activity1', start_date='2000-01-01T00:00:00Z', start_date_local='2000-01-01T00:00:00Z', sport_type='Hike', distance=1000, moving_time=100, total_elevation_gain=1000, visibility='everyone', private=False, kudos_count=10)
    activity.hills = [hill1, hill2]
    
    backgroundImg = getPrimaryActivityPhoto(user, activity.id)
    html = composeMail(html, activity, allHills, backgroundImg)
    sendEmails([Email(html= html, address= testData.TestEmail, subject= 'Test')
                ,Email(html= html, address= testData.TestEmail, subject= 'Test2')])

    assert mock_SMTP.return_value.__enter__.return_value.login.call_count == 1
    assert mock_SMTP.return_value.__enter__.return_value.sendmail.call_count == 2
    assert mock_SMTP.return_value.__enter__.return_value.sendmail.call_args.args[1] == testData.TestEmail


def test_sendFollowupEmail(mock_SMTP):
    html = config.getHTMLTemplate('FollowUpEmail.html')
    html = composeFollowupEmail(html, 12345)
    sendEmails([Email(html= html, address= testData.TestEmail, subject= 'Test')])

    assert mock_SMTP.return_value.__enter__.return_value.login.call_count == 1
    assert mock_SMTP.return_value.__enter__.return_value.sendmail.call_count == 1
    assert mock_SMTP.return_value.__enter__.return_value.sendmail.call_args.args[1] == testData.TestEmail
    assert 'https://www.strava.com/activities/12345' in mock_SMTP.return_value.__enter__.return_value.sendmail.call_args.args[2]
