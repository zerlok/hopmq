# HopMQ

A new way to connect to RabbitMQ with python.

## Useful resources

* [roadmap](docs/roadmap.md)
* [concept pt1](docs/concept-part1.md)
* [concept pt2](docs/concept-part2.md)

## Why HopMQ?

Here’s what people often struggle with in current libraries:

* **Callback Hell**: Even with asyncio, some libraries still feel very callback-heavy (e.g., on_message handlers).
* **Manual Connection Management**: Reconnecting after failures can be clumsy and inconsistent across libraries.
* **Boilerplate Code**: You often need to write a lot of repetitive code to set up consumers, producers, exchanges, etc.
* **Limited High-Level Abstractions**: Libraries like aio-pika are quite low-level, so users build their own patterns repeatedly.

This lib will offer:

* **Native Async/Await Everything**: Fully leverage Python’s async/await without relying on callback-based interfaces.
* **Strict Typed Message Handling**: Support message schemas (e.g., Pydantic) for type safety and easy validation.
* **Reconnection & Heartbeats**: Handle reconnections transparently, with configurable retry strategies.
* **Middleware & Hooks**: Let users plug in middleware for logging, retries, transformations, etc.
* **Declarative Consumers/Producers**: Use decorators or simple class-based handlers, similar to FastAPI's design.
* **Built-in RPC Support**: Make request-response patterns trivial without manual correlation ID handling.

