from datetime import datetime
import os

import pytest
from pykeepass import create_database
from merger import merge_databases


def delete_database(filename):
    if os.path.exists(filename):
        os.remove(filename)

@pytest.fixture
def database_factory():
    def add_entries(db, current_group, entries):
        for entry in entries:
            if entry["type"] == "group":
                new_group = db.add_group(current_group, entry["name"])
                new_entries = entry["children"]
                add_entries(db, new_group, new_entries)
            else:
                db.add_entry(
                    current_group,
                    entry["title"],
                    entry["username"],
                    entry["password"],
                )

    def factory(filename, password, entries):
        database = create_database(filename, password)
        add_entries(database, database.root_group, entries)

        return database

    return factory


def test_merge_databases_with_1_group_level(database_factory):
    db_1_name = "test_1.kdbx"
    db_1_password = "123tamal"
    entries_1 = [
        {
            "type": "entry",
            "title": "Cool Stuffs",
            "username": "mr.test@coolstuffs.com",
            "password": "s3cr3t",
        },
    ]
    database_1 = database_factory(db_1_name, db_1_password, entries_1)

    db_2_name = "test_1.kdbx"
    db_2_password = "456tamal"
    entries_2 = [
        {
            "type": "entry",
            "title": "Cosas Chidas",
            "username": "sr.test@cosaschidas.com",
            "password": "s3cr3t0",
        },
    ]
    database_2 = database_factory(db_2_name, db_2_password, entries_2)

    expected_users = {
        "Cool Stuffs,mr.test@coolstuffs.com,s3cr3t",
        "Cosas Chidas,sr.test@cosaschidas.com,s3cr3t0",
    }


    db_result_name = "result.kdbx"
    db_result_password = "789tamal"

    merged = merge_databases(db_result_name, db_result_password, [database_1, database_2])

    users = {f"{entry.title},{entry.username},{entry.password}" for entry in merged.entries}

    delete_database(db_1_name)
    delete_database(db_2_name)
    delete_database(db_result_name)

    assert users == expected_users

def test_merge_databases_with_x_group_levels(database_factory):
    db_1_name = "test_1.kdbx"
    db_1_password = "123tamal"
    entries_1 = [
        {
            "type": "group",
            "name": "A",
            "children": [
                {
                    "type": "entry",
                    "title": "A1",
                    "username": "a1@test.com",
                    "password": "3r3ss3cr3tod3amor",
                },
                {
                    "type": "group",
                    "name": "D",
                    "children": [
                        {
                            "type": "entry",
                            "title": "D1",
                            "username": "d1@test.com",
                            "password": "s3cr3t",
                        }
                    ],
                },
            ]
        },
        {
            "type": "group",
            "name": "B",
            "children": [
                {
                    "type": "entry",
                    "title": "B1",
                    "username": "b1@test.com",
                    "password": "password",
                }
            ],
        },
        {
            "type": "group",
            "name": "C",
            "children": [],
        }
    ]
    database_1 = database_factory(db_1_name, db_1_password, entries_1)

    db_2_name = "test_1.kdbx"
    db_2_password = "456tamal"
    entries_2 = [
        {
            "type": "group",
            "name": "A",
            "children": [
                {
                    "type": "group",
                    "name": "F",
                    "children": [
                        {
                            "type": "entry",
                            "title": "F1",
                            "username": "f1@test.com",
                            "password": "robot",
                        }
                    ],
                },
            ]
        },
        {
            "type": "group",
            "name": "C",
            "children": [
                {
                    "type": "group",
                    "name": "G",
                    "children": [
                        {
                            "type": "entry",
                            "title": "G1",
                            "username": "g1@test.com",
                            "password": "wordpass",
                        }
                    ],
                }
            ],
        },
    ]
    database_2 = database_factory(db_2_name, db_2_password, entries_2)

    expected_groups = {"Group: \"\"", "Group: \"A\"", "Group: \"B\"", "Group: \"C\"", "Group: \"A/D\"", "Group: \"A/F\"", "Group: \"C/G\""}
    expected_users = {
        "A": {"A1,a1@test.com,3r3ss3cr3tod3amor"},
        "B": {"B1,b1@test.com,password"},
        "C": set(),
        "D": {"D1,d1@test.com,s3cr3t"},
        "F": {"F1,f1@test.com,robot"},
        "G": {"G1,g1@test.com,wordpass"},
    }

    db_result_name = "result.kdbx"
    db_result_password = "789tamal"
    merged = merge_databases(db_result_name, db_result_password, [database_1, database_2])

    delete_database(db_1_name)
    delete_database(db_2_name)
    delete_database(db_result_name)

    assert expected_groups == {str(group) for group in merged.groups}
    for group_name, users in expected_users.items():
        group = merged.find_groups(name=group_name, first=True)
        assert users == {f"{entry.title},{entry.username},{entry.password}" for entry in group.entries}

def test_entries_with_latest_changes_have_priority(database_factory):
    db_1_name = "test_1.kdbx"
    db_1_password = "123tamal"
    entries_1 = [
        {
            "type": "entry",
            "title": "A",
            "username": "a@test.com",
            "password": "password",
        },
    ]
    database_1 = database_factory(db_1_name, db_1_password, entries_1)
    database_1.entries[0].mtime = datetime(2022, 5, 26, 0, 0, 0)

    db_2_name = "test_1.kdbx"
    db_2_password = "456tamal"
    entries_2 = [
        {
            "type": "entry",
            "title": "A",
            "username": "a@test.com",
            "password": "wordpass",
        },
    ]
    database_2 = database_factory(db_2_name, db_2_password, entries_2)
    database_1.entries[0].mtime = datetime(2022, 5, 27, 0, 0, 0)

    expected_users = {"A,a@test.com,wordpass"}


    db_result_name = "result.kdbx"
    db_result_password = "789tamal"

    merged = merge_databases(db_result_name, db_result_password, [database_1, database_2])

    users = {f"{entry.title},{entry.username},{entry.password}" for entry in merged.entries}

    delete_database(db_1_name)
    delete_database(db_2_name)
    delete_database(db_result_name)

    assert users == expected_users
