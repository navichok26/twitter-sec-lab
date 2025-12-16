from flask_login import AnonymousUserMixin

from app import db
from app.auth import Policy
from app.models import Group, Post, User


def test_main_admin_has_full_access(
    app, main_admin: User, user: User, group: Group
) -> None:
    with app.app_context():
        post = Post(
            title="Post",
            content="Content",
            author_id=user.id,
            owner_id=user.id,
            group_id=group.id,
        )
        db.session.add(post)
        db.session.commit()

        assert Policy.is_main_admin(main_admin)
        assert Policy.can_edit_post(main_admin, post)
        assert Policy.can_delete_post(main_admin, post)
        assert Policy.can_transfer_post(main_admin, post)
        assert Policy.can_manage_group(main_admin, group)
        assert Policy.can_view_admin_panel(main_admin)


def test_group_admin_access_limited_to_own_group(
    app, group_admin: User, user: User, group: Group
) -> None:
    with app.app_context():
        other_owner = User(
            username="other_owner",
            email="other-owner@example.com",
            role="group_admin",
        )
        other_owner.set_password("password")
        db.session.add(other_owner)
        db.session.commit()

        foreign_group = Group(
            name="Foreign Group",
            description="Other",
            owner_id=other_owner.id,
        )
        db.session.add(foreign_group)
        db.session.commit()

        own_post = Post(
            title="Own Group Post",
            content="X",
            author_id=user.id,
            owner_id=user.id,
            group_id=group.id,
        )
        foreign_post = Post(
            title="Foreign Group Post",
            content="Y",
            author_id=user.id,
            owner_id=user.id,
            group_id=foreign_group.id,
        )
        db.session.add_all([own_post, foreign_post])
        db.session.commit()

        assert Policy.is_group_admin(group_admin)
        assert Policy.can_manage_group(group_admin, group)
        assert not Policy.can_manage_group(group_admin, foreign_group)
        assert Policy.can_edit_post(group_admin, own_post)
        assert not Policy.can_edit_post(group_admin, foreign_post)


def test_user_can_edit_only_own_post(app, user: User, group: Group) -> None:
    with app.app_context():
        own_post = Post(
            title="Own",
            content="A",
            author_id=user.id,
            owner_id=user.id,
            group_id=group.id,
        )
        other_user = User(
            username="other",
            email="other@example.com",
            role="user",
        )
        other_user.set_password("password")
        db.session.add_all([own_post, other_user])
        db.session.commit()

        foreign_post = Post(
            title="Foreign",
            content="B",
            author_id=other_user.id,
            owner_id=other_user.id,
            group_id=group.id,
        )
        db.session.add(foreign_post)
        db.session.commit()

        assert Policy.is_user(user)
        assert Policy.can_edit_post(user, own_post)
        assert not Policy.can_edit_post(user, foreign_post)
        assert not Policy.can_view_admin_panel(user)


def test_guest_permissions(app, user: User, group: Group) -> None:
    with app.app_context():
        post = Post(
            title="Post",
            content="C",
            author_id=user.id,
            owner_id=user.id,
            group_id=group.id,
        )
        db.session.add(post)
        db.session.commit()

        guest = AnonymousUserMixin()

        assert Policy.is_guest(guest)
        assert not Policy.can_edit_post(guest, post)
        assert Policy.can_view_posts(guest)
