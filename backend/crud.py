from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import date, datetime
from helpers import *

import hashing
import schemas, models

"""
crud.py

Operations to interact with the database
"""

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, id: int):
    return db.query(models.User).filter(models.User.id == id).first()

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

    db_user_info = models.UserInfo(id=db_user.id)
    db.add(db_user_info)
    db.commit()

    return schemas.UserRegister(name=db_user.name, surname=db_user.surname, password=db_user.hashed_password, email=db_user.email, image_path=db_user.image_path)

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not hashing.verify_password(password, user.hashed_password):
        return False
    return user

def get_all_skills(db: Session):
    return db.query(models.Skill).all()

def change_mail_password(db: Session, user_id: int, new_email: str, new_password: str, old_password: str):
    old_email = get_user_by_id(db, user_id).email
    user = authenticate_user(db, old_email, old_password)
    if not user:
        raise HTTPException(status_code=400, detail="Wrong password!")
    
    if new_email is not None:
        if new_email == old_email:
            raise HTTPException(status_code=400, detail="New email can't be the same as the old one!")
        email_exists = db.query(models.User).filter(models.User.email == new_email).first()
        if email_exists:
            raise HTTPException(status_code=400, detail="Email already exists!")
        message = "Email changed!"
        user.email = new_email

    if new_password is not None:
        if new_password == old_password:
            raise HTTPException(status_code=400, detail="New password can't be the same as the old one!")
        all_passwords = db.query(models.User.hashed_password).all()
        for pswd in all_passwords:
            if hashing.verify_password(new_password, pswd[0]):
                password_exists = True
                break
            else:
                password_exists = False
        if password_exists:
            raise HTTPException(status_code=400, detail="Password already exists!")
        message = "Password changed!"
        user.hashed_password = hashing.hash_password(new_password)

    if not new_email and not new_password:
        raise HTTPException(status_code=400, detail="You must provide a new email or password to change.")

    if new_email is not None and new_password is not None:
        message = "Email and Password changed!"

    db.commit()
    return message



# Jobs 
def create_job(db: Session, job: schemas.JobBase, recruiter_id: int):
    model_skill = models.Skill
    job_skills = db.query(model_skill).filter(model_skill.skill_name.in_(job.skills.skills)).all()

    recruiter = db.query(models.User).filter(models.User.id==recruiter_id).first()
    
    db_job= models.Job(
        recruiter_id=recruiter_id,
        organization=job.organization,
        recruiter_fullname=f"{recruiter.name} {recruiter.surname}",
        role=job.role,
        place=job.place,
        type=job.type,
        salary=job.salary
    )

    db_job.skills = job_skills

    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return "OK"
 

def get_job(db: Session, job_id: int):
    job = db.query(models.Job).filter(models.Job.job_id == job_id).first()
    return job


def apply_job(db: Session, job_id: int, applier_id: int):    
    user = get_user_by_id(db, applier_id)
    job = get_job(db, job_id)

    if user in job.applicants:
        raise HTTPException(status_code=400, detail="User has already applied!")

    job.applicants.append(user)
    db.commit()

    return "OK"

def revoke_apply_job(db: Session, job_id: int, applier_id: int):
    user = get_user_by_id(db, applier_id)
    job = get_job(db, job_id)    
    
    job.applicants.remove(user)
    db.commit()

    return "OK"


def get_recommended_jobs(db: Session, user_id: int):
    # Recommendation system not yet implemented
    jobs = db.query(models.Job).filter(models.Job.recruiter_id != user_id).all()
    user = db.query(models.User).filter(models.User.id == user_id).first()

    for j in user.applications.copy():
        jobs.remove(j)

    return jobs

def get_applications(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id==user_id).first()
    return user.applications

def get_uploaded_jobs(db: Session, user_id: int):
    jobs = db.query(models.Job).filter(models.Job.recruiter_id==user_id).all()
    return jobs


# Profile
def add_work_experience(db: Session, user_id: int, schema_work: schemas.Work):
    db_work = models.Work(
        user_id= user_id,
        organization = schema_work.organization,
        role=schema_work.role,
        date_started = schema_work.date_started,
        date_ended = (None if (schema_work.date_ended == None) else schema_work.date_ended)
    )
    db.add(db_work)
    db.commit()
    return "OK"


def add_education(db: Session, user_id: int, schema_edu: schemas.Education):
    db_edu = models.Education(
        user_id= user_id,
        organization = schema_edu.organization,
        science_field = schema_edu.science_field,
        degree = (None if (schema_edu.degree == None) else schema_edu.degree),
        date_started = schema_edu.date_started,
        date_ended = (None if (schema_edu.date_ended == None) else schema_edu.date_ended)
    )

    db.add(db_edu)
    db.commit()
    return "OK"


def add_skills(db: Session, user_id: int, updated_skills: schemas.Skills):
    model_user = models.UserInfo
    model_skill = models.Skill
    
    user_info = db.query(model_user).filter(model_user.id==user_id).first()    
    new_skills = db.query(model_skill).filter(model_skill.skill_name.in_(updated_skills.skills)).all()

    user_info.skills = new_skills
    
    db.commit()
    return "OK"


def get_user_info(db: Session, user_id: int):
    """
    Fetch work, education and skills of a user
    """
    return db.query(models.UserInfo).filter(models.UserInfo.id==user_id).first()


