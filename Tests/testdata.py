from dataclasses import dataclass, asdict
from typing import List
import json

@dataclass
class TestData:
    ActivityWithHills: int
    ActivityWithoutHills: int
    Hills: List[str]
    ActivityID: int
    GCPProject: str
    ReceipientID: str
    ReceipientEmail: str
    TestEmail: str
    StravaName: str

def getTestData() -> TestData:
    with open('Tests/testData.json') as file:
        test_data_json = json.load(file)
        test_data = TestData(**test_data_json)
    return test_data