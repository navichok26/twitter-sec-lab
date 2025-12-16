from app.models import Post, User


def test_guest_access(client) -> None:
    response = client.get("/")
    assert response.status_code == 200

    response = client.get("/posts")
    assert response.status_code == 200

    response = client.get("/post/create")
    assert response.status_code == 302


def test_user_can_create_post(client, app, user: User, group) -> None:
    client.post(
        "/login",
        data={"email": "user@example.com", "password": "password"},
        follow_redirects=True,
    )

    response = client.get("/post/create")
    assert response.status_code == 200

    response = client.post(
        "/post/create",
        data={"title": "Test Post", "content": "Test Content", "group_id": group.id},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Test Post" in response.data


def test_admin_panel_access(client, app, user: User, main_admin: User) -> None:
    client.post(
        "/login",
        data={"email": "user@example.com", "password": "password"},
        follow_redirects=True,
    )

    response = client.get("/admin")
    assert response.status_code == 403

    client.get("/logout", follow_redirects=True)
    client.post(
        "/login",
        data={"email": "main-admin@example.com", "password": "password"},
        follow_redirects=True,
    )

    response = client.get("/admin")
    assert response.status_code == 200


def test_post_transfer_route(client, app, user: User, group) -> None:
    client.post(
        "/login",
        data={"email": "user@example.com", "password": "password"},
        follow_redirects=True,
    )

    client.post(
        "/post/create",
        data={"title": "Post to Transfer", "content": "Content", "group_id": group.id},
        follow_redirects=True,
    )

    with app.app_context():
        post = Post.query.order_by(Post.id.desc()).first()
        assert post is not None

    response = client.get(f"/post/{post.id}/transfer")
    assert response.status_code == 200


def test_permission_denied_for_editing_foreign_post(
    client, app, group_admin: User, user: User, group
) -> None:
    client.post(
        "/login",
        data={"email": "group-admin@example.com", "password": "password"},
        follow_redirects=True,
    )

    client.post(
        "/post/create",
        data={"title": "Admin Post", "content": "Admin Content", "group_id": group.id},
        follow_redirects=True,
    )

    client.get("/logout", follow_redirects=True)
    client.post(
        "/login",
        data={"email": "user@example.com", "password": "password"},
        follow_redirects=True,
    )

    with app.app_context():
        post = Post.query.order_by(Post.id.desc()).first()
        assert post is not None

    response = client.get(f"/post/{post.id}/edit")
    assert response.status_code == 403
