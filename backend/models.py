# Data models = database tables
import datetime as dt
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from database import Base

class MilBase(Base):
    __tablename__ = "bases"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

class EquipmentType(Base):
    __tablename__ = "equipment_types"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    category = Column(String)  # vehicle / weapon / ammunition

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password_hash = Column(String)
    role = Column(String)  # admin | base_commander | logistics_officer
    base_id = Column(Integer, ForeignKey("bases.id"), nullable=True)

class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(Integer, primary_key=True)
    base_id = Column(Integer, ForeignKey("bases.id"))
    equipment_type_id = Column(Integer, ForeignKey("equipment_types.id"))
    quantity = Column(Integer)
    date = Column(Date)

class Transfer(Base):
    __tablename__ = "transfers"
    id = Column(Integer, primary_key=True)
    from_base_id = Column(Integer, ForeignKey("bases.id"))
    to_base_id = Column(Integer, ForeignKey("bases.id"))
    equipment_type_id = Column(Integer, ForeignKey("equipment_types.id"))
    quantity = Column(Integer)
    date = Column(Date)
    created_at = Column(DateTime, default=dt.datetime.utcnow)  # timestamp for history

class Assignment(Base):  # one table for both "assigned" and "expended"
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True)
    base_id = Column(Integer, ForeignKey("bases.id"))
    equipment_type_id = Column(Integer, ForeignKey("equipment_types.id"))
    personnel = Column(String)
    kind = Column(String)  # assigned | expended
    quantity = Column(Integer)
    date = Column(Date)

class AuditLog(Base):  # every transaction is recorded here
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=dt.datetime.utcnow)
    username = Column(String)
    action = Column(String)
    detail = Column(String)
