from models.user import User

def create_admin(new_admin: User, session) -> None:
    new_admin.is_superuser = True
    session.add(new_admin) 
    session.commit() 
    session.refresh(new_admin)