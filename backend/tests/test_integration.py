"""
Integration tests for complete task workflows.
"""
import pytest


class TestTaskLifecycle:
    """Test complete task lifecycle workflows."""

    def test_create_complete_delete_workflow(self, client):
        """Test the full lifecycle: create -> complete -> delete."""
        # Create a task
        create_response = client.post('/tasks', json={'title': 'Integration Test Task'})
        assert create_response.status_code == 201
        task = create_response.get_json()
        task_id = task['id']
        assert task['completed'] is False

        # Verify it appears in task list
        list_response = client.get('/tasks')
        assert len(list_response.get_json()) == 1

        # Complete the task
        complete_response = client.put(f'/tasks/{task_id}/complete')
        assert complete_response.status_code == 200
        completed_task = complete_response.get_json()
        assert completed_task['completed'] is True

        # Verify stats show 1 completed
        stats_response = client.get('/tasks/stats')
        stats = stats_response.get_json()
        assert stats['total'] == 1
        assert stats['completed'] == 1
        assert stats['pending'] == 0

        # Delete the task
        delete_response = client.delete(f'/tasks/{task_id}')
        assert delete_response.status_code == 200

        # Verify task list is empty
        final_list = client.get('/tasks').get_json()
        assert len(final_list) == 0

        # Verify stats show 0
        final_stats = client.get('/tasks/stats').get_json()
        assert final_stats['total'] == 0

    def test_multiple_tasks_workflow(self, client):
        """Test workflow with multiple tasks."""
        # Create 5 tasks
        task_ids = []
        for i in range(1, 6):
            response = client.post('/tasks', json={'title': f'Task {i}'})
            task_ids.append(response.get_json()['id'])

        # Verify all tasks exist
        tasks = client.get('/tasks').get_json()
        assert len(tasks) == 5

        # Complete tasks 1, 3, and 5
        for i in [0, 2, 4]:
            client.put(f'/tasks/{task_ids[i]}/complete')

        # Verify stats
        stats = client.get('/tasks/stats').get_json()
        assert stats['total'] == 5
        assert stats['completed'] == 3
        assert stats['pending'] == 2

        # Delete tasks 2 and 4 (both pending)
        client.delete(f'/tasks/{task_ids[1]}')
        client.delete(f'/tasks/{task_ids[3]}')

        # Verify final stats
        final_stats = client.get('/tasks/stats').get_json()
        assert final_stats['total'] == 3
        assert final_stats['completed'] == 3
        assert final_stats['pending'] == 0

    def test_stats_accuracy_throughout_operations(self, client):
        """Test that stats remain accurate through various operations."""
        # Initial stats should be all zeros
        stats = client.get('/tasks/stats').get_json()
        assert stats == {'total': 0, 'completed': 0, 'pending': 0}

        # Create first task
        task1 = client.post('/tasks', json={'title': 'Task 1'}).get_json()
        stats = client.get('/tasks/stats').get_json()
        assert stats == {'total': 1, 'completed': 0, 'pending': 1}

        # Create second task
        task2 = client.post('/tasks', json={'title': 'Task 2'}).get_json()
        stats = client.get('/tasks/stats').get_json()
        assert stats == {'total': 2, 'completed': 0, 'pending': 2}

        # Complete first task
        client.put(f'/tasks/{task1["id"]}/complete')
        stats = client.get('/tasks/stats').get_json()
        assert stats == {'total': 2, 'completed': 1, 'pending': 1}

        # Complete second task
        client.put(f'/tasks/{task2["id"]}/complete')
        stats = client.get('/tasks/stats').get_json()
        assert stats == {'total': 2, 'completed': 2, 'pending': 0}

        # Delete first task
        client.delete(f'/tasks/{task1["id"]}')
        stats = client.get('/tasks/stats').get_json()
        assert stats == {'total': 1, 'completed': 1, 'pending': 0}

        # Delete second task
        client.delete(f'/tasks/{task2["id"]}')
        stats = client.get('/tasks/stats').get_json()
        assert stats == {'total': 0, 'completed': 0, 'pending': 0}

    def test_task_id_increment(self, client):
        """Test that task IDs increment correctly."""
        # Create three tasks
        task1 = client.post('/tasks', json={'title': 'Task 1'}).get_json()
        task2 = client.post('/tasks', json={'title': 'Task 2'}).get_json()
        task3 = client.post('/tasks', json={'title': 'Task 3'}).get_json()

        # Verify IDs increment
        assert task1['id'] == 1
        assert task2['id'] == 2
        assert task3['id'] == 3

        # Delete task 2
        client.delete(f'/tasks/{task2["id"]}')

        # Create new task - should continue incrementing
        task4 = client.post('/tasks', json={'title': 'Task 4'}).get_json()
        assert task4['id'] == 4  # Should be 4, not 2

    def test_error_handling_in_workflow(self, client):
        """Test error handling doesn't break subsequent operations."""
        # Try to complete non-existent task
        response = client.put('/tasks/999/complete')
        assert response.status_code == 404

        # Create a valid task - should still work
        task = client.post('/tasks', json={'title': 'Valid Task'}).get_json()
        assert task['id'] == 1

        # Try to delete non-existent task
        response = client.delete('/tasks/999')
        assert response.status_code == 404

        # Complete the valid task - should still work
        response = client.put(f'/tasks/{task["id"]}/complete')
        assert response.status_code == 200

        # Try to create invalid task
        response = client.post('/tasks', json={'title': ''})
        assert response.status_code == 400

        # Delete the valid task - should still work
        response = client.delete(f'/tasks/{task["id"]}')
        assert response.status_code == 200

        # Final stats should be zeros
        stats = client.get('/tasks/stats').get_json()
        assert stats == {'total': 0, 'completed': 0, 'pending': 0}
