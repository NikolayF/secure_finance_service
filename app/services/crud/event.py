from models.event import Event, EventUpdate
from typing import List, Optional

def get_all_events(session) -> List[Event]:
    return session.query(Event).all()

def get_event_by_id(id:int, session) -> Optional[Event]:
    event = session.get(Event, id) 
    if event:
        return event 
    return None

def update_event(id: int, new_data: EventUpdate, session) -> Event:
    event = session.get(Event, id) 
    if event:
        event_data = new_data.dict(exclude_unset=True) 
    for key, value in event_data.items():
        setattr(event, key, value) 
        
    session.add(event) 
    session.commit() 
    session.refresh(event)
    return event

def create_event(new_event: Event, session) -> None:
    session.add(new_event) 
    session.commit() 
    session.refresh(new_event)
    
def delete_all_events(session) -> None:
    session.query(Event).delete()
    session.commit()
    
def delete_events_by_id(id:int, session) -> None:
    event = session.get(Event, id)
    if event:
        session.delete(event)
        session.commit()
        return
        
    raise Exception("Event with supplied ID does not exist")