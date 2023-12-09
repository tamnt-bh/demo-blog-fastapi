import json
import unittest
from unittest.mock import patch

import mongomock
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

from app.domain.auth.entity import TokenData
from app.infra.database.models.user import UserModel
from app.infra.security.security_service import get_password_hash
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

    def test_create_user(self):
        with patch("app.infra.security.security_service.verify_token") as mock_token:
            mock_token.return_value = TokenData(email=self.user.email)
            data = {'payload': json.dumps(
                {"email": "test1@test.com", "role": "user", "fullname": "John Doe", "password": "12345678"})}
            r = self.client.post(
                "/api/user",
                data=data,
                headers={
                    "Authorization": "Bearer {}".format("xxx"),
                },
            )
            assert r.status_code == 200
            user = UserModel.objects(id=r.json().get("id")).get()
            assert user.email == "test1@test.com"
            assert user.role
            assert user.fullname
            assert user.password

            data = {'payload': json.dumps(
                {"email": "test1@test.com", "role": "user", "fullname": "John Doe", "password": "12345678"})}
            r = self.client.post(
                "/api/user",
                data=data,
                headers={
                    "Authorization": "Bearer {}".format("xxx"),
                },
            )
            assert r.status_code == 500

    def test_get_all_users(self):
        with patch("app.infra.security.security_service.verify_token") as mock_token:
            mock_token.return_value = TokenData(email=self.user.email)
            r = self.client.get(
                url="/api/user",
                headers={
                    "Authorization": "Bearer {}".format("xxx"),
                },
            )
            assert r.status_code == 200
            resp = r.json()
            assert len(resp["data"]) == 2

    def test_get_me(self):
        with patch("app.infra.security.security_service.verify_token") as mock_token:
            mock_token.return_value = TokenData(email=self.user.email)
            r = self.client.get(
                url="/api/user/me",
                headers={
                    "Authorization": "Bearer {}".format("xxx"),
                },
            )
            assert r.status_code == 200
            resp = r.json()
            assert resp.get("email") == "test@test.com"

    def test_get_user_by_id(self):
        with patch("app.infra.security.security_service.verify_token") as mock_token:
            mock_token.return_value = TokenData(email=self.user.email)
            data = {'payload': json.dumps(
                {"email": "test2@test.com", "role": "user", "fullname": "John Doe", "password": "12345678"})}
            r = self.client.post(
                "/api/user",
                data=data,
                headers={
                    "Authorization": "Bearer {}".format("xxx"),
                },
            )
            assert r.status_code == 200
            user = UserModel.objects(id=r.json().get("id")).get()

            r = self.client.get(
                url="/api/user/{}".format(str(user.id)),
                headers={
                    "Authorization": "Bearer {}".format("xxx"),
                },
            )
            assert r.status_code == 200
            resp = r.json()
            assert resp.get("email") == "test2@test.com"

    def test_delete_user_by_id(self):
        with patch("app.infra.security.security_service.verify_token") as mock_token:
            mock_token.return_value = TokenData(email=self.user.email)
            data = {'payload': json.dumps(
                {"email": "test3@test.com", "role": "user", "fullname": "John Doe", "password": "12345678"})}
            r = self.client.post(
                "/api/user",
                data=data,
                headers={
                    "Authorization": "Bearer {}".format("xxx"),
                },
            )
            assert r.status_code == 200
            user = UserModel.objects(id=r.json().get("id")).get()

            r = self.client.delete(
                url="/api/user/{}".format(str(user.id)),
                headers={
                    "Authorization": "Bearer {}".format("xxx"),
                },
            )
            assert r.status_code == 200

    def test_update_me(self):
        with patch("app.infra.security.security_service.verify_token") as mock_token:
            mock_token.return_value = TokenData(email=self.user.email)
            data = {'payload': json.dumps(
                {"fullname": "Updated"})}
            r = self.client.put(
                "/api/user/me",
                data=data,
                headers={
                    "Authorization": "Bearer {}".format("xxx"),
                },
            )
            assert r.status_code == 200
            user = UserModel.objects(id=r.json().get("id")).get()
            assert user.fullname == "Updated"
