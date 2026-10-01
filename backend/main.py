import datetime as dt, logging
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import func, or_

from database import Base, engine, get_db, SessionLocal
from models import MilBase, EquipmentType, User, Purchase, Transfer, Assignment, AuditLog
from auth import hash_pw, create_token, require

logging.basicConfig(filename="api.log", level=logging.INFO, format="%(asctime)s %(message)s")
app = FastAPI(title="Military Asset Management System")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

ALL = ("admin", "base_commander", "logistics_officer")
ADMIN_CMD = ("admin", "base_commander")

# ---------- seed demo data ----------
@app.on_event("startup")
def seed():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    if db.query(User).count() == 0:
        db.add_all([MilBase(name="Alpha"), MilBase(name="Bravo"), MilBase(name="Charlie")])
        db.add_all([EquipmentType(name="M4 Rifle", category="weapon"),
                    EquipmentType(name="Humvee", category="vehicle"),
                    EquipmentType(name="5.56mm Ammo", category="ammunition")])
        db.commit()
        db.add_all([User(username="admin", password_hash=hash_pw("admin123"), role="admin"),
                    User(username="commander", password_hash=hash_pw("cmd123"), role="base_commander", base_id=1),
                    User(username="logistics", password_hash=hash_pw("log123"), role="logistics_officer", base_id=1)])
        d = dt.date.today()
        db.add_all([Purchase(base_id=1, equipment_type_id=1, quantity=100, date=d - dt.timedelta(days=30)),
                    Purchase(base_id=2, equipment_type_id=2, quantity=20, date=d - dt.timedelta(days=20)),
                    Transfer(from_base_id=1, to_base_id=2, equipment_type_id=1, quantity=10, date=d - dt.timedelta(days=10)),
                    Assignment(base_id=1, equipment_type_id=1, personnel="Sgt. Rao", kind="assigned", quantity=5, date=d - dt.timedelta(days=5)),
                    Assignment(base_id=1, equipment_type_id=1, personnel="Sgt. Rao", kind="expended", quantity=2, date=d - dt.timedelta(days=2))])
        db.commit()
    db.close()

# ---------- helpers ----------
def audit(db, user, action, detail):
    """API logging: every write is stored in audit_logs and api.log."""
    db.add(AuditLog(username=user.username, action=action, detail=detail)); db.commit()
    logging.info(f"{user.username} | {action} | {detail}")

def scope(user, base_id):
    """Admins may see any base; everyone else is locked to their own base."""
    return base_id if user.role == "admin" else user.base_id

def out(db, rows):  # rows -> dicts with human-readable base/equipment names
    B = {b.id: b.name for b in db.query(MilBase)}
    E = {e.id: e.name for e in db.query(EquipmentType)}
    res = []
    for r in rows:
        d = {c.name: getattr(r, c.name) for c in r.__table__.columns}
        for k in [k for k in d if k.endswith("base_id")]:
            d[k.replace("_id", "_name")] = B.get(d[k])
        d["equipment_name"] = E.get(d["equipment_type_id"])
        res.append(d)
    return res

def listing(db, user, M, base_cols, base_id, eq, start, end):
    q = db.query(M)
    b = scope(user, base_id)
    if b:
        q = q.filter(or_(*[getattr(M, c) == b for c in base_cols]))
    if eq: q = q.filter(M.equipment_type_id == eq)
    if start: q = q.filter(M.date >= start)
    if end: q = q.filter(M.date <= end)
    return out(db, q.order_by(M.date.desc()).all())

def own_base_only(user, *base_ids):
    if user.role != "admin" and user.base_id not in base_ids:
        raise HTTPException(403, "You can only act on your own base")

# ---------- auth ----------
class Login(BaseModel):
    username: str
    password: str

@app.post("/api/login")
def login(body: Login, db=Depends(get_db)):
    u = db.query(User).filter(User.username == body.username).first()
    if not u or u.password_hash != hash_pw(body.password):
        raise HTTPException(401, "Wrong username or password")
    db.add(AuditLog(username=u.username, action="LOGIN", detail="")); db.commit()
    return {"token": create_token(u), "user": {"username": u.username, "role": u.role, "base_id": u.base_id}}

@app.get("/api/meta")
def meta(db=Depends(get_db), user=Depends(require(*ALL))):
    return {"bases": [{"id": b.id, "name": b.name} for b in db.query(MilBase)],
            "equipment": [{"id": e.id, "name": e.name} for e in db.query(EquipmentType)]}

# ---------- dashboard ----------
def qsum(db, M, bcol, b, eq, lo, hi, kind=None):
    q = db.query(func.coalesce(func.sum(M.quantity), 0))
    if b: q = q.filter(getattr(M, bcol) == b)
    if eq: q = q.filter(M.equipment_type_id == eq)
    if lo: q = q.filter(M.date >= lo)
    if hi: q = q.filter(M.date <= hi)
    if kind: q = q.filter(M.kind == kind)
    return q.scalar()

