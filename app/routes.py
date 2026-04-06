from flask import Blueprint, request, jsonify, current_app
from .models import db, User
import redis
import json
from functools import wraps

bp = Blueprint('api', __name__, url_prefix='/api')

def get_redis():
    return redis.Redis.from_url(current_app.config['REDIS_URL'])

#декоратор для кэширования, сохраняет результаты гет-запросов
#для экономии ресурсов и усорения ответов 
def cache_redis(timeout=300):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            redis_client = get_redis()
            
            cache_key = f"cache:{request.path}"
            
            cached_data = redis_client.get(cache_key)
            if cached_data:
                return jsonify(json.loads(cached_data))
            
            result = f(*args, **kwargs)
            
            if isinstance(result, tuple):
                response_data = result[0].json
            else:
                response_data = result.json
                
            redis_client.setex(cache_key, timeout, json.dumps(response_data))
            
            return result
        return decorated_function
    return decorator

@bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'API работает'})

@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Нет данных'}), 400

    if not data.get('name'):
        return jsonify({'error': 'Имя пользователя обязательно'}), 400

    if not data.get('email'):
        return jsonify({'error': 'Email обязателен'}), 400

    existing_user = User.query.filter_by(email=data['email']).first()

    if existing_user:
        return jsonify({'error': 'Пользователь уже существует'}), 400

    user = User(
        name=data['name'],
        email=data['email']
    )

    db.session.add(user)
    db.session.commit()

    redis_client = get_redis()
    redis_client.delete("cache:/api/users")

    return jsonify(user.to_dict()), 201

@bp.route('/users', methods=['GET'])
@cache_redis(timeout=60)
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@bp.route('/users/<int:user_id>', methods=['GET'])
@cache_redis(timeout=120)
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Пользователь не найден'}), 404
    return jsonify(user.to_dict())

@bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Пользователь не найден'}), 404
    
    data = request.get_json()
    
    if data.get('name'):
        user.name = data['name']
    if data.get('email'):
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'error': 'Email уже используется'}), 400
        user.email = data['email']
    
    db.session.commit()
    
    redis_client = get_redis()
    redis_client.delete("cache:/api/users")
    redis_client.delete(f"cache:/api/users/{user_id}")
    
    return jsonify(user.to_dict())

@bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Пользователь не найден'}), 404
    
    db.session.delete(user)
    db.session.commit()
    
    redis_client = get_redis()
    redis_client.delete("cache:/api/users")
    redis_client.delete(f"cache:/api/users/{user_id}")
    
    return jsonify({'message': 'Пользователь успешно удален'})