from sqlalchemy.orm import Session
from passlib.context import CryptContext
from schema import schemas
from model.models import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def serialize_sqlalchemy_obj(obj):
    # Exclude the "hashed_password" field from serialization
    exclude_fields = ['hashed_password']
    
    return {
        column.name: getattr(obj, column.name)
        for column in obj.__table__.columns
        if column.name not in exclude_fields
    }


def get_user_by_username(db: Session, username: str):
    print(username, db)
    return db.query(User).filter(User.username == username).first()

def create_user(db, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session,  ):
    users = db.query(User).all()
    serialized_users = [serialize_sqlalchemy_obj(user) for user in users]
    return serialized_users 
