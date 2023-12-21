import library.StravaAPI as StravaAPI
import library.activityFunctions as activityFunctions
from Tests.testdata import getTestData

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

def test_processActivity():   
    activityFunctions.processActivity(testData.ActivityID)

def test_bullyReceipients():
    activityFunctions.bullyReceipients()
