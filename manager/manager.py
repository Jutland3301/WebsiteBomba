from __future__ import annotations

import json
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
import tkinter as tk
import webbrowser

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import generator


ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
PROJECT_CONTENT = CONTENT / "projects"
IMAGES = ROOT / "images"

PREVIEW_PORT = 8000

preview_server = None
preview_thread = None


# ============================================================
# JSON
# ============================================================

def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )


# ============================================================
# IMAGE
# ============================================================

def choose_image(parent) -> str | None:

    source = filedialog.askopenfilename(
        parent=parent,
        title="Choose image",
        filetypes=[
            (
                "Images",
                "*.jpg *.jpeg *.png *.gif *.webp"
            ),
            ("All files", "*.*")
        ]
    )

    if not source:
        return None

    source_path = Path(source)

    IMAGES.mkdir(
        parents=True,
        exist_ok=True
    )

    destination = IMAGES / source_path.name

    # Avoid overwriting a different existing file.
    if destination.exists():

        counter = 1

        while True:

            candidate = (
                IMAGES
                / (
                    f"{source_path.stem}_{counter}"
                    f"{source_path.suffix}"
                )
            )

            if not candidate.exists():
                destination = candidate
                break

            counter += 1

    try:
        shutil.copy2(
            source_path,
            destination
        )

    except shutil.SameFileError:
        pass

    return f"images/{destination.name}"


# ============================================================
# PREVIEW SERVER
# ============================================================

def port_is_open(port: int) -> bool:

    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    ) as sock:

        return (
            sock.connect_ex(
                ("127.0.0.1", port)
            )
            == 0
        )


def start_preview_server():

    global preview_server
    global preview_thread

    if port_is_open(PREVIEW_PORT):
        return

    class RootHandler(SimpleHTTPRequestHandler):

        def __init__(
            self,
            *args,
            **kwargs
        ):
            super().__init__(
                *args,
                directory=str(ROOT),
                **kwargs
            )

        def log_message(
            self,
            format,
            *args
        ):
            pass

    preview_server = ThreadingHTTPServer(
        ("127.0.0.1", PREVIEW_PORT),
        RootHandler
    )

    preview_thread = threading.Thread(
        target=preview_server.serve_forever,
        daemon=True
    )

    preview_thread.start()

    # Give Windows a moment to bind the port.
    time.sleep(0.2)


# ============================================================
# GIT
# ============================================================

def run_git(*arguments: str):

    return subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )


# ============================================================
# CMS
# ============================================================

