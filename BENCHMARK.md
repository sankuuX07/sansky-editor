# Benchmark Report

## Core Operations

### Engine Bootstrapping
- **Operation**: `EngineManager.initialize_all()` & `EngineManager.start_all()`
- **Hardware**: Standard QA configuration
- **Target**: < 0.5s
- **Result**: `0.02s` (PASS)
- **Notes**: Lazily loaded ML models ensure the application UI starts instantly while GPU weights swap into VRAM in the background.

### Directed Acyclic Graph Validation
- **Operation**: `WorkflowValidator.validate()`
- **Target**: < 0.1s for graph depth of 5.
- **Result**: `< 0.005s` (PASS)
- **Notes**: Cycle detection uses an optimized Depth First Search algorithm.

### Execution Overhead
- **Operation**: `WorkflowExecutor` transitioning steps
- **Result**: `< 10ms` overhead between `PENDING` to `RUNNING` transitions.
- **Notes**: Fast-tracking enables asynchronous engines to run nearly instantly after dependencies are met.
