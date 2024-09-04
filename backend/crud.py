from sqlalchemy.orm import Session
from datetime import datetime
from uuid6 import uuid7
from helpers import *

import hashing
import schemas, models

"""
crud.py

Operations to interact with the database
"""

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user.id


def get_users(db: Session, uid: str):
    users = db.query(models.User).all()
    print(users)
    return users


def create_user(db: Session, schema_user: schemas.UserRegister):
    hashed_pwd = hashing.hash_password(schema_user.password)

    db_user = models.User(
        name=schema_user.name, 
        surname=schema_user.surname,
        email=schema_user.email,
        hashed_password=hashed_pwd,
        image_path=schema_user.image_path
        )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return schemas.UserRegister(name=db_user.name, surname=db_user.surname, password=db_user.hashed_password, email=db_user.email, image_path=db_user.image_path)


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not hashing.verify_password(password, user.hashed_password):
        return False
    return user

def create_job(db: Session, schema_job: schemas.JobInDB, recruiter_id: int):
    recruiter_id_key = get_user_by_id(db, recruiter_id)

    db_job= models.Job(
        recruiter_id=recruiter_id_key,
        organization=schema_job.organization,
        role=schema_job.role,
        place=schema_job.place,
        type=schema_job.type,
        salary=schema_job.salary
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return schemas.JobInDB(job_id=db_job.job_id,recruiter_id=db_job.recruiter_id, organization=db_job.organization, role=db_job.role, place=db_job.place, type=db_job.type, salary=db_job.salary)
