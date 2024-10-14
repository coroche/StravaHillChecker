from dataclasses import dataclass, asdict
from utils.decorators import trim
from data.config import db
from firebase_admin import firestore 


@trim
@dataclass
class Hill:
    id: str
    name: str
    latitude: float
    longitude: float
    Area: str
    Height: float
    ActivityID: int = None
    done: bool = False

@trim
@dataclass
class HillList:
    id: str
    name: str
    hills: list[Hill]
    numberCompleted: int = None


def addNewHill(hill: Hill) -> None:
    hill_dict = asdict(hill)
    hill_dict.pop('id')
    collection_ref = db.collection('hills')
    collection_ref.add(hill_dict)


def addHillToList(hillPath: str, listRef: str) -> None:
    list_doc = db.collection('hill_lists').document(listRef)
    list_doc.update({
        'hills': firestore.ArrayUnion([db.document(hillPath)])
    })


def populateHills():
    allHills: list[Hill] = []
    #Append hills here
    for hill in allHills:
        addNewHill(hill)


def populateHillList(listRef: str):
    hillDocs = db.collection('hills').list_documents()
    hillsInList = db.collection('hill_lists').document(listRef).get().to_dict()['hills']
    for doc in hillDocs:
        hill = getHillByID(doc.id)
        if doc not in hillsInList and hill: #Add criteria to include hill in list here
            addHillToList(doc.path, listRef)


def getHillByID(id: str) -> Hill:
    data = db.collection('hills').document(id).get().to_dict()
    if data:
        return Hill(id = id, **data)
    else:
        return None

   
def getHillList(listId: str) -> HillList | None:
    listDict = db.collection('hill_lists').document(listId).get().to_dict()

    if not listDict:
        return None

    name = listDict['name']
    refList = [hill.path for hill in listDict['hills']]
    
    hillList = getHills(refList)
    return HillList(id= listId, name= name, hills= hillList)


def getHills(references: list[str]) -> list[Hill]:
    hillList = []
    hillDocs = db.get_all([db.document(ref) for ref in references])
    for hillDoc in hillDocs:
        hillData = hillDoc.to_dict()
        hillList.append(Hill(id=hillDoc.id, **hillData))
    return hillList


def deleteHillsField(fieldName: str) -> None:
    hillDocs = db.collection('hills').stream()
    for hillDoc in hillDocs:
        doc_ref = db.collection('hills').document(hillDoc.id)
        doc_ref.update({
            fieldName: firestore.DELETE_FIELD
        })