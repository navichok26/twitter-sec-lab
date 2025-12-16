from datetime import UTC, datetime

from flask_login import UserMixin

from app import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    posts_authored = db.relationship(
        "Post", backref="author", lazy=True, foreign_keys="Post.author_id"
    )
    posts_owned = db.relationship(
        "Post", backref="owner", lazy=True, foreign_keys="Post.owner_id"
    )
    groups_owned = db.relationship("Group", backref="owner", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        from app import bcrypt

        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        from app import bcrypt

        return bcrypt.check_password_hash(self.password_hash, password)


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    posts = db.relationship(
        "Post", backref="group_ref", lazy=True, cascade="all, delete-orphan"
    )


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"), nullable=False)

    def __repr__(self):
        return f"<Post {self.title}>"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
