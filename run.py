from app import create_app, db
from app.models import User, Group, Post

app = create_app()

def init_db():
    """Инициализация базы данных тестовыми данными"""
    with app.app_context():
        # Создаем таблицы
        db.create_all()
        
        # Проверяем, нужно ли создавать тестовые данные
        if not User.query.first():
            print("Creating test data...")
            
            # Создаем тестовых пользователей
            main_admin = User(username='admin', email='admin@example.com', role='main_admin')
            main_admin.set_password('admin123')
            db.session.add(main_admin)
            
            group_admin1 = User(username='code_master', email='code@example.com', role='group_admin')
            group_admin1.set_password('admin123')
            db.session.add(group_admin1)
            
            group_admin2 = User(username='history_geek', email='history@example.com', role='group_admin')
            group_admin2.set_password('admin123')
            db.session.add(group_admin2)
            
            user1 = User(username='alice', email='alice@example.com', role='user')
            user1.set_password('user123')
            db.session.add(user1)
            
            user2 = User(username='bob', email='bob@example.com', role='user')
            user2.set_password('user123')
            db.session.add(user2)
            
            db.session.commit()
            
            # Создаем группы
            groups = [
                Group(name='Programming', description='All about programming languages and frameworks', owner_id=group_admin1.id),
                Group(name='History', description='Historical events and discussions', owner_id=group_admin2.id),
                Group(name='Science', description='Scientific discoveries and theories', owner_id=main_admin.id),
                Group(name='Art', description='Art, music, and creative expressions', owner_id=group_admin1.id),
            ]
            
            for group in groups:
                db.session.add(group)
            
            db.session.commit()
            
            print("Database initialized with test data!")
            print("Users created:")
            print("- Main Admin: admin / admin123")
            print("- Group Admin 1: code_master / admin123")
            print("- Group Admin 2: history_geek / admin123")
            print("- User 1: alice / user123")
            print("- User 2: bob / user123")
        else:
            print("Database already initialized.")

if __name__ == '__main__':
    # Инициализируем базу данных перед запуском
    init_db()
    
    # Запускаем приложение
    app.run(debug=True)