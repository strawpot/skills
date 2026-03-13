---
name: engineering-principles
description: "Core engineering and architecture principles for AI-agent-era software development. Guides design decisions toward replaceability, single responsibility, and loose coupling. Use this skill when writing, reviewing, or refactoring code."
---

# Engineering Principles

Software engineering principles optimized for the AI-agent era, where
the cost of development execution is approaching zero. These principles
prioritize **replaceability** over reusability and **clarity** over
cleverness.

## Core Philosophy

The cost of writing code is dropping fast. What remains expensive is
**understanding** code and **untangling** coupled systems. Design so
that any module can be rebuilt from scratch quickly, without rippling
changes across the codebase.

This does NOT mean bloat everything — it means when forced to choose
between reusability and loose coupling, choose loose coupling. A
duplicated 20-line function in two independent modules is better than
a shared utility that couples them.

## Architecture Principles

### 1. Single Responsibility Principle (SRP)

Every module, class, or function should have exactly one reason to
change. If you find yourself saying "this module handles X *and* Y",
split it.

- One file = one concept
- One function = one operation
- One module = one bounded context

### 2. Dependency Inversion

Depend on abstractions (interfaces, protocols, contracts), not on
concrete implementations. High-level modules should not import from
low-level modules — both should depend on shared abstractions.

This makes modules independently replaceable. You can rebuild a module's
internals without touching anything that depends on its interface.

### 3. Composition Over Inheritance

Build behavior by composing small, focused units rather than extending
deep class hierarchies. Inheritance creates tight coupling between
parent and child — changing the parent breaks the child.

- Prefer passing collaborators as arguments (dependency injection)
- Prefer mixins or protocols over base classes
- If inheritance depth > 2, reconsider the design

### 4. Interface Boundaries, Not Shared Internals

Modules communicate through well-defined interfaces — function
signatures, API contracts, message schemas, protocols. Never reach
into another module's internal state or implementation details.

- Public APIs should be small and stable
- Internal implementation is free to change at any time
- If two modules need to share logic, extract it into its own module
  with its own interface — don't make one depend on the other's internals

### 5. Vertical Slicing

Implement features as thin vertical slices through the entire stack
rather than building horizontal layers. Each slice should be
independently deployable and replaceable.

- A feature includes its own routes, logic, storage, and tests
- Avoid "layer" packages (e.g., a single `models/` with everything)
- When replacing a feature, you replace the entire slice, not pieces
  scattered across layers

### 6. Explicit Over Implicit

Prefer explicit configuration, parameters, and dependencies over magic,
convention, or auto-discovery. When a module is rebuilt from scratch,
explicit code is immediately understandable.

- Pass dependencies explicitly — don't rely on globals or ambient state
- Name things for what they do, not what pattern they follow
- If behavior depends on configuration, make the configuration visible
  at the call site

### 7. Fail Fast, Fail Loud

Don't silently swallow errors or degrade gracefully in ways that hide
problems. If something is broken, surface it immediately so it can be
diagnosed and fixed (or the module can be rebuilt).

- Validate inputs at boundaries
- Raise exceptions rather than returning default values for error cases
- Log errors with enough context to diagnose without a debugger
- Avoid catch-all exception handlers that mask the root cause

### 8. Stateless Where Possible

Stateless components are trivially replaceable — you can swap in a new
implementation with zero migration. Push state to the edges (database,
config files, environment) and keep business logic stateless.

- Functions should be pure where practical
- If state is needed, isolate it in a clearly identified stateful
  component (repository, store, cache)
- Avoid hidden state in module-level variables or singletons

## When to Break These Rules

These principles are guidelines, not laws. Break them when:

- **Performance requires it** — sometimes coupling is the only way to
  meet a latency or throughput requirement
- **The domain demands it** — some domains (e.g., UI frameworks)
  genuinely benefit from inheritance hierarchies
- **The scope is tiny** — a 50-line script doesn't need dependency
  inversion

When you do break a rule, leave a comment explaining why.