class SiteManager(tk.Tk):

    def __init__(self):

        super().__init__()

        self.title(
            "Personal Website Manager"
        )

        self.geometry("900x700")
        self.minsize(760, 580)

        self.protocol(
            "WM_DELETE_WINDOW",
            self.close_manager
        )

        self.notebook = ttk.Notebook(
            self
        )

        self.notebook.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.home_tab = ttk.Frame(
            self.notebook
        )

        self.about_tab = ttk.Frame(
            self.notebook
        )

        self.projects_tab = ttk.Frame(
            self.notebook
        )

        self.notebook.add(
            self.home_tab,
            text="HOME"
        )

        self.notebook.add(
            self.about_tab,
            text="ABOUT"
        )

        self.notebook.add(
            self.projects_tab,
            text="PROJECTS"
        )

        self.build_home()
        self.build_about()
        self.build_projects()

        self.build_bottom_bar()

    # ========================================================
    # COMMON UI
    # ========================================================

    def labeled_entry(
        self,
        parent,
        label,
        row
    ):

        ttk.Label(
            parent,
            text=label
        ).grid(
            row=row,
            column=0,
            sticky="w",
            padx=10,
            pady=6
        )

        entry = ttk.Entry(
            parent,
            width=70
        )

        entry.grid(
            row=row,
            column=1,
            sticky="ew",
            padx=10,
            pady=6
        )

        return entry

    def image_row(
        self,
        parent,
        row
    ):

        ttk.Label(
            parent,
            text="Image"
        ).grid(
            row=row,
            column=0,
            sticky="w",
            padx=10,
            pady=6
        )

        holder = ttk.Frame(parent)

        holder.grid(
            row=row,
            column=1,
            sticky="ew",
            padx=10,
            pady=6
        )

        holder.columnconfigure(
            0,
            weight=1
        )

        entry = ttk.Entry(
            holder
        )

        entry.grid(
            row=0,
            column=0,
            sticky="ew"
        )

        def browse():

            path = choose_image(self)

            if path:

                entry.delete(
                    0,
                    "end"
                )

                entry.insert(
                    0,
                    path
                )

        ttk.Button(
            holder,
            text="BROWSE...",
            command=browse
        ).grid(
            row=0,
            column=1,
            padx=(5, 0)
        )

        return entry

    # ========================================================
    # HOME
    # ========================================================

    def build_home(self):

        frame = self.home_tab

        frame.columnconfigure(
            1,
            weight=1
        )

        frame.rowconfigure(
            4,
            weight=1
        )

        data = load_json(
            CONTENT / "home.json"
        )

        self.home_title = (
            self.labeled_entry(
                frame,
                "Title",
                0
            )
        )

        self.home_date = (
            self.labeled_entry(
                frame,
                "Date",
                1
            )
        )

        self.home_image = (
            self.image_row(
                frame,
                2
            )
        )

        self.home_updated = (
            self.labeled_entry(
                frame,
                "Last updated",
                3
            )
        )

        ttk.Label(
            frame,
            text="Body"
        ).grid(
            row=4,
            column=0,
            sticky="nw",
            padx=10,
            pady=6
        )

        self.home_body = tk.Text(
            frame,
            height=20,
            wrap="word"
        )

        self.home_body.grid(
            row=4,
            column=1,
            sticky="nsew",
            padx=10,
            pady=6
        )

        self.home_title.insert(
            0,
            data.get("title", "")
        )

        self.home_date.insert(
            0,
            data.get("date", "")
        )

        self.home_image.insert(
            0,
            data.get("image", "")
        )

        self.home_updated.insert(
            0,
            data.get(
                "last_updated",
                ""
            )
        )

        self.home_body.insert(
            "1.0",
            data.get("body", "")
        )

        ttk.Button(
            frame,
            text="SAVE HOME",
            command=self.save_home
        ).grid(
            row=5,
            column=1,
            sticky="e",
            padx=10,
            pady=10
        )

    def save_home(
        self,
        show_message=True
    ):

        data = {
            "title":
                self.home_title.get(),

            "date":
                self.home_date.get(),

            "body":
                self.home_body.get(
                    "1.0",
                    "end-1c"
                ),

            "image":
                self.home_image.get(),

            "last_updated":
                self.home_updated.get()
        }

        save_json(
            CONTENT / "home.json",
            data
        )

        generator.generate_home()

        if show_message:

            messagebox.showinfo(
                "Saved",
                "HOME saved."
            )

    # ========================================================
    # ABOUT
    # ========================================================

    def build_about(self):

        frame = self.about_tab

        frame.columnconfigure(
            1,
            weight=1
        )

        frame.rowconfigure(
            5,
            weight=1
        )

        data = load_json(
            CONTENT / "about.json"
        )

        self.about_title = (
            self.labeled_entry(
                frame,
                "Title",
                0
            )
        )

        self.about_image = (
            self.image_row(
                frame,
                1
            )
        )

        self.about_interests = (
            self.labeled_entry(
                frame,
                "Interests",
                2
            )
        )

        self.about_github = (
            self.labeled_entry(
                frame,
                "GitHub",
                3
            )
        )

        self.about_email = (
            self.labeled_entry(
                frame,
                "Email",
                4
            )
        )

        ttk.Label(
            frame,
            text="Body"
        ).grid(
            row=5,
            column=0,
            sticky="nw",
            padx=10,
            pady=6
        )

        self.about_body = tk.Text(
            frame,
            height=18,
            wrap="word"
        )

        self.about_body.grid(
            row=5,
            column=1,
            sticky="nsew",
            padx=10,
            pady=6
        )

        self.about_title.insert(
            0,
            data.get("title", "")
        )

        self.about_image.insert(
            0,
            data.get("image", "")
        )

        self.about_interests.insert(
            0,
            data.get(
                "interests",
                ""
            )
        )

        self.about_github.insert(
            0,
            data.get(
                "github",
                ""
            )
        )

        self.about_email.insert(
            0,
            data.get(
                "email",
                ""
            )
        )

        self.about_body.insert(
            "1.0",
            data.get("body", "")
        )

        ttk.Button(
            frame,
            text="SAVE ABOUT",
            command=self.save_about
        ).grid(
            row=6,
            column=1,
            sticky="e",
            padx=10,
            pady=10
        )

    def save_about(
        self,
        show_message=True
    ):

        data = {
            "title":
                self.about_title.get(),

            "body":
                self.about_body.get(
                    "1.0",
                    "end-1c"
                ),

            "image":
                self.about_image.get(),

            "interests":
                self.about_interests.get(),

            "github":
                self.about_github.get(),

            "email":
                self.about_email.get()
        }

        save_json(
            CONTENT / "about.json",
            data
        )

        generator.generate_about()

        if show_message:

            messagebox.showinfo(
                "Saved",
                "ABOUT saved."
            )

    # ========================================================
    # PROJECT LIST
    # ========================================================

    def build_projects(self):

        frame = self.projects_tab

        toolbar = ttk.Frame(frame)

        toolbar.pack(
            fill="x",
            padx=10,
            pady=10
        )

        ttk.Button(
            toolbar,
            text="+ NEW PROJECT",
            command=self.new_project
        ).pack(
            side="left"
        )

        ttk.Button(
            toolbar,
            text="REFRESH",
            command=self.refresh_projects
        ).pack(
            side="left",
            padx=5
        )

        self.project_list = tk.Listbox(
            frame,
            font=(
                "Courier New",
                11
            )
        )

        self.project_list.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5
        )

        self.project_list.bind(
            "<Double-Button-1>",
            lambda event:
                self.edit_selected_project()
        )

        controls = ttk.Frame(frame)

        controls.pack(
            fill="x",
            padx=10,
            pady=10
        )

        ttk.Button(
            controls,
            text="EDIT",
            command=self.edit_selected_project
        ).pack(
            side="left"
        )

        ttk.Button(
            controls,
            text="DELETE",
            command=self.delete_selected_project
        ).pack(
            side="left",
            padx=5
        )

        self.refresh_projects()

    def refresh_projects(self):

        self.project_list.delete(
            0,
            "end"
        )

        data = load_json(
            CONTENT / "projects.json"
        )

        self.projects = data.get(
            "projects",
            []
        )

        for project in self.projects:

            text = (
                f'{project.get("date", "")}'
                f'   '
                f'{project.get("title", "")}'
            )

            self.project_list.insert(
                "end",
                text
            )

    def new_project(self):

        self.open_project_editor()

    def edit_selected_project(self):

        selection = (
            self.project_list
            .curselection()
        )

        if not selection:

            messagebox.showinfo(
                "Project",
                "Select a project first."
            )

            return

        project = self.projects[
            selection[0]
        ]

        self.open_project_editor(
            project.get("slug")
        )

    # ========================================================
    # PROJECT EDITOR
    # ========================================================

    def open_project_editor(
        self,
        existing_slug=None
    ):

        window = tk.Toplevel(self)

        window.title(
            "Project Editor"
        )

        window.geometry(
            "760x650"
        )

        window.columnconfigure(
            1,
            weight=1
        )

        window.rowconfigure(
            7,
            weight=1
        )

        fields = {}

        # ---------------- Slug

        ttk.Label(
            window,
            text="Slug"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=10,
            pady=5
        )

        fields["slug"] = ttk.Entry(
            window
        )

        fields["slug"].grid(
            row=0,
            column=1,
            sticky="ew",
            padx=10,
            pady=5
        )

        # ---------------- Normal fields

        normal_fields = [
            ("title", "Title"),
            ("date", "Date"),
            ("status", "Status"),
            (
                "description",
                "Description"
            )
        ]

        row = 1

        for key, label in normal_fields:

            ttk.Label(
                window,
                text=label
            ).grid(
                row=row,
                column=0,
                sticky="w",
                padx=10,
                pady=5
            )

            entry = ttk.Entry(
                window
            )

            entry.grid(
                row=row,
                column=1,
                sticky="ew",
                padx=10,
                pady=5
            )

            fields[key] = entry

            row += 1

        # ---------------- Image

        ttk.Label(
            window,
            text="Image"
        ).grid(
            row=5,
            column=0,
            sticky="w",
            padx=10,
            pady=5
        )

        image_holder = ttk.Frame(
            window
        )

        image_holder.grid(
            row=5,
            column=1,
            sticky="ew",
            padx=10,
            pady=5
        )

        image_holder.columnconfigure(
            0,
            weight=1
        )

        fields["image"] = ttk.Entry(
            image_holder
        )

        fields["image"].grid(
            row=0,
            column=0,
            sticky="ew"
        )

        def browse_project_image():

            path = choose_image(
                window
            )

            if path:

                fields["image"].delete(
                    0,
                    "end"
                )

                fields["image"].insert(
                    0,
                    path
                )

        ttk.Button(
            image_holder,
            text="BROWSE...",
            command=browse_project_image
        ).grid(
            row=0,
            column=1,
            padx=(5, 0)
        )

        # ---------------- GitHub

        ttk.Label(
            window,
            text="GitHub"
        ).grid(
            row=6,
            column=0,
            sticky="w",
            padx=10,
            pady=5
        )

        fields["github"] = ttk.Entry(
            window
        )

        fields["github"].grid(
            row=6,
            column=1,
            sticky="ew",
            padx=10,
            pady=5
        )

        # ---------------- Body

        ttk.Label(
            window,
            text="Body"
        ).grid(
            row=7,
            column=0,
            sticky="nw",
            padx=10,
            pady=5
        )

        body = tk.Text(
            window,
            height=18,
            wrap="word"
        )

        body.grid(
            row=7,
            column=1,
            sticky="nsew",
            padx=10,
            pady=5
        )

        # ---------------- Load existing

        if existing_slug:

            source = (
                PROJECT_CONTENT
                / f"{existing_slug}.json"
            )

            if source.exists():

                data = load_json(
                    source
                )

                for key in fields:

                    fields[key].insert(
                        0,
                        data.get(key, "")
                    )

                body.insert(
                    "1.0",
                    data.get("body", "")
                )

        # ---------------- Save

        def save():

            slug = (
                fields["slug"]
                .get()
                .strip()
            )

            if not slug:

                messagebox.showerror(
                    "Invalid slug",
                    "Slug is required.",
                    parent=window
                )

                return

            # Only safe URL/file characters.
            if not re.fullmatch(
                r"[a-z0-9]+(?:-[a-z0-9]+)*",
                slug
            ):

                messagebox.showerror(
                    "Invalid slug",
                    (
                        "Use only lowercase letters, "
                        "numbers and hyphens.\n\n"
                        "Example:\n"
                        "stm32-audio-recorder"
                    ),
                    parent=window
                )

                return

            new_json = (
                PROJECT_CONTENT
                / f"{slug}.json"
            )

            # Prevent accidentally replacing another project.
            if (
                new_json.exists()
                and slug != existing_slug
            ):

                messagebox.showerror(
                    "Slug exists",
                    (
                        "Another project already "
                        "uses this slug."
                    ),
                    parent=window
                )

                return

            project = {
                key:
                    entry.get().strip()

                for key, entry
                in fields.items()
            }

            project["body"] = (
                body.get(
                    "1.0",
                    "end-1c"
                )
            )

            PROJECT_CONTENT.mkdir(
                parents=True,
                exist_ok=True
            )

            save_json(
                new_json,
                project
            )

            index = load_json(
                CONTENT
                / "projects.json"
            )

            projects = index.get(
                "projects",
                []
            )

            # Remove previous index entry.
            projects = [
                item
                for item in projects
                if item.get("slug")
                not in {
                    slug,
                    existing_slug
                }
            ]

            projects.insert(
                0,
                {
                    "slug":
                        slug,

                    "title":
                        project["title"],

                    "date":
                        project["date"],

                    "description":
                        project[
                            "description"
                        ],

                    "image":
                        project["image"]
                }
            )

            index["projects"] = (
                projects
            )

            save_json(
                CONTENT
                / "projects.json",
                index
            )

            # ---------------- Slug rename cleanup

            if (
                existing_slug
                and existing_slug != slug
            ):

                old_json = (
                    PROJECT_CONTENT
                    / f"{existing_slug}.json"
                )

                old_html = (
                    ROOT
                    / "projects"
                    / f"{existing_slug}.html"
                )

                if old_json.exists():
                    old_json.unlink()

                if old_html.exists():
                    old_html.unlink()

            generator.generate_projects()
            generator.generate_project_pages()

            self.refresh_projects()

            window.destroy()

            messagebox.showinfo(
                "Saved",
                "Project saved."
            )

        ttk.Button(
            window,
            text="SAVE PROJECT",
            command=save
        ).grid(
            row=8,
            column=1,
            sticky="e",
            padx=10,
            pady=10
        )

    # ========================================================
    # DELETE PROJECT
    # ========================================================

    def delete_selected_project(self):

        selection = (
            self.project_list
            .curselection()
        )

        if not selection:
            return

        project = self.projects[
            selection[0]
        ]

        slug = project.get(
            "slug"
        )

        title = project.get(
            "title",
            slug
        )

        if not messagebox.askyesno(
            "Delete project",
            (
                f"Delete project:\n\n"
                f"{title}\n\n"
                f"This cannot be undone "
                f"from the manager."
            )
        ):

            return

        index = load_json(
            CONTENT / "projects.json"
        )

        index["projects"] = [
            item
            for item
            in index.get(
                "projects",
                []
            )
            if item.get("slug")
            != slug
        ]

        save_json(
            CONTENT / "projects.json",
            index
        )

        json_file = (
            PROJECT_CONTENT
            / f"{slug}.json"
        )

        html_file = (
            ROOT
            / "projects"
            / f"{slug}.html"
        )

        if json_file.exists():
            json_file.unlink()

        if html_file.exists():
            html_file.unlink()

        generator.generate_projects()

        self.refresh_projects()

    # ========================================================
    # SAVE CURRENT FORM DATA
    # ========================================================

    def save_main_pages(self):

        self.save_home(
            show_message=False
        )

        self.save_about(
            show_message=False
        )

    # ========================================================
    # GENERATE
    # ========================================================

    def generate_all(self):

        try:

            self.save_main_pages()

            generator.generate_all()

            messagebox.showinfo(
                "Generated",
                "Site generated successfully."
            )

        except Exception as error:

            messagebox.showerror(
                "Generation failed",
                str(error)
            )

    # ========================================================
    # PREVIEW
    # ========================================================

    def preview(self):

        try:

            self.save_main_pages()

            generator.generate_all()

            start_preview_server()

            webbrowser.open(
                (
                    f"http://localhost:"
                    f"{PREVIEW_PORT}/"
                )
            )

        except Exception as error:

            messagebox.showerror(
                "Preview failed",
                str(error)
            )

    # ========================================================
    # PUBLISH
    # ========================================================

    def publish(self):

        if not messagebox.askyesno(
            "Publish",
            (
                "Generate the site and push "
                "all current changes to GitHub?"
            )
        ):

            return

        try:

            # Save forms currently visible in CMS.
            self.save_main_pages()

            # Build all HTML.
            generator.generate_all()

            # Confirm this really is a Git repository.
            result = run_git(
                "rev-parse",
                "--is-inside-work-tree"
            )

            if result.returncode != 0:

                raise RuntimeError(
                    "This folder is not a Git repository."
                )

            # Stage everything.
            result = run_git(
                "add",
                "."
            )

            if result.returncode != 0:

                raise RuntimeError(
                    result.stderr
                    or "git add failed."
                )

            # Check whether anything changed.
            status = run_git(
                "status",
                "--porcelain"
            )

            if status.returncode != 0:

                raise RuntimeError(
                    status.stderr
                    or "git status failed."
                )

            if not status.stdout.strip():

                messagebox.showinfo(
                    "Publish",
                    (
                        "Nothing changed.\n\n"
                        "The site is already "
                        "up to date."
                    )
                )

                return

            # Commit.
            result = run_git(
                "commit",
                "-m",
                "Update website"
            )

            if result.returncode != 0:

                raise RuntimeError(
                    result.stderr
                    or result.stdout
                    or "git commit failed."
                )

            # Push using existing Git credentials.
            result = run_git(
                "push"
            )

            if result.returncode != 0:

                raise RuntimeError(
                    result.stderr
                    or result.stdout
                    or "git push failed."
                )

            messagebox.showinfo(
                "Published",
                (
                    "Website pushed "
                    "successfully.\n\n"
                    "GitHub Pages will update "
                    "after GitHub finishes "
                    "deploying it."
                )
            )

        except FileNotFoundError:

            messagebox.showerror(
                "Git not found",
                (
                    "Git could not be found.\n\n"
                    "Make sure Git is installed "
                    "and available from PowerShell."
                )
            )

        except Exception as error:

            messagebox.showerror(
                "Publish failed",
                str(error)
            )

    # ========================================================
    # BOTTOM BAR
    # ========================================================

    def build_bottom_bar(self):

        bar = ttk.Frame(self)

        bar.pack(
            fill="x",
            padx=10,
            pady=(0, 10)
        )

        ttk.Button(
            bar,
            text="GENERATE ALL",
            command=self.generate_all
        ).pack(
            side="left"
        )

        ttk.Button(
            bar,
            text="PREVIEW SITE",
            command=self.preview
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            bar,
            text="PUBLISH",
            command=self.publish
        ).pack(
            side="right"
        )

    # ========================================================
    # CLOSE
    # ========================================================

    def close_manager(self):

        global preview_server

        if preview_server:

            try:
                preview_server.shutdown()
            except Exception:
                pass

        self.destroy()


if __name__ == "__main__":

    app = SiteManager()
    app.mainloop()