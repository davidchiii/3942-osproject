def create_comment_dict(
    comment_id, created_time, docname, comment_content, comment_data
):
    return {
        "id": comment_id,
        "created": created_time[:-5],
        "docname": docname,
        "content": comment_content,
        "author": comment_data.get("author", {}).get(
            "displayName", "Unknown Author"
        ),
        "link": comment_data.get("htmlLink", "#"),
    }


def process_comments(comments, user_email, docname):
    items = []

    for comment in comments:
        comment_id = comment["id"]
        comment_content = comment["content"]
        created_time = comment["createdTime"]
        author_email = comment.get("author", {}).get("emailAddress", "")
        made_by_user = False
        if user_email in comment_content.lower():
            items.append(
                create_comment_dict(
                    comment_id, created_time, docname, comment_content, comment
                )
            )

        if author_email.lower() == user_email.lower():
            made_by_user = True

        for reply in comment.get("replies", []):
            if (
                reply.get("author", {}).get("emailAddress", "").lower()
                != user_email.lower()
                and made_by_user
            ):
                items.append(
                    create_comment_dict(
                        comment_id,
                        reply.get("createdTime", ""),
                        docname,
                        reply.get("content", ""),
                        reply,
                    )
                )
            elif user_email in reply.get("content", "").lower():
                items.append(
                    create_comment_dict(
                        comment_id,
                        reply.get("createdTime", ""),
                        docname,
                        reply.get("content", ""),
                        reply,
                    )
                )
    return items


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
