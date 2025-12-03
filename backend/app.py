from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from pydantic import ValidationError
from typing import Dict, Tuple

from models import TaskCreate, TaskResponse, StatsResponse

app = Flask(__name__)
CORS(app)

# In-memory storage
tasks = {}
next_id = 1


@app.route('/tasks', methods=['GET'])
def get_tasks() -> Tuple[Response, int]:
    """List all tasks"""
    task_list = [TaskResponse(**task).model_dump() for task in tasks.values()]
    return jsonify(task_list), 200


@app.route('/tasks', methods=['POST'])
def create_task() -> Tuple[Response, int]:
    """Create a new task"""
    global next_id

    data = request.get_json(silent=True)

    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    try:
        task_create = TaskCreate(**data)

        # Create task dict
        task = {
            'id': next_id,
            'title': task_create.title,
            'completed': False
        }

        tasks[next_id] = task
        next_id += 1

        # Return validated response
        task_response = TaskResponse(**task)
        return jsonify(task_response.model_dump()), 201

    except ValidationError as e:
        # Convert Pydantic errors to JSON-serializable format
        error_details = []
        for error in e.errors():
            error_details.append({
                'field': '.'.join(str(x) for x in error['loc']),
                'message': error['msg'],
                'type': error['type']
            })
        return jsonify({'error': 'Task validation failed', 'details': error_details}), 400


@app.route('/tasks/<int:task_id>/complete', methods=['PUT'])
def complete_task(task_id: int) -> Tuple[Response, int]:
    """Mark a task as completed"""
    if task_id not in tasks:
        return jsonify({'error': 'Task not found'}), 404

    tasks[task_id]['completed'] = True
    task_response = TaskResponse(**tasks[task_id])
    return jsonify(task_response.model_dump()), 200


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id: int) -> Tuple[Response, int]:
    """Delete a task"""
    if task_id not in tasks:
        return jsonify({'error': 'Task not found'}), 404

    deleted_task = tasks.pop(task_id)
    task_response = TaskResponse(**deleted_task)
    return jsonify(task_response.model_dump()), 200


@app.route('/tasks/stats', methods=['GET'])
def get_stats() -> Tuple[Response, int]:
    """Get task statistics"""
    total = len(tasks)
    completed = sum(1 for task in tasks.values() if task['completed'])
    pending = total - completed

    stats_response = StatsResponse(
        total=total,
        completed=completed,
        pending=pending
    )

    return jsonify(stats_response.model_dump()), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
