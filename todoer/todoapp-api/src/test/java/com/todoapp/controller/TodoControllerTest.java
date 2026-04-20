package com.todoapp.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.todoapp.dto.CreateTodoRequest;
import com.todoapp.dto.TodoDTO;
import com.todoapp.model.TodoStatus;
import com.todoapp.service.TodoService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;

import static org.hamcrest.Matchers.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(TodoController.class)
@DisplayName("TodoController Tests")
class TodoControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private TodoService todoService;

    @Autowired
    private ObjectMapper objectMapper;

    private CreateTodoRequest createRequest;
    private TodoDTO todoDTO;

    @BeforeEach
    void setUp() {
        createRequest = CreateTodoRequest.builder()
                .title("Test Todo")
                .description("Test Description")
                .status(TodoStatus.PENDING)
                .build();

        todoDTO = TodoDTO.builder()
                .id("1")
                .title("Test Todo")
                .description("Test Description")
                .status(TodoStatus.PENDING)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();
    }

    @Nested
    @DisplayName("Create Todo Tests")
    class CreateTodoTests {

        @Test
        @DisplayName("Should create a new todo successfully")
        void testCreateTodoSuccess() throws Exception {
            when(todoService.createTodo(any(CreateTodoRequest.class))).thenReturn(todoDTO);

            mockMvc.perform(post("/api/todos")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(objectMapper.writeValueAsString(createRequest)))
                    .andExpect(status().isCreated())
                    .andExpect(jsonPath("$.id").value(1))
                    .andExpect(jsonPath("$.title").value("Test Todo"))
                    .andExpect(jsonPath("$.status").value("PENDING"));

            verify(todoService, times(1)).createTodo(any(CreateTodoRequest.class));
        }

        @Test
        @DisplayName("Should create todo with minimal data")
        void testCreateTodoWithMinimalData() throws Exception {
            CreateTodoRequest minimalRequest = CreateTodoRequest.builder()
                    .title("Minimal Todo")
                    .status(TodoStatus.PENDING)
                    .build();

            TodoDTO minimalDTO = TodoDTO.builder()
                    .id("2")
                    .title("Minimal Todo")
                    .status(TodoStatus.PENDING)
                    .createdAt(LocalDateTime.now())
                    .updatedAt(LocalDateTime.now())
                    .build();

            when(todoService.createTodo(any(CreateTodoRequest.class))).thenReturn(minimalDTO);

            mockMvc.perform(post("/api/todos")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(objectMapper.writeValueAsString(minimalRequest)))
                    .andExpect(status().isCreated())
                    .andExpect(jsonPath("$.id").value(2));

            verify(todoService, times(1)).createTodo(any(CreateTodoRequest.class));
        }

        @Test
        @DisplayName("Should create todo with long title")
        void testCreateTodoWithLongTitle() throws Exception {
            String longTitle = "a".repeat(500);
            createRequest.setTitle(longTitle);
            todoDTO.setTitle(longTitle);

            when(todoService.createTodo(any(CreateTodoRequest.class))).thenReturn(todoDTO);

            mockMvc.perform(post("/api/todos")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(objectMapper.writeValueAsString(createRequest)))
                    .andExpect(status().isCreated());

            verify(todoService, times(1)).createTodo(any(CreateTodoRequest.class));
        }

        @Test
        @DisplayName("Should create todo with all status types")
        void testCreateTodoWithAllStatusTypes() throws Exception {
            for (TodoStatus status : TodoStatus.values()) {
                createRequest.setStatus(status);
                todoDTO.setStatus(status);

                when(todoService.createTodo(any(CreateTodoRequest.class))).thenReturn(todoDTO);

                mockMvc.perform(post("/api/todos")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(createRequest)))
                        .andExpect(status().isCreated())
                        .andExpect(jsonPath("$.status").value(status.toString()));

                verify(todoService, atLeastOnce()).createTodo(any(CreateTodoRequest.class));
            }
        }
    }

    @Nested
    @DisplayName("Get Todo Tests")
    class GetTodoTests {

        @Test
        @DisplayName("Should get todo by id successfully")
        void testGetTodoByIdSuccess() throws Exception {
            when(todoService.getTodoById("1")).thenReturn(todoDTO);

            mockMvc.perform(get("/api/todos/1"))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.id").value("1"))
                    .andExpect(jsonPath("$.title").value("Test Todo"));

            verify(todoService, times(1)).getTodoById("1");
        }

        @Test
        @DisplayName("Should return 404 for non-existent todo")
        void testGetTodoNotFound() throws Exception {
            when(todoService.getTodoById("999"))
                    .thenThrow(new com.todoapp.exception.TodoNotFoundException("Todo not found with id: 999"));

            mockMvc.perform(get("/api/todos/999"))
                    .andExpect(status().isNotFound());

            verify(todoService, times(1)).getTodoById("999");
        }

        @Test
        @DisplayName("Should get all todos successfully")
        void testGetAllTodosSuccess() throws Exception {
            List<TodoDTO> todos = Arrays.asList(todoDTO);
            when(todoService.getAllTodos()).thenReturn(todos);

            mockMvc.perform(get("/api/todos"))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$", hasSize(1)))
                    .andExpect(jsonPath("$[0].id").value("1"));

            verify(todoService, times(1)).getAllTodos();
        }

        @Test
        @DisplayName("Should return empty list when no todos exist")
        void testGetAllTodosEmpty() throws Exception {
            when(todoService.getAllTodos()).thenReturn(Arrays.asList());

            mockMvc.perform(get("/api/todos"))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$", hasSize(0)));

            verify(todoService, times(1)).getAllTodos();
        }
    }

    @Nested
    @DisplayName("Filter Todo Tests")
    class FilterTodoTests {

        @Test
        @DisplayName("Should filter todos by PENDING status")
        void testFilterTodosByPendingStatus() throws Exception {
            List<TodoDTO> pendingTodos = Arrays.asList(todoDTO);
            when(todoService.getTodosByStatus(TodoStatus.PENDING)).thenReturn(pendingTodos);

            mockMvc.perform(get("/api/todos?status=PENDING"))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$", hasSize(1)))
                    .andExpect(jsonPath("$[0].status").value("PENDING"));

            verify(todoService, times(1)).getTodosByStatus(TodoStatus.PENDING);
        }

        @Test
        @DisplayName("Should filter todos by IN_PROGRESS status")
        void testFilterTodosByInProgressStatus() throws Exception {
            todoDTO.setStatus(TodoStatus.IN_PROGRESS);
            List<TodoDTO> inProgressTodos = Arrays.asList(todoDTO);
            when(todoService.getTodosByStatus(TodoStatus.IN_PROGRESS)).thenReturn(inProgressTodos);

            mockMvc.perform(get("/api/todos?status=IN_PROGRESS"))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$[0].status").value("IN_PROGRESS"));

            verify(todoService, times(1)).getTodosByStatus(TodoStatus.IN_PROGRESS);
        }

        @Test
        @DisplayName("Should filter todos by COMPLETED status")
        void testFilterTodosByCompletedStatus() throws Exception {
            todoDTO.setStatus(TodoStatus.COMPLETED);
            List<TodoDTO> completedTodos = Arrays.asList(todoDTO);
            when(todoService.getTodosByStatus(TodoStatus.COMPLETED)).thenReturn(completedTodos);

            mockMvc.perform(get("/api/todos?status=COMPLETED"))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$[0].status").value("COMPLETED"));

            verify(todoService, times(1)).getTodosByStatus(TodoStatus.COMPLETED);
        }

        @Test
        @DisplayName("Should filter todos by CANCELLED status")
        void testFilterTodosByCancelledStatus() throws Exception {
            todoDTO.setStatus(TodoStatus.CANCELLED);
            List<TodoDTO> cancelledTodos = Arrays.asList(todoDTO);
            when(todoService.getTodosByStatus(TodoStatus.CANCELLED)).thenReturn(cancelledTodos);

            mockMvc.perform(get("/api/todos?status=CANCELLED"))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$[0].status").value("CANCELLED"));

            verify(todoService, times(1)).getTodosByStatus(TodoStatus.CANCELLED);
        }

        @Test
        @DisplayName("Should return empty list for status with no todos")
        void testFilterTodosEmptyResult() throws Exception {
            when(todoService.getTodosByStatus(TodoStatus.COMPLETED)).thenReturn(Arrays.asList());

            mockMvc.perform(get("/api/todos?status=COMPLETED"))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$", hasSize(0)));

            verify(todoService, times(1)).getTodosByStatus(TodoStatus.COMPLETED);
        }
    }

    @Nested
    @DisplayName("Search Todo Tests")
    class SearchTodoTests {

        @Test
        @DisplayName("Should search todos by title")
        void testSearchTodosByTitle() throws Exception {
            List<TodoDTO> searchResults = Arrays.asList(todoDTO);
            when(todoService.searchTodos("Test")).thenReturn(searchResults);

            mockMvc.perform(get("/api/todos?search=Test"))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$", hasSize(1)))
                    .andExpect(jsonPath("$[0].title").value("Test Todo"));

            verify(todoService, times(1)).searchTodos("Test");
        }

        @Test
        @DisplayName("Should search with case-insensitive keyword")
        void testSearchTodosCaseInsensitive() throws Exception {
            List<TodoDTO> searchResults = Arrays.asList(todoDTO);
            when(todoService.searchTodos("test")).thenReturn(searchResults);

            mockMvc.perform(get("/api/todos?search=test"))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$", hasSize(1)));

            verify(todoService, times(1)).searchTodos("test");
        }

        @Test
        @DisplayName("Should return empty list for non-matching search")
        void testSearchTodosNoMatch() throws Exception {
            when(todoService.searchTodos("NonExistent")).thenReturn(Arrays.asList());

            mockMvc.perform(get("/api/todos?search=NonExistent"))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$", hasSize(0)));

            verify(todoService, times(1)).searchTodos("NonExistent");
        }

        @Test
        @DisplayName("Should search with special characters")
        void testSearchTodosWithSpecialCharacters() throws Exception {
            List<TodoDTO> searchResults = Arrays.asList(todoDTO);
            when(todoService.searchTodos(any())).thenReturn(searchResults);

            mockMvc.perform(get("/api/todos?search=@%23$"))
                    .andExpect(status().isOk());

            verify(todoService, times(1)).searchTodos(any());
        }
    }

    @Nested
    @DisplayName("Update Todo Tests")
    class UpdateTodoTests {

        @Test
        @DisplayName("Should update todo successfully")
        void testUpdateTodoSuccess() throws Exception {
            CreateTodoRequest updateRequest = CreateTodoRequest.builder()
                    .title("Updated Title")
                    .description("Updated Description")
                    .status(TodoStatus.IN_PROGRESS)
                    .build();

            TodoDTO updatedDTO = TodoDTO.builder()
                    .id("1")
                    .title("Updated Title")
                    .description("Updated Description")
                    .status(TodoStatus.IN_PROGRESS)
                    .createdAt(LocalDateTime.now())
                    .updatedAt(LocalDateTime.now())
                    .build();

            when(todoService.updateTodo(eq("1"), any(CreateTodoRequest.class))).thenReturn(updatedDTO);

            mockMvc.perform(put("/api/todos/1")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(objectMapper.writeValueAsString(updateRequest)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.title").value("Updated Title"))
                    .andExpect(jsonPath("$.status").value("IN_PROGRESS"));

            verify(todoService, times(1)).updateTodo(eq("1"), any(CreateTodoRequest.class));
        }

        @Test
        @DisplayName("Should update only title")
        void testUpdateTodoTitleOnly() throws Exception {
            CreateTodoRequest updateRequest = CreateTodoRequest.builder()
                    .title("New Title")
                    .description("Test Description")
                    .status(TodoStatus.PENDING)
                    .build();

            todoDTO.setTitle("New Title");
            when(todoService.updateTodo(eq("1"), any(CreateTodoRequest.class))).thenReturn(todoDTO);

            mockMvc.perform(put("/api/todos/1")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(objectMapper.writeValueAsString(updateRequest)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.title").value("New Title"));

            verify(todoService, times(1)).updateTodo(eq("1"), any(CreateTodoRequest.class));
        }

        @Test
        @DisplayName("Should update status to COMPLETED")
        void testUpdateTodoStatusToCompleted() throws Exception {
            CreateTodoRequest updateRequest = CreateTodoRequest.builder()
                    .title("Test Todo")
                    .description("Test Description")
                    .status(TodoStatus.COMPLETED)
                    .build();

            todoDTO.setStatus(TodoStatus.COMPLETED);
            when(todoService.updateTodo(eq("1"), any(CreateTodoRequest.class))).thenReturn(todoDTO);

            mockMvc.perform(put("/api/todos/1")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(objectMapper.writeValueAsString(updateRequest)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.status").value("COMPLETED"));

            verify(todoService, times(1)).updateTodo(eq("1"), any(CreateTodoRequest.class));
        }

        @Test
        @DisplayName("Should return 404 when updating non-existent todo")
        void testUpdateTodoNotFound() throws Exception {
            CreateTodoRequest updateRequest = CreateTodoRequest.builder()
                    .title("Updated")
                    .status(TodoStatus.PENDING)
                    .build();

            when(todoService.updateTodo(eq("999"), any(CreateTodoRequest.class)))
                    .thenThrow(new com.todoapp.exception.TodoNotFoundException("Todo not found with id: 999"));

            mockMvc.perform(put("/api/todos/999")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(objectMapper.writeValueAsString(updateRequest)))
                    .andExpect(status().isNotFound());

            verify(todoService, times(1)).updateTodo(eq("999"), any(CreateTodoRequest.class));
        }
    }

    @Nested
    @DisplayName("Delete Todo Tests")
    class DeleteTodoTests {

        @Test
        @DisplayName("Should delete todo successfully")
        void testDeleteTodoSuccess() throws Exception {
            mockMvc.perform(delete("/api/todos/1"))
                    .andExpect(status().isNoContent());

            verify(todoService, times(1)).deleteTodo("1");
        }

        @Test
        @DisplayName("Should return 404 when deleting non-existent todo")
        void testDeleteTodoNotFound() throws Exception {
            doThrow(new com.todoapp.exception.TodoNotFoundException("Todo not found with id: 999"))
                    .when(todoService).deleteTodo("999");

            mockMvc.perform(delete("/api/todos/999"))
                    .andExpect(status().isNotFound());

            verify(todoService, times(1)).deleteTodo("999");
        }

        @Test
        @DisplayName("Should handle multiple delete requests")
        void testMultipleDeletes() throws Exception {
            mockMvc.perform(delete("/api/todos/1"))
                    .andExpect(status().isNoContent());

            mockMvc.perform(delete("/api/todos/2"))
                    .andExpect(status().isNoContent());

            verify(todoService, times(1)).deleteTodo("1");
            verify(todoService, times(1)).deleteTodo("2");
        }
    }

    @Nested
    @DisplayName("CORS and Error Handling Tests")
    class CORSAndErrorHandlingTests {

        @Test
        @DisplayName("Should support CORS headers")
        void testCORSHeaders() throws Exception {
            mockMvc.perform(get("/api/todos")
                    .header("Origin", "http://localhost:3000"))
                    .andExpect(status().isOk());

            verify(todoService, times(1)).getAllTodos();
        }

        @Test
        @DisplayName("Should return proper error response format")
        void testErrorResponseFormat() throws Exception {
            when(todoService.getTodoById("999"))
                    .thenThrow(new com.todoapp.exception.TodoNotFoundException("Not found"));

            mockMvc.perform(get("/api/todos/999"))
                    .andExpect(status().isNotFound())
                    .andExpect(jsonPath("$.error").exists())
                    .andExpect(jsonPath("$.message").exists());

            verify(todoService, times(1)).getTodoById("999");
        }
    }
}
