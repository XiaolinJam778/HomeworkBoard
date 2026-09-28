from deadline_utils import (
    validate_due_date,
    validate_due_time,
    get_deadline_group,
    is_due_soon,
)


print("Date validation:")
print(validate_due_date("2026-09-30"))
print(validate_due_date("2026-99-99"))

print()

print("Time validation:")
print(validate_due_time("23:59"))
print(validate_due_time("28:80"))
print(validate_due_time(""))

print()

print("Deadline group:")
print(
    get_deadline_group(
        "2026-09-28",
        "23:59"
    )
)

print()

print("Due soon:")
print(
    is_due_soon(
        "2026-09-28",
        "23:59"
    )
)