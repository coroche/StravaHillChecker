from dataclasses import dataclass, asdict
from utils.decorators import trim
from data.config import db
from data.hillsDAO import getHillList, HillList, Hill

@trim
@dataclass
class User:
    id: str
    email: str
    athlete_id: int
    hill_lists: list[HillList]
    

def getUser(userId: str, updateHillCounts: bool = False) -> User:
    hill_lists: list[HillList] = []

    user_doc = db.collection('users').document(userId)
    user_data = user_doc.get().to_dict()
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
            counts[hill_list.id] = len([hill for hill in hill_list.hills if hill.done])
        
        for hill_list in user_data_hill_lists:
            hill_list['numberCompleted'] = counts[hill_list['list'].id]
        
        user_doc.update({
            'hill_lists': user_data_hill_lists
        })

    return User(id=userId, hill_lists=hill_lists, **user_data)

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


def recordCompletedHills(userId: str, hillIds: list[str], activityId: int, user_data: dict = None) -> User:
    user_doc = db.collection('users').document(userId)

    if not user_data:
        user_data = user_doc.get().to_dict()

    completed_hills = {}
    if 'completed_hills' in user_data.keys():
        completed_hills = user_data['completed_hills']

    for hillId in hillIds:
        completed_hills[hillId] = activityId

    user_doc.update({
        'completed_hills': completed_hills
    })

    return getUser(userId, updateHillCounts=True)


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