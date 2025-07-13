from dataclasses import dataclass, asdict, field
from utils.decorators import trim
from data import db
from data.hillsDAO import getHillList, HillList, Hill
from google.cloud.firestore import DocumentReference
from google.cloud.firestore_v1.base_query import FieldFilter
from datetime import datetime, timezone, timedelta
from enum import Enum

class StravaLinkStatus(Enum):
    NotInitiated = 0
    Denied = 1
    Connected = 2

@trim
@dataclass
class User:
    id: str
    email: str = ''
    athlete_id: int = 0
    hill_lists: list[HillList] = field(default_factory=list)
    strava_access_token: str = ''
    strava_refresh_token: str = ''
    strava_token_expiry: datetime = datetime(1900,1,1)
    strava_link: int = StravaLinkStatus.NotInitiated.value

    def getAllHills(self) -> list[Hill]:
        seenIds: set[str] = set()
        distinctHills = [
            hill for hill_list in self.hill_lists
            for hill in hill_list.hills
            if hill.id not in seenIds and not seenIds.add(hill.id)
        ]
        return list(distinctHills)
    
    
    def _update_completed_hills(self, hillIds: list[str], modify_func) -> None:
        user_doc = db.collection('users').document(self.id)

        user_data = user_doc.get().to_dict()

        completed_hills: dict[str, int] = user_data.get('completed_hills', {})

        for hillId in hillIds:
            modify_func(completed_hills, hillId)

        user_doc.update({
            'completed_hills': completed_hills
        })

        updated_user = getUser(userId=self.id, updateHillCounts=True)
        self.hill_lists = updated_user.hill_lists


    def recordCompletedHills(self, hillIds: list[str], activityId: int, user_data: dict = None) -> None:
        def add_hill(completed_hills: dict[str, int], hillId: str):
            completed_hills[hillId] = activityId

        self._update_completed_hills(hillIds, add_hill)


    def deleteCompletedHills(self, hillIds: list[str]) -> None:
        def remove_hill(completed_hills: list[str], hillId: str):
            completed_hills.pop(hillId, None)

        self._update_completed_hills(hillIds, remove_hill)


    def deleteActivity(self, activityToDelete: int) -> None:
        user_doc = db.collection('users').document(self.id)
        user_data = user_doc.get().to_dict()
        completed_hills: dict[str, int] = user_data.get('completed_hills', {})
        completed_hills = {hillId: activityId for hillId, activityId in completed_hills.items() if activityId != activityToDelete}
        
        user_doc.update({
            'completed_hills': completed_hills
        })

        updated_user = getUser(userId=self.id, updateHillCounts=True)
        self.hill_lists = updated_user.hill_lists
        

    def updateStravaTokens(self, access_token, refresh_token, expires_in) -> None:
        self.strava_access_token = access_token
        self.strava_refresh_token = refresh_token
        self.strava_token_expiry = (token_expiry:=datetime.now(timezone.utc) + timedelta(seconds=expires_in))
        
        user_doc = db.collection('users').document(self.id)
        user_doc.update({
            'strava_access_token': access_token,
            'strava_refresh_token': refresh_token,
            'strava_token_expiry':token_expiry
        })

    
    def setStravaConnectionData(self, *, athleteId: int = None, scopes: list = None, linkStatus: StravaLinkStatus = None) -> None:
        user_doc = db.collection('users').document(self.id)
        update_dict = {}
        if athleteId:
            update_dict['athlete_id'] = athleteId
        
        if scopes:
            update_dict['strava_scopes'] = scopes

        if linkStatus:
            update_dict['strava_link'] = linkStatus.value
        
        user_doc.update(update_dict)

    
    def removeStravaConnectionData(self) -> None:
        user_doc = db.collection('users').document(self.id)
        user_doc.update({
            'athlete_id': 0,
            'strava_scopes': [],
            'strava_link': StravaLinkStatus.NotInitiated.value,
            'strava_access_token': '',
            'strava_refresh_token': '',
            'strava_token_expiry': datetime(1900,1,1)
        })


def getRawUserData(*, userId: str = None, athleteId: int = None) -> tuple[str | None, DocumentReference | None, dict | None]:
    if not userId:
        query = db.collection('users').where(filter=FieldFilter('athlete_id', '==', athleteId))
        results = query.get()
        if results:
            userId = results[0].id
    
    if not userId:
        return None, None, None
    
    user_doc = db.collection('users').document(userId)
    user_data = user_doc.get().to_dict()
    
    return userId, user_doc, user_data


def getUser(*, userId: str = None, athleteId: int = None, updateHillCounts: bool = False) -> User | None:
    hill_lists: list[HillList] = []

    userId, user_doc, user_data = getRawUserData(userId=userId, athleteId=athleteId)

    user_data_hill_lists = user_data.pop('hill_lists')

    for hill_list in user_data_hill_lists:
        completed = hill_list['numberCompleted']
        userHillList = getHillList(hill_list['list'].id)
        userHillList.numberCompleted = completed

        completedHillsDict = user_data['completed_hills']

        for hill in userHillList.hills:
            if hill.id in completedHillsDict:
                hill.ActivityID = completedHillsDict[hill.id]
                hill.done = True

        hill_lists.append(userHillList)
    
    if updateHillCounts:
        counts = {}
        for hill_list in hill_lists:
            count = len([hill for hill in hill_list.hills if hill.done])
            counts[hill_list.id] = count
            hill_list.numberCompleted = count
        
        for hill_list in user_data_hill_lists:
            hill_list['numberCompleted'] = counts[hill_list['list'].id]
        
        user_doc.update({
            'hill_lists': user_data_hill_lists
        })

    return User(id=userId, hill_lists=hill_lists, **user_data)

def getBasicUser(*, userId: str = None, athleteId: int = None, updateHillCounts: bool = False) -> User | None:
    userId, _, user_data = getRawUserData(userId=userId, athleteId=athleteId)
    if not user_data:
        return None
    
    user_data['hill_lists'] = []
    return User(id=userId, **user_data)


def getUserHillList(userId: str, listId: str) -> HillList | None:
    user_doc = db.collection('users').document(userId)
    user_data = user_doc.get().to_dict()
    if not user_data:
        return None
    
    user_data_hill_lists = user_data.pop('hill_lists')

    hill_list = [hill_list for hill_list in user_data_hill_lists if hill_list['list'].id == listId]
    if not hill_list:
        return None
    
    hill_list = hill_list[0]
    completed = hill_list['numberCompleted']
    userHillList = getHillList(hill_list['list'].id)
    userHillList.numberCompleted = completed

    completedHillsDict = user_data['completed_hills']

    for hill in userHillList.hills:
        if hill.id in completedHillsDict:
            hill.ActivityID = completedHillsDict[hill.id]
            hill.done = True
    
    userHillList_dict = asdict(userHillList)
    userHillList_dict.pop('hills')
    return HillList(hills= userHillList.hills, **userHillList_dict)


def importCompletedHills(userId: str) -> None:
    user_data = db.collection('users').document(userId).get().to_dict()

    completed_hills_dict = {}
    if 'completed_hills' in user_data.keys():
        completed_hills_dict = user_data['completed_hills']

    hills: list[Hill] = []
    #ToDo: Import completed hills from external location

    for hill in hills:
        if hill.done:
            completed_hills_dict[hill.id] = hill.ActivityID

    user_doc = db.collection('users').document(userId)
    user_doc.update({
        'completed_hills': completed_hills_dict
    })
