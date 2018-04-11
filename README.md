# Mixology

A generic dependency-resolution algorithm written in pure Python.


## Installation

If you are using [poetry](https://github.com/sdispater/poetry), it's as simple as:

```bash
poetry add mixology
```

If not you can use `pip`:

```bash
pip install mixology
```

## Usage

Mixology is a dependency resolution algorithm.
It is heavily inspired by [Molinillo](https://github.com/CocoaPods/Molinillo) in Ruby.

In order to start using `mixology` you need to initialize a `Resolver` instance
with a `SpecificationProvider` and a `UI` which should be adapted to work with
your system.

Then, you need to call `Resolver.resolve()` with a list of user-requested dependencies
and an optional "locking" `DependencyGraph`.

### Specification provider

The `SpecificationProvider` class forms the basis
for the key integration point for a client library with Molinillo.

Its methods convert the client's domain-specific model objects into concepts the resolver understands:

- Nested dependencies
- Names
- Requirement satisfaction
- Finding specifications (known internally as possibilities)
- Sorting dependencies (for the sake of reasonable resolver performance)

The base class looks like this:

```python
class SpecificationProvider(object):
    """
    Provides information about specifications and dependencies to the resolver,
    allowing the Resolver class to remain generic while still providing power
    and flexibility.

    This contract contains the methods that users of mixology must implement
    using knowledge of their own model classes.
    """

    @property
    def name_for_explicit_dependency_source(self):  # type: () -> str
        return 'user-specified dependency'

    @property
    def name_for_locking_dependency_source(self):  # type: () -> str
        return 'Lockfile'

    def search_for(self, dependency):  # type: (Any) -> List[Any]
        """
        Search for the specifications that match the given dependency.

        The specifications in the returned list will be considered in reverse
        order, so the latest version ought to be last.
        """
        return []

    def dependencies_for(self, specification):  # type: (Any) -> List[Any]
        """
        Returns the dependencies of specification.
        """
        return []

    def is_requirement_satisfied_by(self,
                                    requirement,  # type: Any
                                    activated,    # type: DependencyGraph
                                    spec          # type: Any
                                    ):  # type: (...) -> Any
        """
        Determines whether the given requirement is satisfied by the given
        spec, in the context of the current activated dependency graph.
        """
        return True

    def name_for(self, dependency):  # type: (Any) -> str
        """
        Returns the name for the given dependency.
        """
        return str(dependency)

    def sort_dependencies(self,
                          dependencies,  # type: List[Any]
                          activated,     # type: DependencyGraph
                          conflicts      # type: Dict[str, List[Conflict]]
                          ):  # type: (...) -> List[Any]
        """
        Sort dependencies so that the ones
        that are easiest to resolve are first.

        Easiest to resolve is (usually) defined by:
            1) Is this dependency already activated?
            2) How relaxed are the requirements?
            3) Are there any conflicts for this dependency?
            4) How many possibilities are there to satisfy this dependency?
        """
        return sorted(
            dependencies,
            key=lambda dep: (
                activated.vertex_named(self.name_for(dep)).payload is None,
                conflicts.get(self.name_for(dep) is None)
            )
        )

    def allow_missing(self, dependency):  # type: (Any) -> bool
        """
        Returns whether this dependency, which has no possible matching
        specifications, can safely be ignored.
        """
        return False
```

### UI

The `UI` class helps give feedback on and debug the depency resolution process.

You can subclass it to customize it to your needs.

The base class looks like this:

```python
class UI(object):

    def __init__(self, debug=False):
        self._debug = debug

    @property
    def output(self):
        return sys.stdout

    @property
    def progress_rate(self):  # type: () -> float
        return 0.33

    def is_debugging(self):  # type: () -> bool
        return self._debug

    def indicate_progress(self):  # type: () -> None
        self.output.write('.')

    def before_resolution(self):  # type: () -> None
        self.output.write('Resolving dependencies...\n')

    def after_resolution(self):  # type: () -> None
        self.output.write('')

    def debug(self, message, depth):  # type: (...) -> None
        if self.is_debugging():
            debug_info = str(message)
            debug_info = '\n'.join([
                ':{}: {}'.format(str(depth).rjust(4), s)
                for s in debug_info.split('\n')
            ]) + '\n'

            self.output.write(debug_info)

```


## Contributing

To work on the Mixology codebase, you'll want to fork the project, clone the fork locally
and install the required depedendencies via `poetry <https://poetry.eustace.io>`_.

```bash
git clone git@github.com:sdispater/mixology.git
poetry install
```

Then, create your feature branch:

```bash
git checkout -b my-new-feature
```

Make your modifications, add tests accordingly and execute the test suite:

```bash
poetry run pytest tests/
```

When you are ready commit your changes:

```bash
git commit -am 'Add new feature'
```

push your branch:

```bash
git push origin my-new-feature
```

and finally create a pull request.
