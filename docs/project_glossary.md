# Simple Chat Agency - Project Glossary

This glossary provides standardized terminology for the Simple Chat Agency project. Use these terms in JIRA tickets, documentation, and team communications to ensure clarity and consistency.

## A

**Agency** - The core orchestration system that coordinates multiple agents to process messages and generate responses.

**Agency Swarm** - The framework used for creating and managing multiple AI agents that work together to process messages.

**Agent** - An individual AI component with a specific role in the message processing pipeline (e.g., Chat Manager, Chat Processor, Chat Assistant).

**Async Task** - A task running asynchronously using Python's asyncio framework, particularly important for handling Slack events without blocking.

## B

**Bolt App** - Refers to the Slack Bolt application instance used to handle Slack API interactions.

**Block Kit** - Slack's UI framework for building rich message layouts and interactive components.

## C

**Circuit Breaker** - A design pattern that prevents cascading failures by detecting when a service is unavailable and temporarily stopping requests to it.

**Clean User Text** - The process of transforming raw message text to remove platform-specific formatting (e.g., Slack mentions).

**Conversation Context** - The accumulated history and state of a user conversation used to provide continuity in responses.

**Conversation ID** - A unique identifier for tracking conversation threads, typically formatted as `{channel}:{thread_ts}`.

## D

**DuckDB** - An analytical SQL database engine used for data processing in the Cash Flow POC project.

## E

**Event Loop** - The core asyncio mechanism for handling concurrent operations in Python.

**Event Handlers** - Functions that respond to specific events from Slack or other platforms.

## F

**Fallback Mechanism** - A system that provides alternative functionality when a primary system fails.

**Firebase** - The cloud database service used for storing conversation data and agent configurations.

**Flask** - The web framework used for the application's HTTP endpoints.

## J

**JIRA Epic** - A large body of work that can be broken down into smaller tasks. Epics for this project might include "Error Handling Improvements" or "Performance Optimization".

**JIRA Story** - A user-centric description of a software feature from an end-user perspective (e.g., "As a user, I want error messages to be clearly formatted").

**JIRA Task** - A specific unit of work that needs to be completed, often technical in nature (e.g., "Implement structured logging system").

**JIRA Bug** - A defect in the code that needs to be fixed (e.g., "Fix race condition in async task management").

## L

**Logging System** - The structured mechanism for recording application events and errors.

## M

**Message Processing Pipeline** - The sequence of steps a message goes through from reception to response generation.

**Memory Management** - The system for tracking and cleaning up resources in the application.

**Multi-Platform Support** - The capability to integrate with multiple messaging platforms beyond Slack.

## O

**OpenAI** - The AI service used for generating responses through its API.

## P

**Processed Events** - A cache of previously handled events to prevent duplicate processing.

**Promise Pattern** - A programming concept for handling asynchronous operations.

## R

**Rate Limiting** - Controlling the frequency of API requests to prevent overuse and ensure fair service.

**Request ID** - A unique identifier assigned to each incoming request for tracking through logs and monitoring.

**Retry Logic** - The system for automatically retrying failed operations with appropriate backoff.

## S

**Slack Bot** - The user-facing interface that interacts with users in Slack workspaces.

**Slack Events API** - The API used to receive events from Slack (e.g., messages, app mentions).

**Socket Mode** - A Slack connection method that uses WebSockets instead of HTTP endpoints.

**Structured Logging** - A format for logs that makes them machine-readable and easily searchable.

## T

**Task Tracking** - The system for monitoring asynchronous tasks and their completion status.

**Thread** - A conversation chain in Slack or other messaging platforms.

**Timeout Protection** - Safeguards that prevent operations from running indefinitely.

## JIRA Ticketing Templates

### Epic Template
```
Title: [AREA] [FEATURE]
Description:
As a [USER TYPE], I need [CAPABILITY] so that [BENEFIT].

Objectives:
- [OBJECTIVE 1]
- [OBJECTIVE 2]

Success Criteria:
- [CRITERIA 1]
- [CRITERIA 2]

Technical Notes:
- [RELEVANT TECHNICAL DETAILS]
```

### Story Template
```
Title: [VERB] [FEATURE] for [USER/SYSTEM]
Description:
As a [USER TYPE],
I want [FUNCTIONALITY]
So that [BENEFIT]

Acceptance Criteria:
- [ ] [CRITERIA 1]
- [ ] [CRITERIA 2]

Technical Notes:
- [IMPLEMENTATION DETAILS]
```

