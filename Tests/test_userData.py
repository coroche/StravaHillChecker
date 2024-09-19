from data import userDAO
from data.hillsDAO import Hill
import time
from Tests.testdata import getTestData

testData = getTestData()

def test_getUser():
    start_time = time.time()  
    user = userDAO.getUser(testData.UserId)
    end_time = time.time()    
    elapsed_time = end_time - start_time 

    assert user
    assert user.hill_lists
    assert user.email == testData.UserEmail
    for hillList in user.hill_lists:
        assert all([isinstance(hill, Hill) for hill in hillList.hills])
    assert elapsed_time < 0.5

