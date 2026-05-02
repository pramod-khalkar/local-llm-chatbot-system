package com.todoapp.model;

import com.fasterxml.jackson.annotation.JsonCreator;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public enum TodoStatus {
    PENDING,
    IN_PROGRESS,
    COMPLETED,
    CANCELLED;

    @JsonCreator
    public static TodoStatus fromString(String value) {
        if (value == null || value.isEmpty()) {
            return null;
        }
        try {
            return TodoStatus.valueOf(value.toUpperCase());
        } catch (IllegalArgumentException e) {
            log.warn("Invalid TodoStatus value: {}", value);
            return null;
        }
    }
}
