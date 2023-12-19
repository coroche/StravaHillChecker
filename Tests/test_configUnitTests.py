import config
import test_data

testData = test_data.getTestData()

def test_getConfig():
    settings = config.getConfig()
    settings_dict = test_data.asdict(settings)
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


