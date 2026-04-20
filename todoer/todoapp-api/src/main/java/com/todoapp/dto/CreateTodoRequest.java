package com.todoapp.dto;

import com.todoapp.model.TodoStatus;
import lombok.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CreateTodoRequest {
    private String title;
    private String description;
    private TodoStatus status;
}
