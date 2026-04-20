# BDD Feature: Todo Management
# Testing all scenarios for creating, reading, updating, and deleting todos

Feature: Todo Management Application
  As a user
  I want to manage my todos
  So that I can organize my tasks effectively

  Background:
    Given the todo application is running
    And the API is accessible at http://localhost:8080/api/todos

  # CREATE SCENARIOS
  Scenario: Create a new todo with all fields
    Given I have a todo with title "Buy Groceries" and description "Milk, eggs, bread"
    When I create the todo with status "PENDING"
    Then the todo should be created successfully
    And the response status should be 201
    And the todo should have an id
    And the todo should have created timestamp

  Scenario: Create a todo with only required fields
    Given I have a todo with title "Learn Spring Boot"
    When I create the todo with status "PENDING"
    Then the todo should be created successfully
    And the response status should be 201

  Scenario: Create todo with different status types
    Given I have a todo with title "Task"
    When I create the todo with status "<status>"
    Then the todo should have status "<status>"
    Examples:
      | status      |
      | PENDING     |
      | IN_PROGRESS |
      | COMPLETED   |
      | CANCELLED   |

  Scenario: Create multiple todos sequentially
    Given I have a todo with title "Todo 1"
    When I create the todo with status "PENDING"
    And I have another todo with title "Todo 2"
    And I create the todo with status "PENDING"
    Then I should have 2 todos created
    And both todos should have different ids

  Scenario: Create todo with empty description
    Given I have a todo with title "Task without description"
    When I create the todo without description
    Then the todo should be created successfully
    And the description should be null or empty

  # READ SCENARIOS
  Scenario: Get all todos
    Given there are 3 todos in the database
    When I request all todos
    Then I should receive 3 todos
    And the response status should be 200

  Scenario: Get a specific todo by id
    Given there is a todo with id 1 and title "Test Todo"
    When I get the todo with id 1
    Then I should receive the todo with title "Test Todo"
    And the response status should be 200

  Scenario: Get non-existent todo
    Given there is no todo with id 999
    When I get the todo with id 999
    Then the response status should be 404
    And the error message should be "Todo not found with id: 999"

  Scenario: Get todos when database is empty
    Given the database has no todos
    When I request all todos
    Then I should receive an empty list
    And the response status should be 200

  # FILTER SCENARIOS
  Scenario: Filter todos by PENDING status
    Given there are todos with different statuses
    When I filter todos by status "PENDING"
    Then I should receive only todos with status "PENDING"
    And the response status should be 200

  Scenario: Filter todos by COMPLETED status
    Given there are todos with different statuses
    When I filter todos by status "COMPLETED"
    Then I should receive only todos with status "COMPLETED"

  Scenario: Filter todos by IN_PROGRESS status
    Given there are todos with different statuses
    When I filter todos by status "IN_PROGRESS"
    Then I should receive only todos with status "IN_PROGRESS"

  Scenario: Filter todos by CANCELLED status
    Given there are todos with different statuses
    When I filter todos by status "CANCELLED"
    Then I should receive only todos with status "CANCELLED"

  Scenario: Filter todos by status with no results
    Given there are no todos with status "COMPLETED"
    When I filter todos by status "COMPLETED"
    Then I should receive an empty list
    And the response status should be 200

  # SEARCH SCENARIOS
  Scenario: Search todos by keyword
    Given there is a todo with title "Buy Groceries"
    When I search for todos with keyword "Groceries"
    Then I should receive the todo with title "Buy Groceries"
    And the response status should be 200

  Scenario: Search todos case-insensitive
    Given there is a todo with title "Buy Groceries"
    When I search for todos with keyword "groceries"
    Then I should receive the todo with title "Buy Groceries"

  Scenario: Search todos with no matching results
    Given there are todos in the database
    When I search for todos with keyword "NonExistent"
    Then I should receive an empty list
    And the response status should be 200

  Scenario: Search todos with multiple matches
    Given there are multiple todos with "Todo" in title
    When I search for todos with keyword "Todo"
    Then I should receive all todos containing "Todo"

  # UPDATE SCENARIOS
  Scenario: Update todo title
    Given there is a todo with id 1 and title "Old Title"
    When I update the todo with new title "New Title"
    Then the todo should have title "New Title"
    And the response status should be 200

  Scenario: Update todo status to COMPLETED
    Given there is a todo with id 1 and status "PENDING"
    When I update the todo status to "COMPLETED"
    Then the todo should have status "COMPLETED"
    And the updated timestamp should be newer than created timestamp

  Scenario: Update all fields of a todo
    Given there is a todo with id 1
    When I update the todo with new title "New", new description "NewDesc", and new status "IN_PROGRESS"
    Then the todo should have all new values
    And the response status should be 200

  Scenario: Update non-existent todo
    Given there is no todo with id 999
    When I try to update the todo with id 999
    Then the response status should be 404
    And the error message should be "Todo not found with id: 999"

  Scenario: Update todo status through all transitions
    Given there is a todo with id 1 and status "PENDING"
    When I update the status to "IN_PROGRESS"
    And I update the status to "COMPLETED"
    Then the todo should have status "COMPLETED"
    And the updated timestamp should reflect all changes

  # DELETE SCENARIOS
  Scenario: Delete a todo
    Given there is a todo with id 1
    When I delete the todo with id 1
    Then the response status should be 204
    And the todo should no longer exist

  Scenario: Delete non-existent todo
    Given there is no todo with id 999
    When I try to delete the todo with id 999
    Then the response status should be 404

  Scenario: Delete multiple todos sequentially
    Given there are 3 todos with ids 1, 2, 3
    When I delete the todo with id 1
    And I delete the todo with id 2
    Then there should be 1 todo remaining

  Scenario: Delete and verify it's gone
    Given there is a todo with id 1 and title "To Delete"
    When I delete the todo with id 1
    And I try to get the todo with id 1
    Then the response status should be 404

  # EDGE CASES
  Scenario: Create todo with very long title
    Given I have a todo with a long title of 500 characters
    When I create the todo
    Then the todo should be created successfully

  Scenario: Create todo with special characters
    Given I have a todo with title "!@#$%^&*()_+-=[]{}|;':,.<>?"
    When I create the todo
    Then the todo should be created successfully

  Scenario: Perform operations with invalid JSON
    When I send invalid JSON to create a todo
    Then the response status should be 400

  Scenario: Handle concurrent operations
    Given I have 5 different todos to create
    When I create all todos concurrently
    Then all 5 todos should be created successfully
    And each todo should have a unique id

  # INTEGRATION SCENARIOS
  Scenario: Complete workflow - Create, Update, Search, Delete
    Given I have a new todo with title "Complete Workflow"
    When I create the todo with status "PENDING"
    And I update the todo status to "IN_PROGRESS"
    And I search for the todo by title "Workflow"
    And I receive the todo
    And I update the status to "COMPLETED"
    And I delete the todo
    Then the todo should no longer exist

  Scenario: Bulk operations
    Given I have 10 todos to create
    When I create all 10 todos
    And I filter todos by status "PENDING"
    And I search for specific todos
    And I update multiple todos
    Then all operations should complete successfully
    And the database should be consistent

  Scenario: Data persistence
    Given I create a todo with all details
    When I retrieve the same todo
    Then all details should be exactly as created
    And timestamps should be preserved
