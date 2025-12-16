from app import db
from app.models import Group, Post, User


def test_user_password_and_repr(app) -> None:
    with app.app_context():
        user = User(username="test", email="test@example.com", role="user")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        assert user.username == "test"
        assert user.email == "test@example.com"
        assert user.role == "user"
        assert user.check_password("password")
        assert not user.check_password("wrong")
        assert "test" in repr(user)


def test_group_creation_and_owner_relationship(app, group_admin: User) -> None:
    with app.app_context():
        group = Group(
            name="Test Group",
            description="Test Description",
            owner_id=group_admin.id,
        )
        db.session.add(group)
        db.session.commit()

        assert group.name == "Test Group"
        assert group.description == "Test Description"
        assert group.owner_id == group_admin.id
        assert group.owner == group_admin


def test_post_creation_and_basic_fields(app, user: User, group: Group) -> None:
    with app.app_context():
        post = Post(
            title="Test Post",
            content="Test Content",
            author_id=user.id,
            owner_id=user.id,
            group_id=group.id,
        )
        db.session.add(post)
        db.session.commit()

        assert post.title == "Test Post"
        assert post.content == "Test Content"
        assert post.author_id == user.id
        assert post.owner_id == user.id
        assert post.group_id == group.id
        assert post.author == user
        assert post.owner == user


def test_relationship_collections(app, user: User, group: Group) -> None:
    with app.app_context():
        post1 = Post(
            title="Post 1",
            content="Content 1",
            author_id=user.id,
            owner_id=user.id,
            group_id=group.id,
        )
        post2 = Post(
            title="Post 2",
            content="Content 2",
            author_id=user.id,
            owner_id=user.id,
            group_id=group.id,
        )

        db.session.add_all([post1, post2])
        db.session.commit()

        assert len(user.posts_authored) == 2
        assert len(user.posts_owned) == 2
        assert len(group.posts) == 2
        assert group.posts[0].title in {"Post 1", "Post 2"}
