import tkinter as tk
from tkinter import ttk, messagebox

from database import (
    get_visible_assignments,
    get_assignment,
    delete_assignment,
    set_assignment_completed,
)

from deadline_utils import (
    is_overdue,
    is_due_soon,
    get_deadline_group,
)

from widget_settings import (
    load_settings,
    save_settings,
)

from ui.assignment_dialog import AssignmentDialog


class HomeworkBoardApp:
    def __init__(self):
        self.root = tk.Tk()

        self.root.title("HomeworkBoard")

        # 去掉 Windows 默认标题栏
        self.root.overrideredirect(True)

        # -------------------------
        # 读取 Widget 设置
        # -------------------------

        self.settings = load_settings()

        self.window_x = self.settings["x"]
        self.window_y = self.settings["y"]

        self.window_width = self.settings["width"]
        self.window_height = self.settings["height"]

        self.position_locked = self.settings["locked"]

        self.root.geometry(
            f"{self.window_width}x{self.window_height}"
            f"+{self.window_x}+{self.window_y}"
        )

        # 拖动时记录鼠标位置
        self.drag_start_x = 0
        self.drag_start_y = 0

        self.create_widgets()
        self.configure_styles()
        self.load_assignments()

        # 关闭窗口时保存位置
        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_app
        )

    # ==================================================
    # UI
    # ==================================================

    def create_widgets(self):
        # -------------------------
        # 顶部栏
        # -------------------------

        header_frame = ttk.Frame(
            self.root,
            padding=(12, 8)
        )
        header_frame.pack(fill="x")

        title_label = ttk.Label(
            header_frame,
            text="HomeworkBoard",
            font=(
                "Microsoft YaHei UI",
                16,
                "bold"
            )
        )
        title_label.pack(side="left")

        # 关闭按钮
        close_button = ttk.Button(
            header_frame,
            text="×",
            width=3,
            command=self.close_app
        )
        close_button.pack(
            side="right",
            padx=(8, 0)
        )

        # 锁定按钮
        self.lock_button = ttk.Button(
            header_frame,
            width=6,
            command=self.toggle_position_lock
        )
        self.lock_button.pack(
            side="right",
            padx=(8, 0)
        )

        self.update_lock_button()

        # 添加作业
        add_button = ttk.Button(
            header_frame,
            text="+ 添加作业",
            command=self.open_add_dialog
        )
        add_button.pack(side="right")

        # -------------------------
        # 顶部栏拖动绑定
        # -------------------------

        for widget in (
            header_frame,
            title_label
        ):
            widget.bind(
                "<Button-1>",
                self.start_drag
            )

            widget.bind(
                "<B1-Motion>",
                self.do_drag
            )

            widget.bind(
                "<ButtonRelease-1>",
                self.end_drag
            )

        # -------------------------
        # 作业列表
        # -------------------------

        content_frame = ttk.Frame(
            self.root,
            padding=(12, 0, 12, 8)
        )
        content_frame.pack(
            fill="both",
            expand=True
        )

        columns = (
            "due",
            "course",
            "title",
            "group",
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
            "group",
            text="分类"
        )

        self.assignment_tree.heading(
            "status",
            text="状态"
        )

        self.assignment_tree.column(
            "due",
            width=145,
            anchor="center"
        )

        self.assignment_tree.column(
            "course",
            width=160,
            anchor="w"
        )

        self.assignment_tree.column(
            "title",
            width=220,
            anchor="w"
        )

        self.assignment_tree.column(
            "group",
            width=75,
            anchor="center"
        )

        self.assignment_tree.column(
            "status",
            width=70,
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

        # 双击编辑
        self.assignment_tree.bind(
            "<Double-1>",
            self.on_double_click
        )

        # -------------------------
        # 右键菜单
        # -------------------------

        self.context_menu = tk.Menu(
            self.root,
            tearoff=0
        )

        self.context_menu.add_command(
            label="完成 / 恢复",
            command=self.toggle_completed
        )

        self.context_menu.add_command(
            label="编辑",
            command=self.edit_selected
        )

        self.context_menu.add_separator()

        self.context_menu.add_command(
            label="删除",
            command=self.delete_selected
        )

        self.assignment_tree.bind(
            "<Button-3>",
            self.show_context_menu
        )

    # ==================================================
    # Styles
    # ==================================================

    def configure_styles(self):
        self.assignment_tree.tag_configure(
            "overdue",
            foreground="#c62828"
        )

        self.assignment_tree.tag_configure(
            "due_soon",
            foreground="#d84315"
        )

        self.assignment_tree.tag_configure(
            "completed",
            foreground="#888888"
        )

    # ==================================================
    # Assignment loading
    # ==================================================

    def load_assignments(self):
        for item in self.assignment_tree.get_children():
            self.assignment_tree.delete(item)

        assignments = get_visible_assignments()

        for assignment in assignments:
            due_date = assignment["due_date"]
            due_time = assignment["due_time"]

            completed = bool(
                assignment["completed"]
            )

            if due_time:
                due_text = (
                    f"{due_date} {due_time}"
                )
            else:
                due_text = due_date

            group = get_deadline_group(
                due_date,
                due_time,
                completed
            )

            group_text = self.get_group_text(
                group
            )

            status_text = (
                "已完成"
                if completed
                else "未完成"
            )

            tag = self.get_assignment_tag(
                due_date,
                due_time,
                completed
            )

            self.assignment_tree.insert(
                "",
                "end",
                iid=str(assignment["id"]),
                values=(
                    due_text,
                    assignment["course"],
                    assignment["title"],
                    group_text,
                    status_text
                ),
                tags=(tag,)
            )

    def get_group_text(self, group):
        mapping = {
            "overdue": "已过期",
            "today": "今天",
            "tomorrow": "明天",
            "this_week": "本周",
            "later": "以后",
            "completed": "已完成",
        }

        return mapping.get(
            group,
            ""
        )

    def get_assignment_tag(
        self,
        due_date,
        due_time,
        completed
    ):
        if completed:
            return "completed"

        if is_overdue(
            due_date,
            due_time,
            completed
        ):
            return "overdue"

        if is_due_soon(
            due_date,
            due_time,
            completed,
            hours=24
        ):
            return "due_soon"

        return ""

    # ==================================================
    # Selection
    # ==================================================

    def get_selected_assignment_id(self):
        selection = (
            self.assignment_tree.selection()
        )

        if not selection:
            messagebox.showinfo(
                "提示",
                "请先选择一条作业。"
            )
            return None

        return int(selection[0])

    # ==================================================
    # Assignment actions
    # ==================================================

    def open_add_dialog(self):
        AssignmentDialog(
            self.root,
            on_saved=self.load_assignments
        )

    def edit_selected(self):
        assignment_id = (
            self.get_selected_assignment_id()
        )

        if assignment_id is None:
            return

        assignment = get_assignment(
            assignment_id
        )

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
        assignment_id = (
            self.get_selected_assignment_id()
        )

        if assignment_id is None:
            return

        assignment = get_assignment(
            assignment_id
        )

        if assignment is None:
            return

        confirmed = messagebox.askyesno(
            "确认删除",
            f"确定删除“{assignment['title']}”吗？"
        )

        if not confirmed:
            return

        delete_assignment(
            assignment_id
        )

        self.load_assignments()

    def toggle_completed(self):
        assignment_id = (
            self.get_selected_assignment_id()
        )

        if assignment_id is None:
            return

        assignment = get_assignment(
            assignment_id
        )

        if assignment is None:
            return

        new_completed = not bool(
            assignment["completed"]
        )

        set_assignment_completed(
            assignment_id,
            completed=new_completed
        )

        self.load_assignments()

    # ==================================================
    # Mouse actions
    # ==================================================

    def on_double_click(self, event):
        item = (
            self.assignment_tree.identify_row(
                event.y
            )
        )

        if not item:
            return

        self.assignment_tree.selection_set(
            item
        )

        self.edit_selected()

    def show_context_menu(self, event):
        item = (
            self.assignment_tree.identify_row(
                event.y
            )
        )

        if not item:
            return

        self.assignment_tree.selection_set(
            item
        )

        try:
            self.context_menu.tk_popup(
                event.x_root,
                event.y_root
            )

        finally:
            self.context_menu.grab_release()

    # ==================================================
    # Widget position
    # ==================================================

    def start_drag(self, event):
        # 锁定后不能拖动
        if self.position_locked:
            return

        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def do_drag(self, event):
        if self.position_locked:
            return

        new_x = (
            self.root.winfo_pointerx()
            - self.drag_start_x
        )

        new_y = (
            self.root.winfo_pointery()
            - self.drag_start_y
        )

        self.root.geometry(
            f"+{new_x}+{new_y}"
        )

    def end_drag(self, event):
        if self.position_locked:
            return

        self.save_widget_settings()

    # ==================================================
    # Position locking
    # ==================================================

    def toggle_position_lock(self):
        self.position_locked = (
            not self.position_locked
        )

        self.update_lock_button()

        self.save_widget_settings()

    def update_lock_button(self):
        if self.position_locked:
            self.lock_button.configure(
                text="解锁"
            )
        else:
            self.lock_button.configure(
                text="锁定"
            )

    # ==================================================
    # Settings
    # ==================================================

    def save_widget_settings(self):
        """
        保存当前窗口位置、尺寸和锁定状态。
        """

        self.root.update_idletasks()

        settings = {
            "x": self.root.winfo_x(),
            "y": self.root.winfo_y(),
            "width": self.root.winfo_width(),
            "height": self.root.winfo_height(),
            "locked": self.position_locked,
        }

        save_settings(
            settings
        )

        self.settings = settings

    # ==================================================
    # Close
    # ==================================================

    def close_app(self):
        self.save_widget_settings()
        self.root.destroy()

    # ==================================================
    # Run
    # ==================================================

    def run(self):
        self.root.mainloop()