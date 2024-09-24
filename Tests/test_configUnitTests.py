from data import config
from Tests.testdata import getTestData
from dataclasses import asdict

testData = getTestData()

def test_getConfig():
    settings = config.getConfig()
    settings_dict = asdict(settings)
    assert all(value is not None for value in settings_dict.values())

def test_getParameter():
    smtp_server = config.get('test_parameter')
    assert smtp_server == 'test'

def test_writeParameter():
    config.write('test_parameter', 'hello world!')
    assert config.get('test_parameter') == 'hello world!'
    config.write('test_parameter', 'test')
    assert config.get('test_parameter') == 'test'

def test_getCredentials():
    credentials = config.getCredentials()
    assert credentials['installed']['project_id'] == testData.GCPProject

def test_getToken():
    token = config.getToken()
    assert token

def test_getMailingList():
    mailingList = config.getMailingList()
    assert mailingList

def test_getActivityNotifications():
    activityNotifications = config.getActivityNotifications(testData.ActivityWithHills)
    assert activityNotifications

def test_getUnkudosedNotifications():
    unkudosedNotifications = config.getUnkudosedNotifications(ignoreTimeDiff=True)
    assert unkudosedNotifications
    assert all([not notification.kudos for notification in unkudosedNotifications])

def test_writeAndUpdateNotification():
    config.writeNotification(123, 'ABC123')
    notification = config.getNotification(123, 'ABC123')
    assert notification
    assert not notification.kudos
    config.updateNotification(123, 'ABC123')
    notification = config.getNotification(123, 'ABC123')
    assert notification.kudos
    config.deleteNotification(123, 'ABC123')
    assert not config.getNotification(123, 'ABC123')


def test_getRecipient():
    recipient = config.getRecipient(testData.RecipientID)
    assert recipient.email == testData.RecipientEmail


def test_getHTMLTemplate():
    html = config.getHTMLTemplate('Email.html')
    assert html

def test_createRecipient():
    success, message, id = config.createRecipient('test@mail.com', True, 'John', 'Doe')
    assert success
    recipient = config.getRecipient(id)
    assert recipient.email == 'test@mail.com'
    assert recipient.on_strava
    assert recipient.strava_firstname == 'John'
    assert recipient.strava_lastname == 'D.'
    assert recipient.strava_fullname == 'JohnD.'

    config.deleteRecipient(id)

def test_createRecipient_emailExists():
    success, _, id = config.createRecipient('test@mail.com', True, 'John', 'Doe')
    assert success
    success, message, _ = config.createRecipient('test@mail.com', False)
    assert not success
    assert message == 'Email address already subscribed'
    recipients = config.getRecipientByEmail('test@mail.com')
    assert len(recipients) == 1

    config.deleteRecipient(id)

def test_deleteRecipient():
    success, _, id = config.createRecipient('test@mail.com', False)
    assert success
    recipient = config.getRecipient(id)
    assert recipient.email == 'test@mail.com'
    config.deleteRecipient(id)
    recipients = config.getRecipientByEmail('test@mail.com')
    assert not recipients

def test_deleteNonExistentRecipient():
    id = 'ABC123'
    assert not config.deleteRecipient(id)

def test_verifyRecipientEmail():
    _, _, id = config.createRecipient('test@mail.com', True, 'John', 'Doe')
    recipient = config.getRecipient(id)
    assert not recipient.email_verified
    config.verifyRecipientEmail(id)
    recipient = config.getRecipient(id)
    assert recipient.email_verified
    config.deleteRecipient(id)
