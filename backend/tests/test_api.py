"""
API endpoint tests for the Task Manager application.
"""
import pytest


class TestGetTasks:
    """Tests for GET /tasks endpoint."""

    def test_get_tasks_empty(self, client):
        """Test getting tasks when none exist."""
        response = client.get('/tasks')
        assert response.status_code == 200
        assert response.get_json() == []

    def test_get_tasks_with_data(self, client, sample_task):
        """Test getting tasks when tasks exist."""
        # Create two tasks
        client.post('/tasks', json=sample_task(title="Task 1"))
        client.post('/tasks', json=sample_task(title="Task 2"))

        response = client.get('/tasks')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        assert data[0]['title'] == "Task 1"
        assert data[1]['title'] == "Task 2"
        assert data[0]['completed'] is False


class TestCreateTask:
    """Tests for POST /tasks endpoint."""

    def test_create_task_valid(self, client):
        """Test creating a task with valid data."""
        response = client.post('/tasks', json={'title': 'New Task'})
        assert response.status_code == 201
        data = response.get_json()
        assert data['id'] == 1
        assert data['title'] == 'New Task'
        assert data['completed'] is False

    def test_create_task_with_whitespace(self, client):
        """Test creating a task with leading/trailing whitespace."""
        response = client.post('/tasks', json={'title': '  Task with spaces  '})
        assert response.status_code == 201
        data = response.get_json()
        assert data['title'] == 'Task with spaces'  # Should be stripped

    def test_create_task_missing_body(self, client):
        """Test creating a task without request body."""
        response = client.post('/tasks')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_create_task_missing_title(self, client):
        """Test creating a task without title field."""
        response = client.post('/tasks', json={})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_create_task_empty_title(self, client):
        """Test creating a task with empty title."""
        response = client.post('/tasks', json={'title': ''})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_create_task_whitespace_only_title(self, client):
        """Test creating a task with whitespace-only title."""
        response = client.post('/tasks', json={'title': '   '})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_create_task_title_too_long(self, client):
        """Test creating a task with title exceeding max length."""
        long_title = 'a' * 201
        response = client.post('/tasks', json={'title': long_title})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


class TestCompleteTask:
    """Tests for PUT /tasks/<id>/complete endpoint."""

    def test_complete_existing_task(self, client, created_task):
        """Test completing an existing task."""
        task_id = created_task['id']
        response = client.put(f'/tasks/{task_id}/complete')
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == task_id
        assert data['completed'] is True

    def test_complete_nonexistent_task(self, client):
        """Test completing a task that doesn't exist."""
        response = client.put('/tasks/999/complete')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data

    def test_complete_already_completed_task(self, client, created_task):
        """Test completing an already completed task."""
        task_id = created_task['id']
        # Complete it once
        client.put(f'/tasks/{task_id}/complete')
        # Complete it again
        response = client.put(f'/tasks/{task_id}/complete')
        assert response.status_code == 200
        data = response.get_json()
        assert data['completed'] is True

    def test_complete_task_preserves_title(self, client, sample_task):
        """Test that completing a task preserves the data."""
        task = client.post('/tasks', json=sample_task(title="Important Task")).get_json()
        task_id = task['id']

        response = client.put(f'/tasks/{task_id}/complete')
        assert response.status_code == 200
        data = response.get_json()
        assert data['title'] == "Important Task"
        assert data['completed'] is True

    def test_complete_task_returns_correct_id(self, client, sample_task):
        """Test that completing a task returns the correct task ID."""
        # Create multiple tasks
        task1 = client.post('/tasks', json=sample_task(title="Task 1")).get_json()
        task2 = client.post('/tasks', json=sample_task(title="Task 2")).get_json()
        task3 = client.post('/tasks', json=sample_task(title="Task 3")).get_json()

        # Complete task 2
        response = client.put(f'/tasks/{task2["id"]}/complete')
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == task2['id']
        assert data['title'] == "Task 2"
        assert data['completed'] is True

    def test_complete_task_reflects_in_task_list(self, client, sample_task):
        """Test that completing a task is reflected in the task list."""
        task = client.post('/tasks', json=sample_task(title="Test Task")).get_json()
        task_id = task['id']

        # Complete the task
        client.put(f'/tasks/{task_id}/complete')

        # Get task list and verify completion status
        tasks_response = client.get('/tasks')
        tasks = tasks_response.get_json()
        completed_task = next(t for t in tasks if t['id'] == task_id)
        assert completed_task['completed'] is True


class TestDeleteTask:
    """Tests for DELETE /tasks/<id> endpoint."""

    def test_delete_existing_task(self, client, created_task):
        """Test deleting an existing task."""
        task_id = created_task['id']
        response = client.delete(f'/tasks/{task_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == task_id

        # Verify task is deleted
        get_response = client.get('/tasks')
        assert get_response.get_json() == []

    def test_delete_nonexistent_task(self, client):
        """Test deleting a task that doesn't exist."""
        response = client.delete('/tasks/999')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data

    def test_delete_completed_task(self, client, created_task):
        """Test deleting a completed task."""
        task_id = created_task['id']
        # Complete the task
        client.put(f'/tasks/{task_id}/complete')
        # Delete it
        response = client.delete(f'/tasks/{task_id}')
        assert response.status_code == 200


class TestGetStats:
    """Tests for GET /tasks/stats endpoint."""

    def test_stats_empty(self, client):
        """Test stats when no tasks exist."""
        response = client.get('/tasks/stats')
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 0
        assert data['completed'] == 0
        assert data['pending'] == 0

    def test_stats_with_pending_tasks(self, client, sample_task):
        """Test stats with only pending tasks."""
        client.post('/tasks', json=sample_task(title="Task 1"))
        client.post('/tasks', json=sample_task(title="Task 2"))

        response = client.get('/tasks/stats')
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 2
        assert data['completed'] == 0
        assert data['pending'] == 2

    def test_stats_with_completed_tasks(self, client, sample_task):
        """Test stats with only completed tasks."""
        # Create and complete two tasks
        task1 = client.post('/tasks', json=sample_task(title="Task 1")).get_json()
        task2 = client.post('/tasks', json=sample_task(title="Task 2")).get_json()
        client.put(f'/tasks/{task1["id"]}/complete')
        client.put(f'/tasks/{task2["id"]}/complete')

        response = client.get('/tasks/stats')
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 2
        assert data['completed'] == 2
        assert data['pending'] == 0

    def test_stats_with_mixed_tasks(self, client, sample_task):
        """Test stats with both pending and completed tasks."""
        # Create three tasks
        task1 = client.post('/tasks', json=sample_task(title="Task 1")).get_json()
        client.post('/tasks', json=sample_task(title="Task 2"))
        task3 = client.post('/tasks', json=sample_task(title="Task 3")).get_json()

        # Complete two of them
        client.put(f'/tasks/{task1["id"]}/complete')
        client.put(f'/tasks/{task3["id"]}/complete')

        response = client.get('/tasks/stats')
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 3
        assert data['completed'] == 2
        assert data['pending'] == 1

    def test_stats_after_deletion(self, client, sample_task):
        """Test that stats update correctly after deletion."""
        # Create two tasks
        task1 = client.post('/tasks', json=sample_task(title="Task 1")).get_json()
        task2 = client.post('/tasks', json=sample_task(title="Task 2")).get_json()

        # Delete one
        client.delete(f'/tasks/{task1["id"]}')

        response = client.get('/tasks/stats')
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 1
        assert data['completed'] == 0
        assert data['pending'] == 1
