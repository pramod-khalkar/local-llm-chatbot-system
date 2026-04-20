package com.todoapp.service;

import com.todoapp.dto.CreateTodoRequest;
import com.todoapp.dto.TodoDTO;
import com.todoapp.model.Todo;
import com.todoapp.model.TodoStatus;
import com.todoapp.repository.TodoRepository;
import com.todoapp.exception.TodoNotFoundException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class TodoService {

    private final TodoRepository todoRepository;

    public TodoDTO createTodo(CreateTodoRequest request) {
        log.info("Creating new todo with title: {}", request.getTitle());
        Todo todo = Todo.builder()
                .title(request.getTitle())
                .description(request.getDescription())
                .status(request.getStatus() != null ? request.getStatus() : TodoStatus.PENDING)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();
        Todo savedTodo = todoRepository.save(todo);
        return convertToDTO(savedTodo);
    }

    public TodoDTO getTodoById(String id) {
        log.info("Fetching todo with id: {}", id);
        Todo todo = todoRepository.findById(id)
                .orElseThrow(() -> new TodoNotFoundException("Todo not found with id: " + id));
        return convertToDTO(todo);
    }

    public List<TodoDTO> getAllTodos() {
        log.info("Fetching all todos");
        return todoRepository.findAll().stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    public List<TodoDTO> getTodosByStatus(TodoStatus status) {
        log.info("Fetching todos with status: {}", status);
        return todoRepository.findByStatus(status).stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    public List<TodoDTO> searchTodos(String keyword) {
        log.info("Searching todos with keyword: {}", keyword);
        return todoRepository.findByTitleContainingIgnoreCase(keyword).stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    public TodoDTO updateTodo(String id, CreateTodoRequest request) {
        log.info("Updating todo with id: {}", id);
        Todo todo = todoRepository.findById(id)
                .orElseThrow(() -> new TodoNotFoundException("Todo not found with id: " + id));
        
        todo.setTitle(request.getTitle());
        todo.setDescription(request.getDescription());
        todo.setStatus(request.getStatus());
        todo.setUpdatedAt(LocalDateTime.now());
        
        Todo updatedTodo = todoRepository.save(todo);
        return convertToDTO(updatedTodo);
    }

    public void deleteTodo(String id) {
        log.info("Deleting todo with id: {}", id);
        if (!todoRepository.existsById(id)) {
            throw new TodoNotFoundException("Todo not found with id: " + id);
        }
        todoRepository.deleteById(id);
    }

    private TodoDTO convertToDTO(Todo todo) {
        return TodoDTO.builder()
                .id(todo.getId())
                .title(todo.getTitle())
                .description(todo.getDescription())
                .status(todo.getStatus())
                .createdAt(todo.getCreatedAt())
                .updatedAt(todo.getUpdatedAt())
                .build();
    }
}