### Task Template
```
Title: [VERB] [SPECIFIC TECHNICAL TASK]
Description:
Implement [SPECIFIC COMPONENT/FEATURE] in [LOCATION]

Details:
- [DETAIL 1]
- [DETAIL 2]

Acceptance Criteria:
- [ ] [CRITERIA 1]
- [ ] [CRITERIA 2]

Related Components:
- [COMPONENT 1]
- [COMPONENT 2]
```

### Bug Template
```
Title: [SPECIFIC ERROR] when [ACTION]
Description:
When [ACTIONS TO REPRODUCE],
[CURRENT BEHAVIOR] occurs.
The expected behavior is [EXPECTED BEHAVIOR].

Steps to Reproduce:
1. [STEP 1]
2. [STEP 2]

Impact:
[SEVERITY] - [DESCRIPTION OF IMPACT]

Possible Solution:
[IF KNOWN]
```

## Sample JIRA Tickets Based on Future Improvements

### Epic: Error Handling System Overhaul
```
Title: ERROR-HANDLING Comprehensive Error Handling System
Description:
As a developer and user, I need a robust error handling system so that issues are properly caught, reported, and can be fixed quickly.

Objectives:
- Implement standardized error formatting across the application
- Ensure users receive appropriate error messages
- Provide detailed internal error logging for troubleshooting
- Add retry mechanisms for transient failures

Success Criteria:
- All errors are captured and do not crash the application
- Users receive helpful error messages with error IDs
- Developers can trace errors using logs and error IDs
- System handles transient failures gracefully

Technical Notes:
- Will require creating a centralized error handling module
- Should implement proper exception hierarchies
```

### Story: User-Facing Error Messages
```
Title: Implement User-Friendly Error Messages for End Users
Description:
As a user,
I want to see clear and helpful error messages when something goes wrong
So that I understand what happened and what I can do about it

Acceptance Criteria:
- [ ] Error messages are concise and user-friendly
- [ ] Technical details are omitted from user-facing messages
- [ ] Error messages include a unique error ID for reference
- [ ] Errors that are the user's fault give clear instructions on how to fix them
- [ ] System errors indicate that the team has been notified

Technical Notes:
- Implement in process_slack_message_async and other user-facing functions
- Create a standard error message format function
```

### Task: Implement Structured Logging System
```
Title: Implement Structured Logging System with Request IDs
Description:
Implement a comprehensive structured logging system that includes request IDs for traceability

Details:
- Create a logger.py module with standardized logging configuration
- Implement a RequestIdFilter to inject request IDs into log records
- Create helper functions for setting and retrieving request context
- Replace all print statements with appropriate logger calls

Acceptance Criteria:
- [ ] All logs are formatted consistently with timestamps and severity levels
- [ ] All logs include a request ID when available
- [ ] Print statements are fully replaced with logger calls
- [ ] Log levels are appropriately used (INFO, WARNING, ERROR, etc.)
- [ ] Logs are machine-readable in JSON format

Related Components:
- app.py
- app_firestore.py
- agency.py
- All message processing functions
```

### Bug: Async Task Exception Handling
```
Title: Unhandled exceptions in async tasks cause silent failures
Description:
When an exception occurs within an async task submitted via submit_async_task,
the exception is not properly caught or logged, causing silent failures.
The expected behavior is for all exceptions to be caught, logged, and reported.

Steps to Reproduce:
1. Submit an async task that will raise an exception
2. Observe that no error is logged or handled

Impact:
HIGH - Critical errors can occur without any visibility, making troubleshooting very difficult

Possible Solution:
Modify submit_async_task to add a done callback that checks for exceptions in the completed future
```

## Priority Classification for JIRA

### P0 (Critical)
- Must be fixed immediately - blocking production use
- Examples: Security vulnerabilities, system crashes, data loss issues

### P1 (High)
- Should be fixed in the current sprint - significant impact on users
- Examples: Error handling improvements, major performance issues

### P2 (Medium)
- Should be planned in near-term roadmap - noticeable impact on users
- Examples: Logging implementation, timeout handling

### P3 (Low)
- Nice to have improvements - minimal impact on current users
- Examples: Code organization, documentation improvements

### P4 (Trivial)
- Extremely low priority - cosmetic or very minor issues
- Examples: Code style consistency, minor refactoring
