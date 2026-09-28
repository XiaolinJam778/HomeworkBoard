from database import (
    create_tables,
    add_assignment,
    get_assignments,
)


create_tables()

add_assignment(
    "马克思主义原理",
    "小组资料整理",
    "2026-10-05",
    None
)

add_assignment(
    "电路与模拟电子技术",
    "实验预习",
    "2026-10-02",
    "14:00"
)

print("Assignments:\n")

for assignment in get_assignments():
    print(
        assignment["due_date"],
        assignment["due_time"],
        assignment["course"],
        assignment["title"]
    )