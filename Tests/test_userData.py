from data import userDAO
from data.hillsDAO import Hill
import time
from Tests.testdata import getTestData

testData = getTestData()

def test_getUser():
    start_time = time.time()  
    user = userDAO.getUser(userId=testData.UserId)
    end_time = time.time()    
    elapsed_time = end_time - start_time 

    assert user
    assert user.hill_lists
    assert user.email == testData.UserEmail
    for hillList in user.hill_lists:
        assert all([isinstance(hill, Hill) for hill in hillList.hills])
    assert elapsed_time < 0.5

    hills = user.getAllHills()
    assert hills
    assert len([hill.id for hill in hills]) == len({hill.id for hill in hills}) #Assert no duplicates

def test_getUserHillList():
    hillList = userDAO.getUserHillList(testData.UserId, testData.HillListID)
    assert hillList
    assert hillList.name == testData.HillListName
    assert len(hillList.hills) == testData.HillListCount
    assert hillList.numberCompleted == len([hill for hill in hillList.hills if hill.done])

def test_markHillsCompleted():
    user = userDAO.getUser(userId=testData.TestUserId)
    assert user.hill_lists[0].numberCompleted == 0
    _, _, user_data = userDAO.getRawUserData(userId=testData.TestUserId)
    assert len(user_data['completed_hills']) == 0
    
    user.recordCompletedHills([testData.HillID, testData.HillID2], 12345)
    assert user.hill_lists[0].numberCompleted == 2
    _, _, user_data = userDAO.getRawUserData(userId=testData.TestUserId)
    assert len(user_data['completed_hills']) == 2

    user.deleteCompletedHills([testData.HillID, testData.HillID2])
    assert user.hill_lists[0].numberCompleted == 0
    _, _, user_data = userDAO.getRawUserData(userId=testData.TestUserId)
    assert len(user_data['completed_hills']) == 0


def test_updateStravaTokens():
    user = userDAO.getUser(userId=testData.TestUserId)
    assert user.strava_access_token == '123ABC'
    assert user.strava_refresh_token == 'ABC123'

    user.updateStravaTokens('NewAccessToken', 'NewRefreshToken')
    
    #Assert object values have been updated
    assert user.strava_access_token == 'NewAccessToken'
    assert user.strava_refresh_token == 'NewRefreshToken'
    
    #Assert db values have been updated
    user = None
    user = userDAO.getUser(userId=testData.TestUserId)
    assert user.strava_access_token == 'NewAccessToken'
    assert user.strava_refresh_token == 'NewRefreshToken'

    user.updateStravaTokens('123ABC', 'ABC123')


def test_deleteActivity():
    user = userDAO.getUser(userId=testData.TestUserId)
    user.recordCompletedHills([testData.HillID, testData.HillID2], 12345)
    user.recordCompletedHills([testData.HillID3], 54321)
    assert user.hill_lists[0].numberCompleted == 3

    user.deleteActivity(12345)
    assert user.hill_lists[0].numberCompleted == 1
    _, _, user_data = userDAO.getRawUserData(userId=testData.TestUserId)
    assert len(user_data['completed_hills']) == 1

    user.deleteCompletedHills([testData.HillID3])
    assert user.hill_lists[0].numberCompleted == 0

      

