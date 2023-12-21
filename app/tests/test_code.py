from __init__ import process_comments


def test_process_comments():
    comments = [
        {
            "id": "1",
            "content": "An included comment user1@test.com",
            "createdTime": "2023-01-01T00:00:00.000Z",
            "author": {
                "emailAddress": "user1@test.com",
                "displayName": "User 1",
            },
            "replies": [
                {
                    "content": "An included comment",
                    "createdTime": "2023-01-02T00:00:00.000Z",
                    "author": {
                        "emailAddress": "user2@test.com",
                        "displayName": "User 2",
                    },
                }
            ],
        },
        {
            "id": "2",
            "content": "An excluded comment",
            "createdTime": "2023-01-03T00:00:00.000Z",
            "author": {
                "emailAddress": "user1@test.com",
                "displayName": "User 1",
            },
            "replies": [
                {
                    "content": "An included comment user1@test.com",
                    "createdTime": "2023-01-04T00:00:00.000Z",
                    "author": {
                        "emailAddress": "user2@test.com",
                        "displayName": "User 2",
                    },
                }
            ],
        },
    ]
    result = process_comments(comments, "user1@test.com", "Example")

    expected = [
        {
            "id": "1",
            "created": "2023-01-01T00:00:00",
            "docname": "Example",
            "content": "An included comment user1@test.com",
            "author": "User 1",
            "link": "#",
        },
        {
            "id": "1",
            "created": "2023-01-02T00:00:00",
            "docname": "Example",
            "content": "An included comment",
            "author": "User 2",
            "link": "#",
        },
        {
            "id": "2",
            "created": "2023-01-04T00:00:00",
            "docname": "Example",
            "content": "An included comment user1@test.com",
            "author": "User 2",
            "link": "#",
        },
    ]

    assert result == expected
