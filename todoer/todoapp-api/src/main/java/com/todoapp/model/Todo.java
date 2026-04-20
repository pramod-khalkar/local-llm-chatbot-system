package com.todoapp.model;

import lombok.*;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import java.time.LocalDateTime;

@Document(collection = "todos")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Todo {
    @Id
    private String id;

    private String title;

    private String description;

    private TodoStatus status;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;
}
