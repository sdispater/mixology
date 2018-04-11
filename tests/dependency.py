from semantic_version import Spec


class Dependency:

    def __init__(self, name, constraint):
        self.name = name.lower()
        if not constraint:
            constraint = '*'

        self.constraint = Spec(constraint.replace(' ', ''))

    def allows_prereleases(self):
        return False

    def __str__(self):
        return self.name + ' ' + str(self.constraint)

    def __repr__(self):
        return '<Dependency {}>'.format(str(self))

    def __hash__(self):
        return hash(self.name + ':' + str(self.constraint))
