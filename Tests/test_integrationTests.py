import StravaAPI
import activityFunctions
import webhookReceiver
from test_data import getTestData

testData = getTestData()

def test_processActivityWithHills():
    hasHills, hills = activityFunctions.processActivity(testData.ActivityWithHills)
    assert hasHills
    hillnames = [x.name for x in hills]
    assert hillnames == testData.Hills
    activity = StravaAPI.getActivityById(testData.ActivityWithHills)
    for hillName in testData.Hills:
        assert hillName in activity.description

def test_processActivityWithoutHills():   
    hasHills, hills = activityFunctions.processActivity(testData.ActivityWithoutHills)
    assert not hasHills
    assert len(hills) == 0

def test_processWebhook_WithHills(capfd):   
    webhookReceiver.handleWebhook(testData.ActivityWithHills)
    out, _ = capfd.readouterr()
    assert out == 'Activity:' + str(testData.ActivityWithHills) + ' processed\nDescription updated\n'

def test_processWebhook_WithoutHills(capfd):     
    webhookReceiver.handleWebhook(testData.ActivityWithoutHills)
    out, _ = capfd.readouterr()
    assert out == 'Activity:' + str(testData.ActivityWithoutHills) + ' processed\n'

def test_processActivity():   
    activityFunctions.processActivity(testData.ActivityID)

def test_bullyReceipients():
    activityFunctions.bullyReceipients()
