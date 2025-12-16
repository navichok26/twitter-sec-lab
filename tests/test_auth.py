import pytest
from flask_login import AnonymousUserMixin
from app.models import User, Group, Post
from app.auth import Policy

def test_policy_permissions(app, test_user, test_group_admin, test_main_admin, test_group):
    with app.app_context():
        # ??????? ????
        post = Post(
            title='Test Post',
            content='Content',
            author_id=test_user.id,
            owner_id=test_user.id,
            group_id=test_group.id
        )
        db.session.add(post)
        db.session.commit()
        
        # ???? 1: ??????? ????? ????? ???
        assert Policy.is_main_admin(test_main_admin) == True
        assert Policy.can_edit_post(test_main_admin, post) == True
        assert Policy.can_delete_post(test_main_admin, post) == True
        assert Policy.can_transfer_post(test_main_admin, post) == True
        assert Policy.can_manage_group(test_main_admin, test_group) == True
        assert Policy.can_view_admin_panel(test_main_admin) == True
        
        # ???? 2: ????? ?????? ????? ????????? ??????? ? ????? ??????
        assert Policy.is_group_admin(test_group_admin) == True
        assert Policy.can_edit_post(test_group_admin, post) == True
        assert Policy.can_delete_post(test_group_admin, post) == True
        assert Policy.can_manage_group(test_group_admin, test_group) == True
        assert Policy.can_view_admin_panel(test_group_admin) == True
        
        # ???? 3: ??????? ???????????? ????? ????????????? ???? ????
        assert Policy.is_user(test_user) == True
        assert Policy.can_edit_post(test_user, post) == True
        assert Policy.can_view_admin_panel(test_user) == False
        
        # ???? 4: ???????????? ?? ????? ????????????? ????? ????
        other_user = User(username='other', email='other@example.com', role='user')
        other_user.set_password('password')
        db.session.add(other_user)
        db.session.commit()
        
        assert Policy.can_edit_post(other_user, post) == False
        
        # ???? 5: ????? ?? ????? ??????, ????? ?????????
        guest = AnonymousUserMixin()
        assert Policy.is_guest(guest) == True
        assert Policy.can_edit_post(guest, post) == False
        assert Policy.can_view_posts(guest) == True

def test_post_transfer_dac(app, test_user, test_group_admin):
    with app.app_context():
        # ??????? ??????
        group = Group(name='History', description='History stuff', owner_id=test_group_admin.id)
        db.session.add(group)
        
        # ??????? ??????? ???????????? ??? ????????
        receiver = User(username='receiver', email='receiver@example.com', role='user')
        receiver.set_password('password')
        db.session.add(receiver)
        db.session.commit()
        
        # ??????? ????
        post = Post(
            title='Original Post',
            content='Content',
            author_id=test_user.id,
            owner_id=test_user.id,
            group_id=group.id
        )
        db.session.add(post)
        db.session.commit()
        
        # ?????????? ????? ????? ?????????????, receiver - ???
        assert Policy.can_edit_post(test_user, post) == True
        assert Policy.can_edit_post(receiver, post) == False
        assert Policy.can_transfer_post(test_user, post) == True
        
        # ???????? ???? receiver'?
        post.owner_id = receiver.id
        db.session.commit()
        
        # ?????? receiver ????? ?????????????, ? ????? - ???
        assert Policy.can_edit_post(test_user, post) == False
        assert Policy.can_edit_post(receiver, post) == True
        
        # ?? ????? ?????? ??? ??? ????? (??? ??? ???? ? ??? ??????)
        assert Policy.can_edit_post(test_group_admin, post) == True

def test_group_admin_only_in_own_group(app, test_group_admin):
    with app.app_context():
        # ??????? ??? ??????
        group1 = Group(name='Group1', description='First group', owner_id=test_group_admin.id)
        group2 = Group(name='Group2', description='Second group', owner_id=2)  # ????? ????????
        db.session.add_all([group1, group2])
        
        # ??????? ????? ? ????? ???????
        post1 = Post(
            title='Post in Group1',
            content='Content',
            author_id=test_group_admin.id,
            owner_id=test_group_admin.id,
            group_id=group1.id
        )
        post2 = Post(
            title='Post in Group2',
            content='Content',
            author_id=3,
            owner_id=3,
            group_id=group2.id
        )
        db.session.add_all([post1, post2])
        db.session.commit()
        
        # ????? ?????? ????? ????????? ?????? ????? ???????
        assert Policy.can_manage_group(test_group_admin, group1) == True
        assert Policy.can_manage_group(test_group_admin, group2) == False
        assert Policy.can_edit_post(test_group_admin, post1) == True
        assert Policy.can_edit_post(test_group_admin, post2) == False