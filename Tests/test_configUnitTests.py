from data import config
from Tests.testdata import getTestData, asdict

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
    creds = config.getCredentials()
    assert creds['installed']['project_id'] == testData.GCPProject

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
    unkudosednotifications = config.getUnkudosedNotifications()
    assert unkudosednotifications
    assert all([not notification.kudos for notification in unkudosednotifications])

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


def test_getReceipient():
    receipient = config.getReceipient(testData.ReceipientID)
    assert receipient.email == testData.ReceipientEmail


def test_getEmailTemplate():
    html = config.getEmailTemplate('Email.html')
    assert html

def test_createReceipient():
    success, message, id = config.createReceipient('test@mail.com', True, 'John', 'Doe')
    assert success
    receipient = config.getReceipient(id)
    assert receipient.email == 'test@mail.com'
    assert receipient.on_strava
    assert receipient.strava_firstname == 'John'
    assert receipient.strava_lastname == 'D.'
    assert receipient.strava_fullname == 'JohnD.'

    config.deleteReceipient(id)

def test_createReceipient_emailexists():
    success, _, id = config.createReceipient('test@mail.com', True, 'John', 'Doe')
    assert success
    success, message, _ = config.createReceipient('test@mail.com', False)
    assert not success
    assert message == 'Email address already subscribed'
    receipients = config.getReceipientByEmail('test@mail.com')
    assert len(receipients) == 1

    config.deleteReceipient(id)

def test_deleteReceipient():
    success, _, id = config.createReceipient('test@mail.com', False)
    assert success
    receipient = config.getReceipient(id)
    assert receipient.email == 'test@mail.com'
    config.deleteReceipient(id)
    receipients = config.getReceipientByEmail('test@mail.com')
    assert not receipients

def test_verifyReceipientEmail():
    _, _, id = config.createReceipient('test@mail.com', True, 'John', 'Doe')
    receipient = config.getReceipient(id)
    assert not receipient.email_verified
    config.verifyReceipientEmail(id)
    receipient = config.getReceipient(id)
    assert receipient.email_verified
    config.deleteReceipient(id)
