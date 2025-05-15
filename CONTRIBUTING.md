# Contributing to Dipend

First off, thank you for considering contributing to Dipend! 🙏  
Your help is extremely valuable and makes this project better for everyone.

This document outlines the guidelines and process for contributing.

## Before You Start

- Make sure to read through the [README](https://github.com/saulova/py-dipend/blob/main/README.md) and [documentation](https://dipend.sauloalvarenga.dev.br) to understand the project.
- Please check if there is an [open issue](https://github.com/saulova/py-dipend/issues) for your intended contribution before opening a new one.
- If you're fixing a bug or suggesting a new feature, open an issue first to discuss your idea.

## Contributor License Agreement (CLA)

In order to protect the project's long-term viability, **all contributors must sign a CLA** before their pull request can be merged.

- You must read the Contributor License Agreement (CLA) at [CLA.md](CLA.md).
- You will be automatically prompted to sign the CLA when opening your first pull request.
- If you have any issues with signing, please contact the maintainers.

We appreciate your understanding and support for open source! ❤️

## How to Contribute

1. **Fork** the repository.
2. **Create a branch**:
   ```bash
   git checkout -b my-feature
   ```
3. **Make your changes**:
   - Follow the project's code style.
   - Write tests for new functionality.
   - Keep changes focused and minimal.
4. **Run tests and lint checks**:
   ```bash
   task lint-all
   task test-all
   ```
5. **Commit your changes**:
   - Use clear and descriptive commit messages.
   - Example: `fix(container): handle multiple registrations gracefully`
6. **Push your branch** and **open a pull request**.

## Code of Conduct

We are committed to creating a welcoming and respectful environment for all contributors.  
Please read and follow our [Code of Conduct](https://github.com/saulova/py-dipend/blob/main/CODE_OF_CONDUCT.md).

## Development Setup

We recommend using [Dev Containers](https://containers.dev/) for a consistent development environment.

### Quick Setup

1. Make sure you have [Docker](https://www.docker.com/) and [Visual Studio Code](https://code.visualstudio.com/) installed.
2. Install the **Dev Containers** extension in VS Code.
3. Clone the repository:
   ```bash
   git clone https://github.com/saulova/py-dipend.git
   cd py-dipend
   ```
4. Open the repository folder in VS Code.
5. When prompted, **"Reopen in Container"**, or manually select:
   > **Command Palette (ctrl+shift+p or cmd+shift+p)** → **Dev Containers: Reopen in Container**

The container will automatically set up all dependencies and development tools for you!

### Available Scripts

Inside the DevContainer terminal:

- `task build-all` — build the project
- `task test-all` — run unit tests
- `task lint-all` — check code style
- `task --list-all` — list all available tasks

---

Thank you again for contributing! 🎉  
We are excited to have you as part of the Dipend community.
