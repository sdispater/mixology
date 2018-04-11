from semantic_version import Version


class Package:

    def __init__(self, name, version):
        self.name = name.lower()
        self.version = Version.coerce(version)
        self.requires = []

    def is_prerelease(self):
        return len(self.version.prerelease) > 0

    def __str__(self):
        return '{}=={}'.format(self.name, str(self.version))

    def __repr__(self):
        return '<Package {}>'.format(str(self))

    def __hash__(self):
        return hash(self.name + ':' + str(self.version))
