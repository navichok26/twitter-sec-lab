import pytest
from app.models import User, Group, Post

def test_user_creation(app):
    """???? ???????? ????????????"""
    with app.app_context():
        user = User(username='test', email='test@example.com', role='user')
        user.set_password('password')
        
        assert user.username == 'test'
        assert user.email == 'test@example.com'
        assert user.role == 'user'
        assert user.check_password('password') == True
        assert user.check_password('wrong') == False

def test_group_creation(app, test_group_admin):
    """???? ???????? ??????"""
    with app.app_context():
        group = Group(
            name='Test Group',
            description='Test Description',
            owner_id=test_group_admin.id
        )
        
        assert group.name == 'Test Group'
        assert group.description == 'Test Description'
        assert group.owner_id == test_group_admin.id

def test_post_creation(app, test_user, test_group):
    """???? ???????? ?????"""
    with app.app_context():
        post = Post(
            title='Test Post',
            content='Test Content',
            author_id=test_user.id,
            owner_id=test_user.id,
            group_id=test_group.id
        )
        
        assert post.title == 'Test Post'
        assert post.content == 'Test Content'
        assert post.author_id == test_user.id
        assert post.owner_id == test_user.id
        assert post.group_id == test_group.id
        assert post.author == test_user
        assert post.owner == test_user
        assert post.group_ref == test_group

def test_relationships(app, test_user, test_group):
    """???? ????????? ????? ????????"""
    with app.app_context():
        # ??????? ????????? ??????
        post1 = Post(
            title='Post 1',
            content='Content 1',
            author_id=test_user.id,
            owner_id=test_user.id,
            group_id=test_group.id
        )
        post2 = Post(
            title='Post 2',
            content='Content 2',
            author_id=test_user.id,
            owner_id=test_user.id,
            group_id=test_group.id
        )
        
        db.session.add_all([post1, post2])
        db.session.commit()
        
        # ????????? ?????????
        assert len(test_user.posts_authored) == 2
        assert len(test_user.posts_owned) == 2
        assert len(test_group.posts) == 2
        assert test_group.posts[0].title == 'Post 1'