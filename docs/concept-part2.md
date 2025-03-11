# HopMQ Architecture Overview

**HopMQ** is an asynchronous Python library for interacting with RabbitMQ using the low-level `asyncio` API. It handles
communication with RabbitMQ brokers and processes events through a Finite State Machine (FSM) to ensure robust and
fault-tolerant operation. It ensures robust event handling and fault-tolerant communication with RabbitMQ while
maintaining an efficient and scalable architecture through async communication and a state machine-driven process.

## Key Concepts

### 1. Finite State Machine (FSM)

The FSM is the core of the architecture, managing state transitions based on events received from RabbitMQ. Each state
processes events and determines the next steps in the execution flow.

#### State Handling

- Each state implements a `handle(event)` method that processes incoming events.
- States return one of the following outcomes:
    - `StateReset`: The FSM switches to the provided new state. It may invoke `handle(event)` again depending on reset
      flags.
    - `StateComplete`: The FSM completes processing and moves to the next state.
    - `StateFinalize`: The FSM completes execution and enters the final state, halting event processing.

#### Error Handling

- The FSM can propagate the exception or transition to a fallback state if one is configured.
- If a state encounters an issue (i.e., a failure or broken state) and the state can't transit to another state, it may
  raise an exception.

### 2. Asynchronous Communication with RabbitMQ

The FSM communicates with RabbitMQ using the low-level `asyncio` socket connection/transport API, ensuring non-blocking
operations.

#### Background Listener Routine

- When the RabbitMQ connection opens, a background routine is initiated to listen for incoming events.
- The routine runs asynchronously, listening for events and dispatching them to the appropriate state handler via in
  memory queue.

#### Connection Failure Handling

- If the background listener fails unexpectedly (e.g., due to a lost connection or read failure), the FSM transitions to
  a **Reconnection State**.
- The FSM will handle retries or backoff strategies in this state, attempting to restore the connection to the broker
  and continue event processing.

### 3. State Transitions and Event Processing

- States may transition based on event handling or network issues.
- Each state can transition the FSM to another state, process the current event, or finalize the execution.
- The FSM ensures that state transitions are orderly, with clear handling for each type of outcome (`StateReset`,
  `StateComplete`, `StateFinalize`).

#### Example State Transitions

- If an event is successfully processed, the FSM moves to the next state with `StateComplete`.
- If the event requires the FSM to reset, it returns `StateReset` and may transition to a new state.
- If the state completes and there are no further actions, the FSM returns `StateFinalize` to halt further processing.

### 4. Reconnection Logic

- The **Reconnection State** handles network failures. If a connection to RabbitMQ is lost, the FSM attempts to
  reconnect.
- The FSM may apply configurable retry intervals, exponential backoff strategies, and a maximum retry limit to prevent
  endless reconnection attempts.
- Once the connection is re-established, the FSM returns to the previous state or moves to a specific state to handle
  potential missed events.

### 5. Asynchronous Event Dispatching

- Events from RabbitMQ are processed asynchronously using the background listener.
- Once an event is received, the FSM asynchronously dispatches the event to the current state handler for processing.
- This allows the system to handle multiple tasks concurrently without blocking on event processing.

## Summary of State Machine Outcomes

| Outcome         | Description                                                                  |
|-----------------|------------------------------------------------------------------------------|
| `StateReset`    | Transition to a new state, may reprocess the event depending on reset flags. |
| `StateComplete` | Finish processing and transition to the next state.                          |
| `StateFinalize` | Finalize the FSM, stop processing further events.                            |
