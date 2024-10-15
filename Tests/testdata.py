from dataclasses import dataclass
from typing import List
import json

@dataclass
class TestData:
    ActivityWithHills: int
    ActivityWithoutHills: int
    Hills: List[str]
    ActivityID: int
    GCPProject: str
    RecipientID: str
    RecipientEmail: str
    TestEmail: str
    StravaName: str
    HillID: str
    HillID2: str
    HillID3: str
    HillListID: str
    HillListName: str
    HillListCount: int
    UserId: str
    TestUserId: str
    UserEmail: str
    AthleteId: int

def getTestData() -> TestData:
    with open('Tests/testData.json') as file:
        test_data_json = json.load(file)
        test_data = TestData(**test_data_json)
    return test_data