from pydantic import BaseModel, ConfigDict, Field, field_validator


def _strip_not_blank(v: str) -> str:
    v = v.strip()
    if not v:
        raise ValueError("must not be blank")
    return v


class Credentials(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=255)
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str


class TokenOut(BaseModel):
    token: str
    user: UserOut


class CategoryIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    _clean_name = field_validator("name")(_strip_not_blank)


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class ProductIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    price: float = Field(gt=0, le=10_000_000)
    stock: int = Field(ge=0, le=1_000_000)
    category_id: int

    _clean_name = field_validator("name")(_strip_not_blank)


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    price: float
    stock: int
    category_id: int
    category: CategoryOut


class ProductPage(BaseModel):
    items: list[ProductOut]
    total: int
    page: int
    page_size: int
