package com.todoapp.controller;

import com.todoapp.dto.CreateTodoRequest;
import com.todoapp.dto.TodoDTO;
import com.todoapp.model.TodoStatus;
import com.todoapp.service.TodoService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/todos")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "*", maxAge = 3600)
public class TodoController {

    private final TodoService todoService;

    @PostMapping
    public ResponseEntity<TodoDTO> createTodo(@RequestBody CreateTodoRequest request) {
        log.info("POST /api/todos - Creating new todo");
        TodoDTO createdTodo = todoService.createTodo(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(createdTodo);
    }

    @GetMapping("/{id}")
    public ResponseEntity<TodoDTO> getTodo(@PathVariable String id) {
        log.info("GET /api/todos/{} - Fetching todo", id);
        TodoDTO todo = todoService.getTodoById(id);
        return ResponseEntity.ok(todo);
    }

    @GetMapping
    public ResponseEntity<List<TodoDTO>> getAllTodos(
            @RequestParam(required = false) TodoStatus status,
            @RequestParam(required = false) String search) {
        log.info("GET /api/todos - Fetching todos (status: {}, search: {})", status, search);
        
        List<TodoDTO> todos;
        if (status != null) {
            todos = todoService.getTodosByStatus(status);
        } else if (search != null && !search.isEmpty()) {
            todos = todoService.searchTodos(search);
        } else {
            todos = todoService.getAllTodos();
        }
        
        return ResponseEntity.ok(todos);
    }

    @PutMapping("/{id}")
    public ResponseEntity<TodoDTO> updateTodo(
            @PathVariable String id,
            @RequestBody CreateTodoRequest request) {
        log.info("PUT /api/todos/{} - Updating todo", id);
        TodoDTO updatedTodo = todoService.updateTodo(id, request);
        return ResponseEntity.ok(updatedTodo);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteTodo(@PathVariable String id) {
        log.info("DELETE /api/todos/{} - Deleting todo", id);
        todoService.deleteTodo(id);
        return ResponseEntity.noContent().build();
    }
}
