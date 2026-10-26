from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession

from . import models, schemas
from .auth import create_session, get_current_session, get_current_user, hash_password, verify_password
from .config import CORS_ORIGINS
from .database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Product Site API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Auth ----------

@app.post("/api/auth/register", response_model=schemas.TokenOut, status_code=201)
def register(data: schemas.Credentials, db: DbSession = Depends(get_db)):
    email = data.email.lower()
    if db.scalar(select(models.User).where(models.User.email == email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    user = models.User(email=email, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    return {"token": create_session(db, user), "user": user}


@app.post("/api/auth/login", response_model=schemas.TokenOut)
def login(data: schemas.Credentials, db: DbSession = Depends(get_db)):
    user = db.scalar(select(models.User).where(models.User.email == data.email.lower()))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    return {"token": create_session(db, user), "user": user}


@app.post("/api/auth/logout", status_code=204)
def logout(session: models.Session = Depends(get_current_session), db: DbSession = Depends(get_db)):
    db.delete(session)
    db.commit()


@app.get("/api/auth/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(get_current_user)):
    return user


# ---------- Categories ----------

@app.get("/api/categories", response_model=list[schemas.CategoryOut])
def list_categories(db: DbSession = Depends(get_db)):
    return db.scalars(select(models.Category).order_by(models.Category.name)).all()


@app.post("/api/categories", response_model=schemas.CategoryOut, status_code=201)
def create_category(
    data: schemas.CategoryIn,
    db: DbSession = Depends(get_db),
    _user: models.User = Depends(get_current_user),
):
    if db.scalar(select(models.Category).where(func.lower(models.Category.name) == data.name.lower())):
        raise HTTPException(status.HTTP_409_CONFLICT, "Category already exists")
    category = models.Category(name=data.name)
    db.add(category)
    db.commit()
    return category


# ---------- Products ----------

def _check_category(db: DbSession, category_id: int):
    if db.get(models.Category, category_id) is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Category does not exist")


@app.get("/api/products", response_model=schemas.ProductPage)
def list_products(
    db: DbSession = Depends(get_db),
    search: str | None = None,
    category_id: int | None = None,
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
):
    query = select(models.Product)
    if search:
        like = f"%{search.strip()}%"
        query = query.where(models.Product.name.ilike(like) | models.Product.description.ilike(like))
    if category_id is not None:
        query = query.where(models.Product.category_id == category_id)
    if min_price is not None:
        query = query.where(models.Product.price >= min_price)
    if max_price is not None:
        query = query.where(models.Product.price <= max_price)

    total = db.scalar(select(func.count()).select_from(query.subquery()))
    items = db.scalars(
        query.order_by(models.Product.id.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@app.get("/api/products/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: DbSession = Depends(get_db)):
    product = db.get(models.Product, product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    return product


@app.post("/api/products", response_model=schemas.ProductOut, status_code=201)
def create_product(
    data: schemas.ProductIn,
    db: DbSession = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    _check_category(db, data.category_id)
    product = models.Product(**data.model_dump(), created_by=user.id)
    db.add(product)
    db.commit()
    return product


@app.put("/api/products/{product_id}", response_model=schemas.ProductOut)
def update_product(
    product_id: int,
    data: schemas.ProductIn,
    db: DbSession = Depends(get_db),
    _user: models.User = Depends(get_current_user),
):
    product = db.get(models.Product, product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    _check_category(db, data.category_id)
    for key, value in data.model_dump().items():
        setattr(product, key, value)
    db.commit()
    return product
