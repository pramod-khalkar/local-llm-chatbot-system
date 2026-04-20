package com.todoapp.service;

import com.todoapp.dto.CreateTodoRequest;
import com.todoapp.dto.TodoDTO;
import com.todoapp.exception.TodoNotFoundException;
import com.todoapp.model.Todo;
import com.todoapp.model.TodoStatus;
import com.todoapp.repository.TodoRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@DisplayName("TodoService Tests")
class TodoServiceTest {

    @Mock
    private TodoRepository todoRepository;

    @InjectMocks
    private TodoService todoService;

    private Todo todo;
    private CreateTodoRequest createRequest;

    @BeforeEach
    void setUp() {
        todo = Todo.builder()
                .id("1")
                .title("Test Todo")
                .description("Test Description")
                .status(TodoStatus.PENDING)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        createRequest = CreateTodoRequest.builder()
                .title("Test Todo")
                .description("Test Description")
                .status(TodoStatus.PENDING)
                .build();
    }

    @Nested
    @DisplayName("Create Todo Tests")
    class CreateTodoTests {

        @Test
        @DisplayName("Should create todo with all fields")
        void testCreateTodoWithAllFields() {
            when(todoRepository.save(any(Todo.class))).thenReturn(todo);

            TodoDTO result = todoService.createTodo(createRequest);

            assertNotNull(result);
            assertEquals("Test Todo", result.getTitle());
            assertEquals("Test Description", result.getDescription());
            assertEquals(TodoStatus.PENDING, result.getStatus());
            verify(todoRepository, times(1)).save(any(Todo.class));
        }

        @Test
        @DisplayName("Should create todo with default status if not provided")
        void testCreateTodoDefaultStatus() {
            CreateTodoRequest request = CreateTodoRequest.builder()
                    .title("Test")
                    .build();
            
            todo.setStatus(TodoStatus.PENDING);
            when(todoRepository.save(any(Todo.class))).thenReturn(todo);

            TodoDTO result = todoService.createTodo(request);

            assertEquals(TodoStatus.PENDING, result.getStatus());
            verify(todoRepository, times(1)).save(any(Todo.class));
        }

        @Test
        @DisplayName("Should set timestamps on creation")
        void testCreateTodoSetsTimestamps() {
            when(todoRepository.save(any(Todo.class))).thenReturn(todo);

            TodoDTO result = todoService.createTodo(createRequest);

            assertNotNull(result.getCreatedAt());
            assertNotNull(result.getUpdatedAt());
            verify(todoRepository, times(1)).save(any(Todo.class));
        }

        @Test
        @DisplayName("Should create todo with empty description")
        void testCreateTodoEmptyDescription() {
            CreateTodoRequest request = CreateTodoRequest.builder()
                    .title("Title Only")
                    .status(TodoStatus.PENDING)
                    .build();

            todo.setTitle("Title Only");
            todo.setDescription(null);
            when(todoRepository.save(any(Todo.class))).thenReturn(todo);

            TodoDTO result = todoService.createTodo(request);

            assertEquals("Title Only", result.getTitle());
            verify(todoRepository, times(1)).save(any(Todo.class));
        }
    }

    @Nested
    @DisplayName("Get Todo Tests")
    class GetTodoTests {

        @Test
        @DisplayName("Should get todo by valid id")
        void testGetTodoByValidId() {
            when(todoRepository.findById("1")).thenReturn(Optional.of(todo));

            TodoDTO result = todoService.getTodoById("1");

            assertNotNull(result);
            assertEquals("1", result.getId());
            assertEquals("Test Todo", result.getTitle());
            verify(todoRepository, times(1)).findById("1");
        }

        @Test
        @DisplayName("Should throw exception for non-existent todo")
        void testGetTodoByInvalidId() {
            when(todoRepository.findById("999")).thenReturn(Optional.empty());

            assertThrows(TodoNotFoundException.class, () -> todoService.getTodoById("999"));
            verify(todoRepository, times(1)).findById("999");
        }

        @Test
        @DisplayName("Should get all todos")
        void testGetAllTodos() {
            List<Todo> todos = Arrays.asList(todo);
            when(todoRepository.findAll()).thenReturn(todos);

            List<TodoDTO> results = todoService.getAllTodos();

            assertEquals(1, results.size());
            assertEquals("Test Todo", results.get(0).getTitle());
            verify(todoRepository, times(1)).findAll();
        }

        @Test
        @DisplayName("Should return empty list when no todos exist")
        void testGetAllTodosEmpty() {
            when(todoRepository.findAll()).thenReturn(Arrays.asList());

            List<TodoDTO> results = todoService.getAllTodos();

            assertTrue(results.isEmpty());
            verify(todoRepository, times(1)).findAll();
        }