def flow(db, b, eq, lo, hi):
    return dict(purchases=qsum(db, Purchase, "base_id", b, eq, lo, hi),
                transfer_in=qsum(db, Transfer, "to_base_id", b, eq, lo, hi),
                transfer_out=qsum(db, Transfer, "from_base_id", b, eq, lo, hi),
                assigned=qsum(db, Assignment, "base_id", b, eq, lo, hi, "assigned"),
                expended=qsum(db, Assignment, "base_id", b, eq, lo, hi, "expended"))

def net(f): return f["purchases"] + f["transfer_in"] - f["transfer_out"]

@app.get("/api/dashboard")
def dashboard(base_id: Optional[int] = None, equipment_type_id: Optional[int] = None,
              start: Optional[dt.date] = None, end: Optional[dt.date] = None,
              db=Depends(get_db), user=Depends(require(*ADMIN_CMD))):
    b, eq = scope(user, base_id), equipment_type_id
    cur = flow(db, b, eq, start, end)
    opening = 0
    if start:  # opening = everything that happened before the start date
        prev = flow(db, b, eq, None, start - dt.timedelta(days=1))
        opening = net(prev) - prev["expended"]
    closing = opening + net(cur) - cur["expended"]
    return {"opening_balance": opening, "closing_balance": closing, "net_movement": net(cur), **cur,
            "details": {"purchases": listing(db, user, Purchase, ["base_id"], base_id, eq, start, end),
                        "transfers_in": listing(db, user, Transfer, ["to_base_id"], base_id, eq, start, end),
                        "transfers_out": listing(db, user, Transfer, ["from_base_id"], base_id, eq, start, end)}}

# ---------- purchases ----------
class PurchaseIn(BaseModel):
    base_id: int; equipment_type_id: int; quantity: int = Field(gt=0); date: dt.date

@app.get("/api/purchases")
def list_purchases(base_id: Optional[int] = None, equipment_type_id: Optional[int] = None,
                   start: Optional[dt.date] = None, end: Optional[dt.date] = None,
                   db=Depends(get_db), user=Depends(require(*ALL))):
    return listing(db, user, Purchase, ["base_id"], base_id, equipment_type_id, start, end)

@app.post("/api/purchases")
def add_purchase(body: PurchaseIn, db=Depends(get_db), user=Depends(require(*ALL))):
    own_base_only(user, body.base_id)
    db.add(Purchase(**body.model_dump())); db.commit()
    audit(db, user, "PURCHASE", str(body.model_dump()))
    return {"ok": True}

# ---------- transfers ----------
class TransferIn(BaseModel):
    from_base_id: int; to_base_id: int; equipment_type_id: int; quantity: int = Field(gt=0); date: dt.date

@app.get("/api/transfers")
def list_transfers(base_id: Optional[int] = None, equipment_type_id: Optional[int] = None,
                   start: Optional[dt.date] = None, end: Optional[dt.date] = None,
                   db=Depends(get_db), user=Depends(require(*ALL))):
    return listing(db, user, Transfer, ["from_base_id", "to_base_id"], base_id, equipment_type_id, start, end)

@app.post("/api/transfers")
def add_transfer(body: TransferIn, db=Depends(get_db), user=Depends(require(*ALL))):
    if body.from_base_id == body.to_base_id:
        raise HTTPException(400, "Source and destination base must differ")
    own_base_only(user, body.from_base_id)  # you can only send stock out of your own base
    db.add(Transfer(**body.model_dump())); db.commit()
    audit(db, user, "TRANSFER", str(body.model_dump()))
    return {"ok": True}

# ---------- assignments & expenditures ----------
class AssignIn(BaseModel):
    base_id: int; equipment_type_id: int; personnel: str; kind: str = Field(pattern="^(assigned|expended)$")
    quantity: int = Field(gt=0); date: dt.date

@app.get("/api/assignments")
def list_assignments(base_id: Optional[int] = None, equipment_type_id: Optional[int] = None,
                     start: Optional[dt.date] = None, end: Optional[dt.date] = None,
                     db=Depends(get_db), user=Depends(require(*ADMIN_CMD))):
    return listing(db, user, Assignment, ["base_id"], base_id, equipment_type_id, start, end)

@app.post("/api/assignments")
def add_assignment(body: AssignIn, db=Depends(get_db), user=Depends(require(*ADMIN_CMD))):
    own_base_only(user, body.base_id)
    db.add(Assignment(**body.model_dump())); db.commit()
    audit(db, user, body.kind.upper(), str(body.model_dump()))
    return {"ok": True}

# ---------- audit log (admin only) ----------
@app.get("/api/audit-logs")
def audit_logs(db=Depends(get_db), user=Depends(require("admin"))):
    rows = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(200).all()
    return [{"time": str(r.timestamp), "user": r.username, "action": r.action, "detail": r.detail} for r in rows]
