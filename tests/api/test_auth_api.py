import unittest

import mongomock
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

from app.infra.database.models.user import UserModel
from app.infra.security.security_service import get_password_hash, verify_password
from app.main import app


class TestUserApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        disconnect()
        connect("mongoenginetest", host="mongodb://localhost:1234", mongo_client_class=mongomock.MongoClient)
        cls.client = TestClient(app)
        cls.user = UserModel(
            email="test@test.com",
            role="admin",
            fullname="John Doe",
            password=get_password_hash("12345678")
        ).save()

    @classmethod
    def tearDownClass(cls):
        disconnect()

    def test_login(self):
        r = self.client.post(
            "/api/auth/login",
            json={"email": "test@test.com", "password": "12345678"},
        )
        assert r.status_code == 200

        resp = r.json()
        user = UserModel.objects(id=resp["user"].get("id")).get()
        assert user.email == "test@test.com"
        assert user.role
        assert user.fullname
        assert user.password


    def test_signup(self):
        r = self.client.post(
            "/api/auth/signup",
            json={"email": "test1@test.com", "password": "12345678", "fullname": "Test Joe"},
        )
        assert r.status_code == 200

        resp = r.json()
        user = UserModel.objects(id=resp["user"].get("id")).get()
        assert user.email == "test1@test.com"
        assert user.role == "user"
        assert user.fullname
        assert verify_password("12345678", user.password)
