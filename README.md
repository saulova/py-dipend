<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h1>Dipend</h1>
  <br/>

[![Issues][issues-shield]][issues-url]
[![Apache-2.0 License][license-shield]][license-url]
[![Contributors][contributors-shield]][contributors-url]

  <p align="center">
    Dipend is a lightweight and flexible dependency injection library, making it easier to manage dependencies in modular applications.
    <br />
    <a href="https://dipend.sauloalvarenga.dev.br"><strong>Explore the docs</strong></a>
  </p>
</div>

<!-- Features -->

## Features

- **Interface-based Dependency Injection**: Use interfaces as references for dependencies, ensuring strong type safety.
- **Mapped Dependencies**: Register and resolve multiple implementations of the same interface by key. This allows you to map different behaviors or strategies to specific identifiers and retrieve them dynamically at runtime based on context.
- **Singleton, Transient and Per Context Support**: Easily configure lifetime scopes for your services.
- **Easy to Extend**: Open and flexible architecture.

<p align="right"><a href="#top">(back to top)</a></p>

<!-- Getting Started -->

## Getting Started

### Installation

First, install Dipend in your project:

```bash
pip install dipend
```

### Basic Usage

Here’s a simple example to show how Dipend works:

```python
from dipend import DependencyContainer
from abc import ABC, abstractmethod

# Define an interface
class ILogger(ABC):
    @abstractmethod
    def info(self, message: str):
        pass

# Implement the interface
class Logger(ILogger):
  def info(self, message: str):
    print(f"INFO: {message}")


# Create a dependent class
class Greeter:
  def __init__(self, logger: ILogger):
    self._logger = logger

  def greet(self, name: str):
    message = f"Hello, {name}!"
    self._logger.info(message)
    return message


# Create the container
dependency_container = DependencyContainer()

# Register dependencies
dependency_container.add_singleton(ILogger, Logger)
dependency_container.add_transient(Greeter)

# Build singletons (optional if you want them ready immediately)
dependency_container.build_singletons()

# Resolve and use a dependency
greeter = dependency_container.get_dependency(Greeter)
result = greeter.greet("World")
print(result)
```

<p align="right"><a href="#top">(back to top)</a></p>

## More Examples

Looking for more use cases or advanced configurations?  
Check out the [full documentation][documentation-url].

<p align="right"><a href="#top">(back to top)</a></p>

## Why Dipend?

**Dipend** fully supports using **interfaces** as references for dependency resolution without needing extra boilerplate or manual token management.

This means you can register and retrieve implementations by their interfaces directly, preserving **clean principles** while keeping your code strongly typed and maintainable.

<p align="right"><a href="#top">(back to top)</a></p>

<!-- CONTRIBUTING -->

## Contributing

Contributions make the open-source community such an amazing place to learn, inspire, and create. We warmly welcome your contributions!

Before contributing, please read the following:

- [CONTRIBUTING GUIDELINES][contributing-guidelines-url]
- [CONTRIBUTOR LICENSE AGREEMENT][cla-url]

If you like the project, don't forget to give it a ⭐️!

<p align="right"><a href="#top">(back to top)</a></p>

<!-- LICENSE -->

## License

Copyright 2025 Saulo V. Alvarenga. All rights reserved.

Licensed under the Apache License, Version 2.0.

See [LICENSE][license-url] for complete license information.

<p align="right"><a href="#top">(back to top)</a></p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://img.shields.io/github/contributors/saulova/py-dipend.svg?style=flat-square
[contributors-url]: https://github.com/saulova/py-dipend/graphs/contributors
[issues-shield]: https://img.shields.io/github/issues/saulova/py-dipend.svg?style=flat-square
[issues-url]: https://github.com/saulova/py-dipend/issues
[license-shield]: https://img.shields.io/github/license/saulova/py-dipend?style=flat-square
[license-url]: https://github.com/saulova/py-dipend/blob/main/LICENSE
[contributing-guidelines-url]: https://github.com/saulova/py-dipend/blob/main/CONTRIBUTING.md
[cla-url]: https://github.com/saulova/py-dipend/blob/main/CLA.md
[documentation-url]: https://dipend.sauloalvarenga.dev.br