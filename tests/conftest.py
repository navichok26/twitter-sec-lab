from collections.abc import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app, db
from app.models import Group, Post, User


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def user(app: Flask) -> User:
    u = User(username="user", email="user@example.com", role="user")
    u.set_password("password")
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def group_admin(app: Flask) -> User:
    u = User(
        username="group_admin", email="group-admin@example.com", role="group_admin"
    )
    u.set_password("password")
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def main_admin(app: Flask) -> User:
    u = User(username="main_admin", email="main-admin@example.com", role="main_admin")
    u.set_password("password")
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def group(app: Flask, group_admin: User) -> Group:
    g = Group(name="Default Group", description="Test group", owner_id=group_admin.id)
    db.session.add(g)
    db.session.commit()
    return g


@pytest.fixture
def post(app: Flask, user: User, group: Group) -> Post:
    p = Post(
        title="Initial Post",
        content="Content",
        author_id=user.id,
        owner_id=user.id,
        group_id=group.id,
    )
    db.session.add(p)
    db.session.commit()
    return p
