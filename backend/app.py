from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory storage
tasks = {}
next_id = 1


@app.route('/tasks', methods=['GET'])
def get_tasks():
    """List all tasks"""
    return jsonify(list(tasks.values())), 200


@app.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    global next_id

    data = request.get_json()

    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400

    task = {
        'id': next_id,
        'title': data['title'],
        'completed': False
    }

    tasks[next_id] = task
    next_id += 1

    return jsonify(task), 201


@app.route('/tasks/<int:task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    """Mark a task as completed"""
    if task_id not in tasks:
        return jsonify({'error': 'Task not found'}), 404

    tasks[task_id]['completed'] = True
    return jsonify(tasks[task_id]), 200


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    if task_id not in tasks:
        return jsonify({'error': 'Task not found'}), 404

    deleted_task = tasks.pop(task_id)
    return jsonify(deleted_task), 200


@app.route('/tasks/stats', methods=['GET'])
def get_stats():
    """Get task statistics"""
    total = len(tasks)
    completed = sum(1 for task in tasks.values() if task['completed'])
    pending = total - completed

    stats = {
        'total': total,
        'completed': completed,
        'pending': pending
    }

    return jsonify(stats), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