        @Test
        @DisplayName("Should get todos by PENDING status")
        void testGetTodosByPendingStatus() {
            List<Todo> todos = Arrays.asList(todo);
            when(todoRepository.findByStatus(TodoStatus.PENDING)).thenReturn(todos);

            List<TodoDTO> results = todoService.getTodosByStatus(TodoStatus.PENDING);

            assertEquals(1, results.size());
            assertEquals(TodoStatus.PENDING, results.get(0).getStatus());
            verify(todoRepository, times(1)).findByStatus(TodoStatus.PENDING);
        }

        @Test
        @DisplayName("Should get todos by COMPLETED status")
        void testGetTodosByCompletedStatus() {
            todo.setStatus(TodoStatus.COMPLETED);
            List<Todo> todos = Arrays.asList(todo);
            when(todoRepository.findByStatus(TodoStatus.COMPLETED)).thenReturn(todos);

            List<TodoDTO> results = todoService.getTodosByStatus(TodoStatus.COMPLETED);

            assertEquals(1, results.size());
            assertEquals(TodoStatus.COMPLETED, results.get(0).getStatus());
            verify(todoRepository, times(1)).findByStatus(TodoStatus.COMPLETED);
        }

        @Test
        @DisplayName("Should return empty list for status with no todos")
        void testGetTodosByStatusEmpty() {
            when(todoRepository.findByStatus(TodoStatus.COMPLETED)).thenReturn(Arrays.asList());

            List<TodoDTO> results = todoService.getTodosByStatus(TodoStatus.COMPLETED);

            assertTrue(results.isEmpty());
            verify(todoRepository, times(1)).findByStatus(TodoStatus.COMPLETED);
        }
    }

    @Nested
    @DisplayName("Search Todo Tests")
    class SearchTodoTests {

        @Test
        @DisplayName("Should search todos by keyword")
        void testSearchTodosByKeyword() {
            List<Todo> todos = Arrays.asList(todo);
            when(todoRepository.findByTitleContainingIgnoreCase("Test")).thenReturn(todos);

            List<TodoDTO> results = todoService.searchTodos("Test");

            assertEquals(1, results.size());
            assertTrue(results.get(0).getTitle().contains("Test"));
            verify(todoRepository, times(1)).findByTitleContainingIgnoreCase("Test");
        }

        @Test
        @DisplayName("Should search case-insensitive")
        void testSearchTodosCaseInsensitive() {
            List<Todo> todos = Arrays.asList(todo);
            when(todoRepository.findByTitleContainingIgnoreCase("test")).thenReturn(todos);

            List<TodoDTO> results = todoService.searchTodos("test");

            assertEquals(1, results.size());
            verify(todoRepository, times(1)).findByTitleContainingIgnoreCase("test");
        }

        @Test
        @DisplayName("Should return empty list for non-matching keyword")
        void testSearchTodosNoMatch() {
            when(todoRepository.findByTitleContainingIgnoreCase("NonExistent")).thenReturn(Arrays.asList());

            List<TodoDTO> results = todoService.searchTodos("NonExistent");

            assertTrue(results.isEmpty());
            verify(todoRepository, times(1)).findByTitleContainingIgnoreCase("NonExistent");
        }

        @Test
        @DisplayName("Should handle special characters in search")
        void testSearchTodosWithSpecialCharacters() {
            List<Todo> todos = Arrays.asList(todo);
            when(todoRepository.findByTitleContainingIgnoreCase("@#$")).thenReturn(todos);

            List<TodoDTO> results = todoService.searchTodos("@#$");

            assertEquals(1, results.size());
            verify(todoRepository, times(1)).findByTitleContainingIgnoreCase("@#$");
        }
    }

    @Nested
    @DisplayName("Update Todo Tests")
    class UpdateTodoTests {

        @Test
        @DisplayName("Should update todo successfully")
        void testUpdateTodoSuccess() {
            when(todoRepository.findById("1")).thenReturn(Optional.of(todo));
            when(todoRepository.save(any(Todo.class))).thenReturn(todo);

            CreateTodoRequest updateRequest = CreateTodoRequest.builder()
                    .title("Updated Title")
                    .description("Updated Description")
                    .status(TodoStatus.IN_PROGRESS)
                    .build();

            TodoDTO result = todoService.updateTodo("1", updateRequest);

            assertNotNull(result);
            verify(todoRepository, times(1)).findById("1");
            verify(todoRepository, times(1)).save(any(Todo.class));
        }

