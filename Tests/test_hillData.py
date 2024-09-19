from Tests.testdata import getTestData
from data import hillsDAO

testData = getTestData()

def test_getHill():
    hill = hillsDAO.getHillByID(testData.HillID)
    assert hill.name == testData.Hills[0]

def test_getHillList():
    hillList = hillsDAO.getHillList(testData.HillListID)
    assert hillList
    assert hillList.name == testData.HillListName
    assert len(hillList.hills) == testData.HillListCount
