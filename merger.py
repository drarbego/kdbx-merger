from pykeepass import create_database

def merge_databases(filename, password, mergeable_databases=None):
    if not mergeable_databases:
        raise Exception # No databases

    merged_database = create_database(filename, password)

    for db in mergeable_databases:
        _merge_recursively(db.root_group, merged_database.root_group, merged_database)

    return merged_database

def _merge_recursively(read_group, write_group, merged_db):
    for read_entry in read_group.entries:
        write_entry = merged_db.find_entries(
            title=read_entry.title,
            group=write_group,
            recursive=False,
            first=True,
        )
        if write_entry:
            if write_entry.mtime < read_entry.mtime:
                write_entry.title = read_entry.title
                write_entry.username = read_entry.username
                write_entry.password = read_entry.password
                write_entry.mtime = read_entry.mtime
                write_entry.ctime = read_entry.ctime
                write_entry.notes = read_entry.notes or ""
        else:
            write_entry = merged_db.add_entry(
                write_group,
                read_entry.title or "",
                read_entry.username or "",
                read_entry.password or ""
            )
            write_entry.ctime = read_entry.ctime
            write_entry.mtime = read_entry.mtime
            write_entry.notes = read_entry.notes or ""

    for read_sub_group in read_group.subgroups:
        write_sub_group = merged_db.find_groups(name=read_sub_group.name, path=read_sub_group.path, first=True)
        if not write_sub_group:
            write_sub_group = merged_db.add_group(write_group, read_sub_group.name)
        _merge_recursively(read_sub_group, write_sub_group, merged_db)
