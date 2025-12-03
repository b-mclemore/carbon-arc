import React, { useState, useEffect } from 'react';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function App() {
  const [tasks, setTasks] = useState([]);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [stats, setStats] = useState({ total: 0, completed: 0, pending: 0 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch tasks on component mount
  useEffect(() => {
    fetchTasks();
    fetchStats();
  }, []);

  const fetchTasks = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_URL}/tasks`);
      if (!response.ok) throw new Error('Failed to fetch tasks');
      const data = await response.json();
      setTasks(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_URL}/tasks/stats`);
      if (!response.ok) throw new Error('Failed to fetch stats');
      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error('Stats error:', err);
    }
  };

  const addTask = async (e) => {
    e.preventDefault();
    if (!newTaskTitle.trim()) return;

    setError('');
    try {
      const response = await fetch(`${API_URL}/tasks`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title: newTaskTitle }),
      });

      if (!response.ok) throw new Error('Failed to create task');

      const newTask = await response.json();
      setTasks([...tasks, newTask]);
      setNewTaskTitle('');
      fetchStats();
    } catch (err) {
      setError(err.message);
    }
  };

  const completeTask = async (taskId) => {
    setError('');
    try {
      const response = await fetch(`${API_URL}/tasks/${taskId}/complete`, {
        method: 'PUT',
      });

      if (!response.ok) throw new Error('Failed to complete task');

      const updatedTask = await response.json();
      setTasks(tasks.map(task =>
        task.id === taskId ? updatedTask : task
      ));
      fetchStats();
    } catch (err) {
      setError(err.message);
    }
  };

  const deleteTask = async (taskId) => {
    setError('');
    try {
      const response = await fetch(`${API_URL}/tasks/${taskId}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Failed to delete task');

      setTasks(tasks.filter(task => task.id !== taskId));
      fetchStats();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Task Manager</h1>
      </header>

      <div className="container">
        {/* Stats Section */}
        <div className="stats">
          <h2>Statistics</h2>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-label">Total:</span>
              <span className="stat-value">{stats.total}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Completed:</span>
              <span className="stat-value">{stats.completed}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Pending:</span>
              <span className="stat-value">{stats.pending}</span>
            </div>
          </div>
        </div>

        {/* Add Task Form */}
        <div className="add-task">
          <h2>Add New Task</h2>
          <form onSubmit={addTask}>
            <input
              type="text"
              value={newTaskTitle}
              onChange={(e) => setNewTaskTitle(e.target.value)}
              placeholder="Enter task title..."
              className="task-input"
            />
            <button type="submit" className="btn btn-add">
              Add Task
            </button>
          </form>
        </div>

        {/* Error Message */}
        {error && <div className="error-message">{error}</div>}

        {/* Tasks List */}
        <div className="tasks-section">
          <h2>Tasks</h2>
          {loading ? (
            <p>Loading tasks...</p>
          ) : tasks.length === 0 ? (
            <p className="no-tasks">No tasks yet. Add one above!</p>
          ) : (
            <ul className="task-list">
              {tasks.map(task => (
                <li key={task.id} className={`task-item ${task.completed ? 'completed' : ''}`}>
                  <div className="task-info">
                    <span className="task-title">{task.title}</span>
                    <span className="task-status">
                      {task.completed ? '✓ Completed' : '○ Pending'}
                    </span>
                  </div>
                  <div className="task-actions">
                    {!task.completed && (
                      <button
                        onClick={() => completeTask(task.id)}
                        className="btn btn-complete"
                      >
                        Complete
                      </button>
                    )}
                    <button
                      onClick={() => deleteTask(task.id)}
                      className="btn btn-delete"
                    >
                      Delete
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
