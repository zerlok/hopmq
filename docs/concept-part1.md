# HopMQ Low-Level Architecture Design

## Core Principles

- **Event-Driven Design:** AMQP transport frames and data structures are modeled as events and commands.
- **Finite State Machine (FSM):** The AMQP connection is managed through a state machine to avoid callback hell and
  reduce complex conditional logic.
- **In-Memory Event Queue:** Events and commands are processed sequentially from an in-memory queue, preventing
  concurrency bugs and deadlocks.

## Benefits of This Approach

- **Simplified Flow Control:** No deep nesting or tangled callbacks.
- **Concurrency Safety:** Events are processed one at a time, reducing race conditions.
- **Clear State Transitions:** FSM encapsulates state logic, making it easier to understand and maintain.
- **Extensibility:** New AMQP features can be added by introducing new events and states without breaking the core flow

---

## High-Level Overview

```
+-------------------+      +------------------------+
|   Client Code     |      |    RabbitMQ Broker     |
+-------------------+      +------------------------+
           |                               |
           |       +----------------+      |
           +-----> | In-Memory Queue | <---+
                    +----------------+
                             |
                             v
                   +---------------------+
                   |    Connection FSM   |
                   +---------------------+
                             |
                             v
                   +---------------------+
                   |  Current Connection |
                   |      State          |
                   +---------------------+
```

---

## Components

### 1. **Events & Commands**

- Represents AMQP operations and broker responses.
- Examples:
    - `Connect`, `OpenChannel`, `BindQueue`, `PublishMessage`
    - `ConnectionOk`, `ChannelOpenOk`, `BindOk`, `PublishAck`

### 2. **In-Memory Event Queue**

- A FIFO queue to store commands and events.
- Prevents concurrent state modifications.
- Commands can come from:
    - **Client Code:** When a user calls library methods.
    - **Broker Responses:** When RabbitMQ sends back confirmations.

### 3. **Connection State Machine**

- Handles events and commands based on current state.
- Each state has a `handle` method to process incoming events.
- Transitions between states as needed.

Example states:

- `Disconnected`
- `Connecting`
- `Connected`
- `ChannelOpen`
- `ChannelClosed`
- `Binding`&#x20;

Example transition:

```
State: Disconnected
Event: Connect
Action: Open socket connection, send AMQP handshake
Next State: Connecting
```

### 4. **State Management & Transitions**

- The connection FSM keeps track of the current state.
- Transitions happen automatically as events are handled.
- State-specific logic encapsulated within each state.

Example `handle` method for `Connected` state:

```python
class ConnectedState(State):
    async def handle(self, event: ConnectionEvent) -> StateResult:
        if isinstance(event, BindQueue):
            return StateReset(BindingState(...))
        elif isinstance(event, PublishMessage):
            await self.writer.write(self.marshaller.marshal(event.message))
            return StateDone()
        else:
            raise UnknownEventError(event)
```

1. **State Transitions**:
    - Each state handles a specific event, and when transitioning, the FSM checks the state’s return value.
    - The FSM should manage transitions gracefully, ensuring no invalid transitions occur unless explicitly allowed (
      e.g., StateReset with reset flags).

2. **StateReset Flags**:
    - When a state returns `StateReset`, the FSM may transition to the provided state and reprocess the same event if
      the reset flag is set.
    - Flags should allow the FSM to determine whether the same event should be handled again or if it should move
      directly to the next appropriate state.
    - This allows for flexible transitions, particularly useful for retry mechanisms or conditional state changes.

3. **Error Handling & Fallback Mechanism**:
    - If a state encounters an error or is considered "broken," it may raise an exception.
    - The FSM should have a fallback state mechanism that can be triggered either by the exception or a flag to specify
      the fallback state.
    - If no fallback state is provided, the exception should propagate, and the FSM should halt or enter an error state.

4. **StateComplete and StateFinalize**:
    - `StateComplete` should signify that a state has finished processing and is ready for the FSM to proceed to the
      next state based on subsequent events.
    - `StateFinalize` represents the final state in the FSM cycle, ensuring that no further transitions occur beyond
      this point.

5. **Dynamic State Handling**:
    - States should be able to dynamically adjust based on their context (e.g., event types, previous state). You could
      allow states to define conditions for how and when they can transition or self-reset based on internal state.
    - Each state should have the ability to communicate any changes needed to the FSM's state or execution flow.

6. **State Context**:
    - The FSM could allow each state to maintain its own context, enabling it to track its execution lifecycle
      independently. For example, states could store data about their last event or transition and use that information
      for decision-making in future events.

7. **Timeouts & Retry Logic**:
    - Consider allowing states to define timeouts for their execution. If an event is not handled within a given time
      window, the FSM could either raise an exception or transition to a fallback state.
    - Retry mechanisms could also be implemented by states returning `StateReset` under specific conditions (such as a
      failure to process an event correctly).

8. **Asynchronous Handling**:
    - Since your library involves async handling (for RabbitMQ), asynchronous operations should be supported within
      states. If a state handles an async task (like sending a message or waiting for a response), the state could
      return a `StatePending` status, which the FSM can handle before transitioning to the next state.

9. **State Hooks/Callbacks**:
    - Allow hooks or callbacks to be registered on states, so that other actions can be performed when transitioning
      between states (e.g., logging, metrics, external calls). These hooks could be before or after the state
      transition, giving full control over what occurs at each stage.

These ideas aim to provide flexibility and robustness while maintaining clear control over state transitions and error
management.

### 5. **Broker Communication**

- The connection state communicates directly with RabbitMQ via asyncio low-level API (sockets / transports).
- Sends and receives raw AMQP frames.
- Converts frames into events for the FSM.

Example flow:

1. Client calls `await hopmq.bind_queue("my_queue")`
2. Library provides a `Future` and enqueues a `BindQueue` command.
3. FSM in Connected state detects the command and transitions to the `Binding` state
4. FSM in `Binding` state sends the bind request.
5. RabbitMQ responds with `BindOk`.
6. Library enqueues `BindOk` event.
7. FSM in `Binding` state processes `BindOk`, confirming the binding by setting result for appropriate `Future`&#x20;
8. Client call receives the result.
