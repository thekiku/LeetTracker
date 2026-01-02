from flask import Flask, jsonify, send_from_directory, request, session, redirect
import requests
import os
import random
import time


app = Flask(__name__)
app.secret_key = 'leettracker123'


friends_data = {}
presence_data = {}  # Track online status
global_users = [
    "leetcode", "neetcode", "awkwardindian", "ravindraraje", "stomach_ache",
    "premium", "algo_daily", "daily_coding", "grind75", "topcoder",
    "codeforces", "atcoder", "hackerrank", "solution_1", "pattern_learner",
    "dp_master", "graph_guru", "tree_traveler", "array_addict", "string_slicer"
]


def get_leetcode_stats(username):
    try:
        url = f"https://leetcode-stats.tashif.codes/{username}"
        r = requests.get(url, timeout=5)
        data = r.json()
        return {
            'username': data.get('username', username),
            'problems': data.get('totalSolved', 0),
            'easy': data.get('easySolved', 0),
            'medium': data.get('mediumSolved', 0),
            'hard': data.get('hardSolved', 0)
        }
    except:
        return {'error': 'User not found'}


def get_current_user():
    return session.get('username')


def is_user_online(username):
    if username not in presence_data:
        return False
    last_seen = presence_data.get(username, 0)
    return (time.time() - last_seen) < 60


@app.route('/')
def home():
    user = request.args.get('user') or session.get('username')
    if user:
        session['username'] = user
        return send_from_directory('templates', 'index.html')
    return send_from_directory('templates', 'login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    if username:
        stats = get_leetcode_stats(username)
        if 'error' not in stats:
            session['username'] = username
            if username not in friends_data:
                friends_data[username] = []
            return redirect(f'/?user={username}')
    return redirect('/')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


@app.route('/stats/<username>')
def stats(username):
    return jsonify(get_leetcode_stats(username))


@app.route('/api/add_friend', methods=['POST'])
def add_friend():
    user = get_current_user()
    if not user: return jsonify({'error': 'Login required'}), 401
    data = request.json
    friend = data.get('friend_username', '').strip()
    if friend and friend not in friends_data.get(user, []):
        if user not in friends_data:
            friends_data[user] = []
        friends_data[user].append(friend)
    return jsonify({'status': 'added'})


@app.route('/api/remove_friend', methods=['POST'])
def remove_friend():
    user = get_current_user()
    if not user: return jsonify({'error': 'Login required'}), 401
    data = request.json
    friend = data.get('friend_username', '').strip()
    if user in friends_data and friend in friends_data[user]:
        friends_data[user].remove(friend)
    return jsonify({'status': 'removed'})


@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    user = get_current_user()
    if not user: return jsonify({'error': 'Login required'}), 401
    presence_data[user] = time.time()
    return jsonify({'status': 'ok'})


@app.route('/api/friends/me')
def get_friends():
    user = get_current_user()
    if not user: return jsonify({'error': 'Login required'}), 401
    friends = friends_data.get(user, [])
    return jsonify([{
        'username': f,
        'stats': get_leetcode_stats(f),
        'problems': get_leetcode_stats(f).get('problems', 0),
        'online': is_user_online(f)
    } for f in friends])


@app.route('/api/leaderboard/me')
def get_leaderboard():
    user = get_current_user()
    if not user: return jsonify({'error': 'Login required'}), 401
    friends = friends_data.get(user, [])
    lb = [{'username': f, 'total_problems': get_leetcode_stats(f).get('problems', 0)} for f in friends]
    lb.sort(key=lambda x: x['total_problems'], reverse=True)
    return jsonify({'leaderboard': lb, 'best_friend': lb[0] if lb else None})


@app.route('/api/global_users')
def get_global_users():
    random_users = random.sample(global_users, min(12, len(global_users)))
    return jsonify([{
        'username': user,
        'stats': get_leetcode_stats(user),
        'followed': False
    } for user in random_users])


if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    print("🚀 LeetTracker on http://localhost:5000")
    app.run(debug=True, port=5000)
