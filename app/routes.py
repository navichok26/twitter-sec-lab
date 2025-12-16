from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Group, Post
from app.forms import RegistrationForm, LoginForm, PostForm, EditPostForm, TransferPostForm, GroupForm
from app.auth import Policy, main_admin_required

# Используй Blueprint правильно
bp = Blueprint('main', __name__)

# ??????????? ????????? ??? ?????????? Policy ?? ??? ???????
@bp.context_processor
def inject_policy():
    return dict(policy=Policy)

# ??????? ????????
@bp.route('/')
def index():
    return render_template('index.html')

# ???????????
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, 
                   email=form.email.data,
                   role='user')  # ??? ????? ???????????? - ??????? users
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html', form=form)

# ????
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Login failed. Check email and password.', 'danger')
    
    return render_template('login.html', form=form)

# ?????
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# ?????? ??????
@bp.route('/posts')
def posts_list():
    group_id = request.args.get('group_id', type=int)
    if group_id:
        posts = Post.query.filter_by(group_id=group_id).order_by(Post.created_at.desc()).all()
        group = Group.query.get_or_404(group_id)
    else:
        posts = Post.query.order_by(Post.created_at.desc()).all()
        group = None
    
    groups = Group.query.all()
    return render_template('posts.html', posts=posts, groups=groups, current_group=group)

# ???????? ?????
@bp.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    
    if form.validate_on_submit():
        group = Group.query.get_or_404(form.group_id.data)
        
        # ???????? ????
        if not Policy.can_create_post(current_user, group):
            abort(403)
        
        post = Post(
            title=form.title.data,
            content=form.content.data,
            author_id=current_user.id,
            owner_id=current_user.id,  # ?????????? ???????? = ?????
            group_id=form.group_id.data
        )
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully!', 'success')
        return redirect(url_for('main.posts_list', group_id=group.id))
    
    return render_template('create_post.html', form=form)

# ?????????????? ?????
@bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # ???????? ???? ????? Policy
    if not Policy.can_edit_post(current_user, post):
        abort(403)
    
    form = EditPostForm()
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('main.posts_list', group_id=post.group_id))
    
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    
    return render_template('edit_post.html', form=form, post=post)

# ???????? ?????
@bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # ???????? ???? ????? Policy
    if not Policy.can_delete_post(current_user, post):
        abort(403)
    
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('main.posts_list'))

# ???????? ?????
@bp.route('/post/<int:post_id>/transfer', methods=['GET', 'POST'])
@login_required
def transfer_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # ???????? ???? ????? Policy
    if not Policy.can_transfer_post(current_user, post):
        abort(403)
    
    form = TransferPostForm()
    # ????????? ???????? ????????? ?? ??????
    form.new_owner_id.choices = [(u.id, u.username) 
                                for u in User.query.filter(User.id != post.owner_id).all()]
    
    if form.validate_on_submit():
        post.owner_id = form.new_owner_id.data
        db.session.commit()
        flash('Post transferred successfully!', 'success')
        return redirect(url_for('main.posts_list', group_id=post.group_id))
    
    return render_template('transfer_post.html', form=form, post=post)

# ????? ??????
@bp.route('/admin')
@login_required
def admin_dashboard():
    if not Policy.can_view_admin_panel(current_user):
        abort(403)
    
    if current_user.role == 'main_admin':
        groups = Group.query.all()
        users = User.query.all()
    else:  # group_admin
        groups = Group.query.filter_by(owner_id=current_user.id).all()
        users = []
    
    return render_template('admin/dashboard.html', groups=groups, users=users)

# ?????????? ???????? (?????? ??????? ?????)
@bp.route('/admin/groups', methods=['GET', 'POST'])
@login_required
@main_admin_required
def manage_groups():
    form = GroupForm()
    
    if form.validate_on_submit():
        group = Group(
            name=form.name.data,
            description=form.description.data,
            owner_id=form.owner_id.data
        )
        db.session.add(group)
        db.session.commit()
        flash('Group created successfully!', 'success')
        return redirect(url_for('main.admin_dashboard'))
    
    groups = Group.query.all()
    return render_template('admin/groups.html', form=form, groups=groups)

# ????????? ???????????? (?????? ??????? ?????)
@bp.route('/admin/users/<int:user_id>/promote/<role>')
@login_required
@main_admin_required
def promote_user(user_id, role):
    user = User.query.get_or_404(user_id)
    if role in ['user', 'group_admin', 'main_admin']:
        user.role = role
        db.session.commit()
        flash(f'User {user.username} promoted to {role}', 'success')
    return redirect(url_for('main.admin_dashboard'))