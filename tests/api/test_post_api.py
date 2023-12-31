import json
import unittest
from unittest.mock import patch

import mongomock
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

from app.domain.auth.entity import TokenData
from app.infra.database.models.post import PostModel
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
        cls.user2 = UserModel(
            email="test2@test.com",
            role="admin",
            fullname="User2",
            password=get_password_hash("12345678")
        ).save()
        cls.post = PostModel(
            title="Post Default",
            description="description",
            author=cls.user2
        ).save()

    @classmethod
    def tearDownClass(cls):
        disconnect()

    def test_create_post(self):
        with patch("app.infra.security.security_service.verify_token") as mock_token:
            mock_token.return_value = TokenData(email=self.user.email)
            data = {'payload': json.dumps(
                {"title": "Test", "description": "lorem"})}
            r = self.client.post(
                "/api/post",
                data=data,
                headers={
                    "Authorization": "Bearer {}".format("xxx"),
                },
            )
            assert r.status_code == 200
            post = PostModel.objects(id=r.json().get("id")).get()
            assert post.title == "Test"
            assert post.description == "lorem"
            assert post.created_at
            assert post.updated_at
            assert post.slug

    def test_get_all_posts(self):
        r = self.client.get(
            url="/api/post",
        )
        assert r.status_code == 200
        resp = r.json()
        assert resp["pagination"]["total"] == 2

    def test_get_posts_me(self):
        r = self.client.get(
            url="/api/post/me",
            headers={
                "Authorization": "Bearer {}".format("xxx"),
            },
        )
        assert r.status_code == 401

        with patch("app.infra.security.security_service.verify_token") as mock_token:
            mock_token.return_value = TokenData(email=self.user.email)
            r = self.client.get(
                url="/api/post/me",
                headers={
                    "Authorization": "Bearer {}".format("xxx"),
                },
            )
            assert r.status_code == 200
            resp = r.json()
            assert resp["pagination"]["total"] == 1

    def test_get_post_by_id(self):
        r = self.client.get(
            url="/api/post/{}".format(str(self.post.id)),
            headers={
                "Authorization": "Bearer {}".format("xxx"),
            },
        )
        assert r.status_code == 200
        resp = r.json()
        post = PostModel.objects(id=str(self.post.id)).get()
        assert post.title == resp["title"]
        assert post.slug == resp["slug"]

    def test_update_post(self):
        with patch("app.infra.security.security_service.verify_token") as mock_token:
            mock_token.return_value = TokenData(email=self.user.email)
            data = {'payload': json.dumps(
                {"title": "Test updated", "description": "lorem"})}
            r = self.client.put(
                url="/api/post/{}".format(str(self.post.id)),
                data=data,
                headers={
                    "Authorization": "Bearer {}".format("xxx"),
                },
            )
            assert r.status_code == 200
            post = PostModel.objects(id=r.json().get("id")).get()
            assert post.title == "Test updated"


    def test_get_all_posts_by_search_title(self):
        sub_title_test = "default"
        r = self.client.get(
            url="/api/post?search={}&search_by=title".format(sub_title_test),
        )
        assert r.status_code == 200
        resp = r.json()
        assert resp["pagination"]["total"] == 1
        assert sub_title_test.lower() in resp["data"][0]["title"].lower()

    def test_get_all_posts_by_search_author(self):
        sub_author_test = "2"
        r = self.client.get(
            url="/api/post?search={}&search_by=author".format(sub_author_test),
        )
        assert r.status_code == 200
        resp = r.json()
        assert resp["pagination"]["total"] == 1
        assert sub_author_test.lower() in resp["data"][0]["author"]["fullname"].lower()

    def test_get_all_posts_sort_created_at_asce(self):
        r = self.client.get(
            url="/api/post?sort=asce&sort_by=created_at",
        )
        assert r.status_code == 200
        resp = r.json()
        assert resp["pagination"]["total"] == 2
        assert resp["data"][0]["created_at"] <= resp["data"][1]["created_at"]

    def test_get_all_posts_sort_created_at_desc(self):
        r = self.client.get(
            url="/api/post?sort_by=created_at",
        )
        assert r.status_code == 200
        resp = r.json()
        assert resp["pagination"]["total"] == 2
        assert resp["data"][0]["created_at"] >= resp["data"][1]["created_at"]