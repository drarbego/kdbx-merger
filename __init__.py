class KDBXDataBase:
    def __init__(self, name, groups=None) -> None:
        self.name = name
        self.groups = groups or {}

    def set_group(self, group):
        self.groups[group.name] = group

    class Group:
        def __init__(self, name, groups=None, entries=None) -> None:
            self.name = name
            self.groups = groups or {}
            self.entries = entries or []


    class Entry:
        def __init__(self, title, username, password):
            self.title = title
            self.username = username
            self.password = password

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, self.__class__):
            raise Exception
        return (
            self.title == __o.title
            and self.username == __o.username
            and self.password == __o.password
        )


def read_kdbx_file(path):
    pass
