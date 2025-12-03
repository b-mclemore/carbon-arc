"""
Pydantic schema validation tests.
"""
import pytest
from pydantic import ValidationError
from schemas import TaskCreate, TaskResponse, StatsResponse


class TestTaskCreate:
    """Tests for TaskCreate schema."""

    def test_valid_task_create(self):
        """Test creating TaskCreate with valid data."""
        task = TaskCreate(title="Test Task")
        assert task.title == "Test Task"

    def test_title_whitespace_stripping(self):
        """Test that leading/trailing whitespace is stripped."""
        task = TaskCreate(title="  Test Task  ")
        assert task.title == "Test Task"

    def test_title_empty_string(self):
        """Test that empty string raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="")
        errors = exc_info.value.errors()
        assert any('title' in str(e) for e in errors)

    def test_title_whitespace_only(self):
        """Test that whitespace-only title raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="   ")
        errors = exc_info.value.errors()
        assert any('title' in str(e) for e in errors)

    def test_title_too_long(self):
        """Test that title exceeding max length raises validation error."""
        long_title = "a" * 201
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title=long_title)
        errors = exc_info.value.errors()
        assert any('title' in str(e) for e in errors)

    def test_title_at_max_length(self):
        """Test that title at max length is accepted."""
        max_title = "a" * 200
        task = TaskCreate(title=max_title)
        assert task.title == max_title

    def test_missing_title(self):
        """Test that missing title raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate()
        errors = exc_info.value.errors()
        assert any('title' in str(e) for e in errors)

    def test_title_min_length(self):
        """Test that single character title is accepted."""
        task = TaskCreate(title="a")
        assert task.title == "a"


class TestTaskResponse:
    """Tests for TaskResponse schema."""

    def test_valid_task_response(self):
        """Test creating TaskResponse with valid data."""
        task = TaskResponse(id=1, title="Test Task", completed=False)
        assert task.id == 1
        assert task.title == "Test Task"
        assert task.completed is False

    def test_task_response_completed(self):
        """Test TaskResponse with completed=True."""
        task = TaskResponse(id=2, title="Completed Task", completed=True)
        assert task.completed is True

    def test_task_response_model_dump(self):
        """Test model_dump returns correct dictionary."""
        task = TaskResponse(id=1, title="Test Task", completed=False)
        data = task.model_dump()
        assert data == {'id': 1, 'title': 'Test Task', 'completed': False}

    def test_task_response_from_dict(self):
        """Test creating TaskResponse from dictionary."""
        data = {'id': 1, 'title': 'Test Task', 'completed': False}
        task = TaskResponse(**data)
        assert task.id == 1
        assert task.title == 'Test Task'
        assert task.completed is False

    def test_task_response_missing_field(self):
        """Test that missing required field raises validation error."""
        with pytest.raises(ValidationError):
            TaskResponse(id=1, title="Test Task")  # Missing completed


class TestStatsResponse:
    """Tests for StatsResponse schema."""

    def test_valid_stats_response(self):
        """Test creating StatsResponse with valid data."""
        stats = StatsResponse(total=10, completed=4, pending=6)
        assert stats.total == 10
        assert stats.completed == 4
        assert stats.pending == 6

    def test_stats_all_zero(self):
        """Test StatsResponse with all zeros."""
        stats = StatsResponse(total=0, completed=0, pending=0)
        assert stats.total == 0
        assert stats.completed == 0
        assert stats.pending == 0

    def test_stats_negative_total(self):
        """Test that negative total raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            StatsResponse(total=-1, completed=0, pending=0)
        errors = exc_info.value.errors()
        assert any('total' in str(e) for e in errors)

    def test_stats_negative_completed(self):
        """Test that negative completed raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            StatsResponse(total=5, completed=-1, pending=5)
        errors = exc_info.value.errors()
        assert any('completed' in str(e) for e in errors)

    def test_stats_negative_pending(self):
        """Test that negative pending raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            StatsResponse(total=5, completed=5, pending=-1)
        errors = exc_info.value.errors()
        assert any('pending' in str(e) for e in errors)

    def test_stats_model_dump(self):
        """Test model_dump returns correct dictionary."""
        stats = StatsResponse(total=5, completed=2, pending=3)
        data = stats.model_dump()
        assert data == {'total': 5, 'completed': 2, 'pending': 3}

    def test_stats_missing_field(self):
        """Test that missing required field raises validation error."""
        with pytest.raises(ValidationError):
            StatsResponse(total=5, completed=2)  # Missing pending
