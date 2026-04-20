package com.todoapp.repository;

import com.todoapp.model.Todo;
import com.todoapp.model.TodoStatus;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface TodoRepository extends MongoRepository<Todo, String> {
    List<Todo> findByStatus(TodoStatus status);
    List<Todo> findByTitleContainingIgnoreCase(String title);
}
