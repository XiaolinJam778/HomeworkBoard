import tkinter as tk
from tkinter import ttk, messagebox

from database import (
    get_assignments,
    get_assignment,
    delete_assignment,
    set_assignment_completed
)

from ui.assignment_dialog import AssignmentDialog


class HomeworkBoardApp:
    def __init__(self):
        self.root = tk.Tk()

        self.root.title("HomeworkBoard")
        self.root.geometry("820x450")
        self.root.minsize(700, 380)

        self.create_widgets()
        self.load_assignments()

    def create_widgets(self):
        header_frame = ttk.Frame(self.root, padding=15)
        header_frame.pack(fill="x")

        title_label = ttk.Label(
            header_frame,
            text="HomeworkBoard",
            font=("Microsoft YaHei UI", 18, "bold")
        )
        title_label.pack(side="left")

        add_button = ttk.Button(
            header_frame,
            text="+ 添加作业",
            command=self.open_add_dialog
        )
        add_button.pack(side="right")

        content_frame = ttk.Frame(
            self.root,
            padding=(15, 0, 15, 10)
        )
        content_frame.pack(fill="both", expand=True)

        columns = (
            "due",
            "course",
            "title",
            "status"
        )

        self.assignment_tree = ttk.Treeview(
            content_frame,
            columns=columns,
            show="headings"
        )

        self.assignment_tree.heading(
            "due",
            text="截止时间"
        )

        self.assignment_tree.heading(
            "course",
            text="课程"
        )

        self.assignment_tree.heading(
            "title",
            text="作业"
        )

        self.assignment_tree.heading(
            "status",
            text="状态"
        )

        self.assignment_tree.column(
            "due",
            width=150,
            anchor="center"
        )

        self.assignment_tree.column(
            "course",
            width=190,
            anchor="w"
        )

        self.assignment_tree.column(
            "title",
            width=280,
            anchor="w"
        )

        self.assignment_tree.column(
            "status",
            width=90,
            anchor="center"
        )

        scrollbar = ttk.Scrollbar(
            content_frame,
            orient="vertical",
            command=self.assignment_tree.yview
        )

        self.assignment_tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.assignment_tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.assignment_tree.bind(
            "<Double-1>",
            self.on_double_click
        )

        action_frame = ttk.Frame(
            self.root,
            padding=(15, 0, 15, 15)
        )
        action_frame.pack(fill="x")

        complete_button = ttk.Button(
            action_frame,
            text="完成 / 恢复",
            command=self.toggle_completed
        )
        complete_button.pack(side="left")

        edit_button = ttk.Button(
            action_frame,
            text="编辑",
            command=self.edit_selected
        )
        edit_button.pack(side="left", padx=(10, 0))

        delete_button = ttk.Button(
            action_frame,
            text="删除",
            command=self.delete_selected
        )
        delete_button.pack(side="left", padx=(10, 0))

    def load_assignments(self):
        for item in self.assignment_tree.get_children():
            self.assignment_tree.delete(item)

        assignments = get_assignments()

        for assignment in assignments:
            due_date = assignment["due_date"]
            due_time = assignment["due_time"]

            if due_time:
                due_text = f"{due_date} {due_time}"
            else:
                due_text = due_date

            if assignment["completed"]:
                status_text = "已完成"
            else:
                status_text = "未完成"

            self.assignment_tree.insert(
                "",
                "end",
                iid=str(assignment["id"]),
                values=(
                    due_text,
                    assignment["course"],
                    assignment["title"],
                    status_text
                )
            )

    def get_selected_assignment_id(self):
        selection = self.assignment_tree.selection()

        if not selection:
            messagebox.showinfo(
                "提示",
                "请先选择一条作业。"
            )
            return None

        return int(selection[0])

    def open_add_dialog(self):
        AssignmentDialog(
            self.root,
            on_saved=self.load_assignments
        )

    def edit_selected(self):
        assignment_id = self.get_selected_assignment_id()

        if assignment_id is None:
            return

        assignment = get_assignment(assignment_id)

        if assignment is None:
            messagebox.showerror(
                "错误",
                "没有找到这条作业。"
            )
            return

        AssignmentDialog(
            self.root,
            on_saved=self.load_assignments,
            assignment=assignment
        )

    def delete_selected(self):
        assignment_id = self.get_selected_assignment_id()

        if assignment_id is None:
            return

        assignment = get_assignment(assignment_id)

        if assignment is None:
            return

        confirmed = messagebox.askyesno(
            "确认删除",
            f"确定删除“{assignment['title']}”吗？"
        )

        if not confirmed:
            return

        delete_assignment(assignment_id)
        self.load_assignments()

    def toggle_completed(self):
        assignment_id = self.get_selected_assignment_id()

        if assignment_id is None:
            return

        assignment = get_assignment(assignment_id)

        if assignment is None:
            return

        new_completed = not bool(assignment["completed"])

        set_assignment_completed(
            assignment_id,
            completed=new_completed
        )

        self.load_assignments()

    def on_double_click(self, event):
        item = self.assignment_tree.identify_row(event.y)

        if not item:
            return

        self.assignment_tree.selection_set(item)
        self.edit_selected()

    def run(self):
        self.root.mainloop()