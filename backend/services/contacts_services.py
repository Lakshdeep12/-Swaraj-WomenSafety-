from sqlalchemy.orm import Session
from models.contact import Contact
from schemas.contact import ContactCreate

def create_contact(db: Session, contact: ContactCreate, user_id: int) -> Contact:
    db_contact = Contact(
        user_id=user_id,
        name=contact.name,
        email=contact.email,
        phone_number=contact.phone_number,
        relation=contact.relation,
        message=contact.message
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def get_contacts_by_user(db: Session, user_id: int) -> list[Contact]:
    return db.query(Contact).filter(Contact.user_id == user_id).all()