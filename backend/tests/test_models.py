"""
Pydantic model validation tests.
"""
import pytest
from pydantic import ValidationError
from models import TaskCreate, TaskResponse, StatsResponse


class TestTaskCreate:
    """Tests for TaskCreate model."""

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


class TestTaskResponse:
    """Tests for TaskResponse model."""

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
    """Tests for StatsResponse model."""

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

    def test_stats_missing_field(self):
        """Test that missing required field raises validation error."""
        with pytest.raises(ValidationError):
            StatsResponse(total=5, completed=2)  # Missing pending
