from datetime import datetime, date, time, timedelta


def parse_due_datetime(due_date, due_time=None):
    """
    把数据库中的日期和时间转换成 datetime。

    due_date 示例:
        2026-09-30

    due_time 示例:
        23:59

    如果没有填写截止时间，
    默认按当天 23:59 处理。
    """
    due_date_obj = datetime.strptime(
        due_date,
        "%Y-%m-%d"
    ).date()

    if due_time:
        due_time_obj = datetime.strptime(
            due_time,
            "%H:%M"
        ).time()
    else:
        due_time_obj = time(23, 59)

    return datetime.combine(
        due_date_obj,
        due_time_obj
    )


def validate_due_date(due_date):
    """
    检查日期格式是否为 YYYY-MM-DD。
    """
    try:
        datetime.strptime(due_date, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_due_time(due_time):
    """
    检查时间格式是否为 HH:MM。

    空字符串允许存在。
    """
    if not due_time:
        return True

    try:
        datetime.strptime(due_time, "%H:%M")
        return True
    except ValueError:
        return False


def is_overdue(due_date, due_time=None, completed=False):
    """
    判断作业是否已经过期。

    已完成作业不算过期。
    """
    if completed:
        return False

    due_datetime = parse_due_datetime(
        due_date,
        due_time
    )

    return due_datetime < datetime.now()


def is_due_soon(
    due_date,
    due_time=None,
    completed=False,
    hours=24
):
    """
    判断任务是否将在指定小时数内截止。

    默认：未来 24 小时内。
    """
    if completed:
        return False

    due_datetime = parse_due_datetime(
        due_date,
        due_time
    )

    now = datetime.now()
    remaining = due_datetime - now

    return (
        timedelta(0)
        <= remaining
        <= timedelta(hours=hours)
    )


def get_deadline_group(
    due_date,
    due_time=None,
    completed=False
):
    """
    返回任务所属分类：

    completed
    overdue
    today
    tomorrow
    this_week
    later
    """

    if completed:
        return "completed"

    due_datetime = parse_due_datetime(
        due_date,
        due_time
    )

    today = date.today()
    due_day = due_datetime.date()

    if due_datetime < datetime.now():
        return "overdue"

    if due_day == today:
        return "today"

    tomorrow = today + timedelta(days=1)

    if due_day == tomorrow:
        return "tomorrow"

    # weekday:
    # Monday = 0
    # Sunday = 6
    end_of_week = today + timedelta(
        days=(6 - today.weekday())
    )

    if due_day <= end_of_week:
        return "this_week"

    return "later"