import pytest
from app import create_app, db
from app.models import User, Group, Post

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(username='testuser', email='test@example.com', role='user')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def test_group_admin(app):
    with app.app_context():
        admin = User(username='groupadmin', email='admin@example.com', role='group_admin')
        admin.set_password('password')
        db.session.add(admin)
        db.session.commit()
        return admin

@pytest.fixture
def test_main_admin(app):
    with app.app_context():
        admin = User(username='mainadmin', email='main@example.com', role='main_admin')
        admin.set_password('password')
        db.session.add(admin)
        db.session.commit()
        return admin

@pytest.fixture
def test_group(app, test_group_admin):
    with app.app_context():
        group = Group(name='Programming', description='Code stuff', owner_id=test_group_admin.id)
        db.session.add(group)
        db.session.commit()
        return group