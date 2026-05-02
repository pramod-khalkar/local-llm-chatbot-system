package com.todoapp.config;

import com.todoapp.model.TodoStatus;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.convert.converter.Converter;
import org.springframework.format.FormatterRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Override
    public void addFormatters(FormatterRegistry registry) {
        registry.addConverter(new Converter<String, TodoStatus>() {
            @Override
            public TodoStatus convert(String source) {
                return TodoStatus.fromString(source);
            }
        });
    }
}
