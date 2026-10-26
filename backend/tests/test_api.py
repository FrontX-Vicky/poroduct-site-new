def product(category_id, **overrides):
    return {"name": "Laptop", "description": "Fast", "price": 999.0, "stock": 5,
            "category_id": category_id, **overrides}


def test_1_register_login_and_session(client):
    res = client.post("/api/auth/register", json={"email": "a@b.com", "password": "secret123"})
    assert res.status_code == 201
    assert client.post("/api/auth/register", json={"email": "a@b.com", "password": "secret123"}).status_code == 409
    assert client.post("/api/auth/login", json={"email": "a@b.com", "password": "wrongpass"}).status_code == 401

    token = client.post("/api/auth/login", json={"email": "a@b.com", "password": "secret123"}).json()["token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200 and me.json()["email"] == "a@b.com"


def test_2_writes_blocked_without_valid_session(client, auth, category):
    # no token / bogus token
    assert client.post("/api/products", json=product(category["id"])).status_code == 401
    assert client.post("/api/categories", json={"name": "X"},
                       headers={"Authorization": "Bearer fake"}).status_code == 401

    # after logout the same token must stop working
    assert client.post("/api/auth/logout", headers=auth).status_code == 204
    assert client.post("/api/products", json=product(category["id"]), headers=auth).status_code == 401
    assert client.put("/api/products/1", json=product(category["id"]), headers=auth).status_code == 401


def test_3_server_side_validation(client, auth, category):
    cid = category["id"]
    bad_payloads = [
        product(cid, name="   "),
        product(cid, price=0),
        product(cid, price=-5),
        product(cid, stock=-1),
        product(999),  # category does not exist
    ]
    for payload in bad_payloads:
        assert client.post("/api/products", json=payload, headers=auth).status_code == 422, payload

    assert client.post("/api/categories", json={"name": ""}, headers=auth).status_code == 422
    assert client.post("/api/categories", json={"name": "books"}, headers=auth).status_code == 409
    assert client.post("/api/auth/register", json={"email": "bad", "password": "secret123"}).status_code == 422
    assert client.post("/api/auth/register", json={"email": "c@d.com", "password": "short"}).status_code == 422


def test_4_create_and_update_product(client, auth, category):
    res = client.post("/api/products", json=product(category["id"]), headers=auth)
    assert res.status_code == 201
    pid = res.json()["id"]

    res = client.put(f"/api/products/{pid}", json=product(category["id"], name="Laptop Pro", price=1299),
                     headers=auth)
    assert res.status_code == 200
    fetched = client.get(f"/api/products/{pid}").json()
    assert fetched["name"] == "Laptop Pro" and fetched["price"] == 1299
    assert fetched["category"]["name"] == "Books"

    assert client.put("/api/products/999", json=product(category["id"]), headers=auth).status_code == 404


def test_5_listing_search_filter_pagination(client, auth, category):
    other = client.post("/api/categories", json={"name": "Toys"}, headers=auth).json()
    for i in range(12):
        client.post("/api/products", json=product(category["id"], name=f"Book {i}", price=10 + i), headers=auth)
    client.post("/api/products", json=product(other["id"], name="Robot", price=50), headers=auth)

    page1 = client.get("/api/products", params={"page": 1, "page_size": 5}).json()
    assert page1["total"] == 13 and len(page1["items"]) == 5
    page3 = client.get("/api/products", params={"page": 3, "page_size": 5}).json()
    assert len(page3["items"]) == 3

    assert client.get("/api/products", params={"search": "robot"}).json()["total"] == 1
    assert client.get("/api/products", params={"category_id": other["id"]}).json()["total"] == 1
    priced = client.get("/api/products", params={"min_price": 15, "max_price": 20}).json()
    assert priced["total"] == 6
    assert all(15 <= p["price"] <= 20 for p in priced["items"])
