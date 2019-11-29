import pytest

from .package_source import PackageSource


@pytest.fixture()
def source():
    return PackageSource()
