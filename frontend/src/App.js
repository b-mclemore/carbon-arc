import { useState, useEffect } from 'react';

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
    <div className="min-h-screen">
      <header className="bg-app-dark p-5 text-white text-center shadow-md">
        <h1 className="text-4xl font-semibold">Task Manager</h1>
      </header>

      <div className="max-w-3xl mx-auto p-5">
        {/* Stats Section */}
        <div className="bg-white p-5 rounded-lg mb-5 shadow-md">
          <h2 className="mb-4 text-app-dark text-2xl">Statistics</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex flex-col items-center p-4 bg-gray-50 rounded-md">
              <span className="text-sm text-gray-600 mb-1">Total:</span>
              <span className="text-3xl font-bold text-app-dark">{stats.total}</span>
            </div>
            <div className="flex flex-col items-center p-4 bg-gray-50 rounded-md">
              <span className="text-sm text-gray-600 mb-1">Completed:</span>
              <span className="text-3xl font-bold text-app-dark">{stats.completed}</span>
            </div>
            <div className="flex flex-col items-center p-4 bg-gray-50 rounded-md">
              <span className="text-sm text-gray-600 mb-1">Pending:</span>
              <span className="text-3xl font-bold text-app-dark">{stats.pending}</span>
            </div>
          </div>
        </div>

        {/* Add Task Form */}
        <div className="bg-white p-5 rounded-lg mb-5 shadow-md">
          <h2 className="mb-4 text-app-dark text-2xl">Add New Task</h2>
          <form onSubmit={addTask} className="flex flex-col md:flex-row gap-2.5">
            <input
              type="text"
              value={newTaskTitle}
              onChange={(e) => setNewTaskTitle(e.target.value)}
              placeholder="Enter task title..."
              className="flex-1 px-4 py-2.5 border-2 border-gray-300 rounded-md text-base focus:outline-none focus:border-app-dark"
            />
            <button type="submit" className="bg-app-dark text-white px-5 py-2.5 rounded-md text-base cursor-pointer transition-colors duration-200 hover:bg-[#1a1d23]">
              Add Task
            </button>
          </form>
        </div>

        {/* Error Message */}
        {error && <div className="bg-red-100 text-red-800 px-3 py-2.5 rounded-md mb-5 border border-red-300">{error}</div>}

        {/* Tasks List */}
        <div className="bg-white p-5 rounded-lg shadow-md">
          <h2 className="mb-4 text-app-dark text-2xl">Tasks</h2>
          {loading ? (
            <p>Loading tasks...</p>
          ) : tasks.length === 0 ? (
            <p className="text-center text-gray-600 py-10 px-5 text-lg">No tasks yet. Add one above!</p>
          ) : (
            <ul className="list-none">
              {tasks.map(task => (
                <li key={task.id} className={`flex flex-col md:flex-row justify-between items-start md:items-center p-4 border-2 border-gray-200 rounded-md mb-2.5 transition-all duration-200 hover:border-app-dark hover:shadow-md ${task.completed ? 'bg-gray-50 opacity-80' : ''}`}>
                  <div className="flex flex-col gap-1 flex-1 mb-2 md:mb-0">
                    <span className={`text-lg font-medium ${task.completed ? 'line-through text-gray-500' : 'text-app-dark'}`}>{task.title}</span>
                    <span className="text-sm text-gray-600">
                      {task.completed ? '✓ Completed' : '○ Pending'}
                    </span>
                  </div>
                  <div className="flex gap-2.5 w-full md:w-auto">
                    {!task.completed && (
                      <button
                        onClick={() => completeTask(task.id)}
                        className="flex-1 md:flex-initial bg-green-600 text-white px-4 py-2 rounded-md text-sm cursor-pointer transition-colors duration-200 hover:bg-green-700"
                      >
                        Complete
                      </button>
                    )}
                    <button
                      onClick={() => deleteTask(task.id)}
                      className="flex-1 md:flex-initial bg-red-600 text-white px-4 py-2 rounded-md text-sm cursor-pointer transition-colors duration-200 hover:bg-red-700"
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
