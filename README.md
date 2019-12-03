# Mixology

A generic dependency-resolution library written in pure Python.
It is based on the [PubGrub](https://github.com/dart-lang/pub/blob/master/doc/solver.md) algorithm.


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

In order to start using Mixology you need to initialize a [`VersionSolver`](mixology/version_solver.py) instance
with a [`PackageSource`](mixology/package_source.py) which should be adapted to work with your system.

Then, you need to call `VersionSolver.solve()` which will return a [result](mixology/result.py) with the list of decisions
or raise a [`SolveFailure`](mixology/failure.py) which will give a detailed explanation of the reason why the resolution failed.

## Example

This example is extracted from the test suite of Mixology
and uses the [`poetry-semver`](https://github.com/python-poetry/semver) library.

First we need to have our own `PackageSource` class which implements the required methods
and a simple `Dependency` class. Packages will be represented by simple strings.

```python
from semver import Version
from semver import VersionRange
from semver import parse_constraint

from mixology.constraint import Constraint
from mixology.package_source import PackageSource as BasePackageSource
from mixology.range import Range
from mixology.union import Union


class Dependency:

    def __init__(self, name, constraint):  # type: (str, str) -> None
        self.name = name
        self.constraint = parse_constraint(constraint)
        self.pretty_constraint = constraint

    def __str__(self):  # type: () -> str
        return self.pretty_constraint


class PackageSource(BasePackageSource):

    def __init__(self):  # type: () -> None
        self._root_version = Version.parse("0.0.0")
        self._root_dependencies = []
        self._packages = {}

        super(PackageSource, self).__init__()

    @property
    def root_version(self):
        return self._root_version

    def add(
        self, name, version, deps=None
    ):  # type: (str, str, Optional[Dict[str, str]]) -> None
        if deps is None:
            deps = {}

        version = Version.parse(version)
        if name not in self._packages:
            self._packages[name] = {}

        if version in self._packages[name]:
            raise ValueError("{} ({}) already exists".format(name, version))

        dependencies = []
        for dep_name, spec in deps.items():
            dependencies.append(Dependency(dep_name, spec))

        self._packages[name][version] = dependencies

    def root_dep(self, name, constraint):  # type: (str, str) -> None
        self._root_dependencies.append(Dependency(name, constraint))

    def _versions_for(
        self, package, constraint=None
    ):  # type: (Hashable, Any) -> List[Hashable]
        if package not in self._packages:
            return []

        versions = []
        for version in self._packages[package].keys():
            if not constraint or constraint.allows_any(
                Range(version, version, True, True)
            ):
                versions.append(version)

        return sorted(versions, reverse=True)

    def dependencies_for(self, package, version):  # type: (Hashable, Any) -> List[Any]
        if package == self.root:
            return self._root_dependencies

        return self._packages[package][version]

    def convert_dependency(self, dependency):  # type: (Dependency) -> Constraint
        if isinstance(dependency.constraint, VersionRange):
            constraint = Range(
                dependency.constraint.min,
                dependency.constraint.max,
                dependency.constraint.include_min,
                dependency.constraint.include_max,
                dependency.pretty_constraint,
            )
        else:
            # VersionUnion
            ranges = [
                Range(
                    range.min,
                    range.max,
                    range.include_min,
                    range.include_max,
                    str(range),
                )
                for range in dependency.constraint.ranges
            ]
            constraint = Union.of(ranges)

        return Constraint(dependency.name, constraint)
```

Now, we need to specify our root dependencies and the available packages.

```python
source = PackageSource()

source.root_dep("a", "1.0.0")
source.root_dep("b", "1.0.0")

source.add("a", "1.0.0", deps={"shared": ">=2.0.0 <4.0.0"})
source.add("b", "1.0.0", deps={"shared": ">=3.0.0 <5.0.0"})
source.add("shared", "2.0.0")
source.add("shared", "3.0.0")
source.add("shared", "3.6.9")
source.add("shared", "4.0.0")
source.add("shared", "5.0.0")
```

Now that everything is in place we can create a `VersionSolver` instance
with the newly created `PackageSource` and call `solve()` to retrieve a `SolverResult` instance.

```python
from mixology.version_solver import VersionSolver

solver = VersionSolver(source)
result = solver.solve()
result.decisions
# {Package("_root_"): <Version 0.0.0>, 'b': <Version 1.0.0>, 'a': <Version 1.0.0>, 'shared': <Version 3.6.9>}
result.attempted_solutions
# 1
```


## Contributing

To work on the Mixology codebase, you'll want to fork the project, clone the fork locally
and install the required dependencies via `poetry <https://poetry.eustace.io>`_.

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

When you are ready, commit your changes:

```bash
git commit -am 'Add new feature'
```

push your branch:

```bash
git push origin my-new-feature
```

and finally create a pull request.
