import StravaAPI
import activityFunctions
import webhookReceiver
import json

class TestData:
    def __init__(self, data: dict):
        self.ActivityWithHills = data.get("ActivityWithHills")
        self.ActivityWithoutHills = data.get("ActivityWithoutHills")
        self.Hills = data.get("Hills")

def getTestData() -> TestData:
    with open('Tests/testData.json') as file:
        test_data_json = json.load(file)
        settings = TestData(test_data_json)
    return settings

def test_processActivityWithHills():
    testData = getTestData()
    hasHills, hills = activityFunctions.processActivity(testData.ActivityWithHills)
    assert hasHills
    hillnames = [x.name for x in hills]
    assert hillnames == testData.Hills
    activity = StravaAPI.getActivityById(testData.ActivityWithHills)
    for hillName in testData.Hills:
        assert hillName in activity.description

def test_processActivityWithoutHills():
    testData = getTestData()
    hasHills, hills = activityFunctions.processActivity(testData.ActivityWithoutHills)
    assert not hasHills
    assert len(hills) == 0

def test_processWebhook_WithHills(capfd):
    testData = getTestData()
    webhookReceiver.handleWebhook(testData.ActivityWithHills)
    out, _ = capfd.readouterr()
    assert out == 'Activity:' + str(testData.ActivityWithHills) + ' processed\nDescription updated\n'

def test_processWebhook_WithoutHills(capfd):
    testData = getTestData() 
    webhookReceiver.handleWebhook(testData.ActivityWithoutHills)
    out, _ = capfd.readouterr()
    assert out == 'Activity:' + str(testData.ActivityWithoutHills) + ' processed\n'
