import tkinter as tk
from tkinter import ttk, messagebox

from database import add_assignment, update_assignment


class AssignmentDialog:
    def __init__(
        self,
        parent,
        on_saved=None,
        assignment=None
    ):
        self.parent = parent
        self.on_saved = on_saved
        self.assignment = assignment

        self.window = tk.Toplevel(parent)

        if assignment is None:
            self.window.title("添加作业")
        else:
            self.window.title("编辑作业")

        self.window.geometry("420x320")
        self.window.resizable(False, False)

        self.window.transient(parent)
        self.window.grab_set()

        self.create_widgets()

        if self.assignment is not None:
            self.load_assignment()

    def create_widgets(self):
        frame = ttk.Frame(self.window, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="课程").grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 5)
        )

        self.course_entry = ttk.Entry(frame, width=35)
        self.course_entry.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(0, 15)
        )

        ttk.Label(frame, text="作业名称").grid(
            row=2,
            column=0,
            sticky="w",
            pady=(0, 5)
        )

        self.title_entry = ttk.Entry(frame, width=35)
        self.title_entry.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(0, 15)
        )

        ttk.Label(
            frame,
            text="截止日期（YYYY-MM-DD）"
        ).grid(
            row=4,
            column=0,
            sticky="w",
            pady=(0, 5)
        )

        self.date_entry = ttk.Entry(frame, width=35)
        self.date_entry.grid(
            row=5,
            column=0,
            sticky="ew",
            pady=(0, 15)
        )

        ttk.Label(
            frame,
            text="截止时间（HH:MM，可留空）"
        ).grid(
            row=6,
            column=0,
            sticky="w",
            pady=(0, 5)
        )

        self.time_entry = ttk.Entry(frame, width=35)
        self.time_entry.grid(
            row=7,
            column=0,
            sticky="ew",
            pady=(0, 20)
        )

        button_frame = ttk.Frame(frame)
        button_frame.grid(
            row=8,
            column=0,
            sticky="e"
        )

        cancel_button = ttk.Button(
            button_frame,
            text="取消",
            command=self.window.destroy
        )
        cancel_button.pack(side="right", padx=(10, 0))

        save_button = ttk.Button(
            button_frame,
            text="保存",
            command=self.save_assignment
        )
        save_button.pack(side="right")

        frame.columnconfigure(0, weight=1)

        self.course_entry.focus()

    def load_assignment(self):
        self.course_entry.insert(
            0,
            self.assignment["course"]
        )

        self.title_entry.insert(
            0,
            self.assignment["title"]
        )

        self.date_entry.insert(
            0,
            self.assignment["due_date"]
        )

        if self.assignment["due_time"]:
            self.time_entry.insert(
                0,
                self.assignment["due_time"]
            )

    def save_assignment(self):
        course = self.course_entry.get().strip()
        title = self.title_entry.get().strip()
        due_date = self.date_entry.get().strip()
        due_time = self.time_entry.get().strip()

        if not course:
            messagebox.showwarning(
                "提示",
                "请输入课程名称。",
                parent=self.window
            )
            return

        if not title:
            messagebox.showwarning(
                "提示",
                "请输入作业名称。",
                parent=self.window
            )
            return

        if not due_date:
            messagebox.showwarning(
                "提示",
                "请输入截止日期。",
                parent=self.window
            )
            return

        if not due_time:
            due_time = None

        if self.assignment is None:
            add_assignment(
                course=course,
                title=title,
                due_date=due_date,
                due_time=due_time
            )
        else:
            update_assignment(
                assignment_id=self.assignment["id"],
                course=course,
                title=title,
                due_date=due_date,
                due_time=due_time
            )

        if self.on_saved:
            self.on_saved()

        self.window.destroy()