        @Test
        @DisplayName("Should throw exception when updating non-existent todo")
        void testUpdateTodoNotFound() {
            when(todoRepository.findById("999")).thenReturn(Optional.empty());

            CreateTodoRequest updateRequest = CreateTodoRequest.builder()
                    .title("Updated")
                    .status(TodoStatus.PENDING)
                    .build();

            assertThrows(TodoNotFoundException.class, () -> todoService.updateTodo("999", updateRequest));
            verify(todoRepository, times(1)).findById("999");
        }

        @Test
        @DisplayName("Should update only status")
        void testUpdateTodoStatus() {
            when(todoRepository.findById("1")).thenReturn(Optional.of(todo));
            when(todoRepository.save(any(Todo.class))).thenReturn(todo);

            CreateTodoRequest updateRequest = CreateTodoRequest.builder()
                    .title("Test Todo")
                    .description("Test Description")
                    .status(TodoStatus.COMPLETED)
                    .build();

            TodoDTO result = todoService.updateTodo("1", updateRequest);

            assertNotNull(result);
            verify(todoRepository, times(1)).save(any(Todo.class));
        }

        @Test
        @DisplayName("Should update all fields")
        void testUpdateAllFields() {
            when(todoRepository.findById("1")).thenReturn(Optional.of(todo));
            when(todoRepository.save(any(Todo.class))).thenReturn(todo);

            CreateTodoRequest updateRequest = CreateTodoRequest.builder()
                    .title("New Title")
                    .description("New Description")
                    .status(TodoStatus.IN_PROGRESS)
                    .build();

            TodoDTO result = todoService.updateTodo("1", updateRequest);

            assertNotNull(result);
            verify(todoRepository, times(1)).findById("1");
            verify(todoRepository, times(1)).save(any(Todo.class));
        }
    }

    @Nested
    @DisplayName("Delete Todo Tests")
    class DeleteTodoTests {

        @Test
        @DisplayName("Should delete todo successfully")
        void testDeleteTodoSuccess() {
            when(todoRepository.existsById("1")).thenReturn(true);

            assertDoesNotThrow(() -> todoService.deleteTodo("1"));
            verify(todoRepository, times(1)).deleteById("1");
        }

        @Test
        @DisplayName("Should throw exception when deleting non-existent todo")
        void testDeleteTodoNotFound() {
            when(todoRepository.existsById("999")).thenReturn(false);

            assertThrows(TodoNotFoundException.class, () -> todoService.deleteTodo("999"));
            verify(todoRepository, never()).deleteById("999");
        }

        @Test
        @DisplayName("Should verify deletion was called")
        void testDeleteTodoVerifiesDeletion() {
            when(todoRepository.existsById("1")).thenReturn(true);

            todoService.deleteTodo("1");

            verify(todoRepository, times(1)).deleteById("1");
        }
    }

    @Nested
    @DisplayName("Edge Case Tests")
    class EdgeCaseTests {

        @Test
        @DisplayName("Should handle todo with null description")
        void testTodoWithNullDescription() {
            Todo todoWithNullDescription = Todo.builder()
                    .id("2")
                    .title("No Description")
                    .description(null)
                    .status(TodoStatus.PENDING)
                    .createdAt(LocalDateTime.now())
                    .updatedAt(LocalDateTime.now())
                    .build();

            when(todoRepository.findById("2")).thenReturn(Optional.of(todoWithNullDescription));

            TodoDTO result = todoService.getTodoById("2");

            assertNotNull(result);
            assertNull(result.getDescription());
        }

        @Test
        @DisplayName("Should handle multiple todos with same title")
        void testMultipleTodosWithSameTitle() {
            Todo todo2 = Todo.builder()
                    .id("2")
                    .title("Test Todo")
                    .description("Different Description")
                    .status(TodoStatus.IN_PROGRESS)
                    .createdAt(LocalDateTime.now())
                    .updatedAt(LocalDateTime.now())
                    .build();

            List<Todo> todos = Arrays.asList(todo, todo2);
            when(todoRepository.findByTitleContainingIgnoreCase("Test")).thenReturn(todos);

            List<TodoDTO> results = todoService.searchTodos("Test");

            assertEquals(2, results.size());
        }

        @Test
        @DisplayName("Should handle todo status transitions")
        void testStatusTransitions() {
            TodoStatus[] statuses = {TodoStatus.PENDING, TodoStatus.IN_PROGRESS, TodoStatus.COMPLETED, TodoStatus.CANCELLED};

            for (TodoStatus status : statuses) {
                todo.setStatus(status);
                when(todoRepository.findById("1")).thenReturn(Optional.of(todo));

                TodoDTO result = todoService.getTodoById("1");

                assertEquals(status, result.getStatus());
            }
        }
    }
}
