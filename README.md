# BitNet CLI Development Environment

A [Devfile](https://devfile.io/) for a ready-to-use BitNet CLI development environment.

## Quick Start

1. Launch this repository in a Devfile-compatible tool (e.g., OpenShift Dev Spaces, Eclipse Che).
2. The workspace will start, and the default 2B parameter model will be downloaded automatically.

## Usage

All commands can be run from your IDE's terminal or task runner.

* **Run Default Inference**: `run-bitnet-inference-example`
* **Run Interactive Chat**: `run-bitnet-chat-interactive`
* **Run Benchmark**: `benchmark-model-2b`
* **Download 3B Model**: `download-model-3b`

### Custom Instructions

To run the model with custom system instructions (e.g., a specific persona), execute `bitnet_run_inference` directly in the container's terminal, using the `-p` (prompt) and `-cnv` (conversational) flags.

## License

This project is licensed under the Eclipse Public License - v 2.0.