def change_publicity(db: Session, user_id: int, information: str):
    mod = models.UserInfo

    if information == "work":
        columm = mod.work_public
    elif information == "education":
        columm = mod.education_public
    elif information == "skills":
        columm = mod.skills_public
    else:
        return "BAD"
    
    db.query(mod).filter(mod.id==user_id).update({columm: ~columm})
    db.commit()
    return "OK"
    

def get_publicity(db: Session, user_id: int):
    res = db.query(models.UserInfo).filter(models.UserInfo.id==user_id).first()
    return res



# Friend requests
def friend_request(db: Session, sender_id: int, receiver_id: int):
    model_user = models.User
    sender = db.query(model_user).filter(model_user.id==sender_id).first()
    receiver = db.query(model_user).filter(model_user.id==receiver_id).first()

    try :
        db.execute(models.user_connection_association.insert().values(
            requester_id=sender.id,
            receiver_id=receiver.id,
            state="PENDING"
        ))
        db.commit()

    except IntegrityError as e:
        raise HTTPException(detail="You have already sent a friend request to this person!", status_code=500)

    return "OK"

def get_friend_request(db: Session, receiver_id: int, sender_id: int):
    sender = db.query(models.User).filter(models.User.id==sender_id).first()
    receiver = db.query(models.User).filter(models.User.id==receiver_id).first()
    
    res = db.query(models.user_connection_association).filter(
        models.user_connection_association.c.requester_id==sender.id,
        models.user_connection_association.c.receiver_id==receiver.id
    ).first()

    return res

def handle_friend_request(db: Session, sender_id: int, receiver_id: int, accepted: bool):
    sender = db.query(models.User).filter(models.User.id==sender_id).first()
    receiver = db.query(models.User).filter(models.User.id==receiver_id).first()

    if accepted:
        db.query(models.user_connection_association).filter(
            models.user_connection_association.c.requester_id==sender.id,
            models.user_connection_association.c.receiver_id==receiver.id
        ).update({"state": "ACCEPTED"})
    else: 
        db.query(models.user_connection_association).filter(
            models.user_connection_association.c.requester_id==sender.id,
            models.user_connection_association.c.receiver_id==receiver.id
        ).delete()
    
    db.commit()
    return "OK"

# Post
def create_post(db: Session, post: schemas.Post):
    db_post = models.Post(
        user_id= post.user_id,
        input_text= post.input_text,
        media_image_url= post.image_url,
        media_video_url= post.video_url,
        media_sound_url= post.sound_url,
        date_uploaded=  datetime.now().isoformat(sep=" ", timespec="seconds")
    )
    db.add(db_post)
    db.commit()
    return "OK"

def get_posts(db: Session, user_id: int):
    model_post = models.Post

    user = db.query(models.User).filter(models.User.id==user_id).first()
    connections = user.get_connections()
    ids = [u.id for u in connections] + [user_id]

# posts of friends and the user
    users_posts = db.query(model_post). \
        filter(model_post.user_id.in_(ids)). \
        order_by(model_post.date_uploaded.desc()). \
        limit(50).all()


# posts wich friends liked
    connections_liked_posts = []
    for c in connections:
        for p in c.liked_posts:
            connections_liked_posts.append(p)



    all_posts = users_posts + connections_liked_posts + user.uploaded_posts

    has_liked = []
    for p in all_posts:
        if p in user.liked_posts:
            has_liked.append(p.post_id)

    return list(set(all_posts)), has_liked

def handle_like(db: Session, user_id: int, post_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    post = db.query(models.Post).filter(models.Post.post_id == post_id).first()

    if user in post.likers:
        post.likers.remove(user)
        message = "Post unliked!"
    else:
        post.likers.append(user)
        message = "Post liked!"

    db.commit()
    return message


def post_comment(db: Session, user_id, post_id: int, comment: schemas.Comment):
    user = db.query(models.User).filter(models.User.id==user_id).first()

    stmt = models.comment_post_association.insert().values(
        post_id=post_id,
        user_id=user_id,
        comment_text = comment.comment_text
    )

    db.execute(stmt)
    db.commit()

def convert_to_comment_schema(db: Session, post_id: int, commentors):
    com_model = models.comment_post_association
    
    # store commentors in dict for quick retrieval
    users_dict = {}
    for c in commentors:
        users_dict[c.id] = c

    # get all comments with the post_id
    all_comments = db.query(com_model).filter(com_model.c.post_id == post_id).all()
    
    # for each comment create the schema
    response_list = []
    for comment in all_comments:
        user_id = comment.user_id

        current_com  = schemas.CommentResponse(
            user_id=comment.user_id,
            user_fullname=f"{users_dict[user_id].name} {users_dict[user_id].surname}",
            image_url=users_dict[user_id].image_path,
            comment_text=comment.comment_text,
            date_commented=comment.date_commented
        )
        response_list.append(current_com)

    sorted_comments = sorted(response_list, key=lambda x: datetime.fromisoformat(str(x.date_commented)), reverse=True)
    return sorted_comments


# Only for generating data
def add_predefined_skills_to_db(db: Session, schema_skill: schemas.addSkill):
    db_skill = models.Skill(
        skill_name=schema_skill.skill_name
    )
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return schemas.addSkill(skill_name=db_skill.skill_name)

