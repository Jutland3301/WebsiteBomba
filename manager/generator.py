from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
PROJECT_CONTENT = CONTENT / "projects"

PROJECT_OUTPUT = ROOT / "projects"


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


def paragraphs(text: str) -> str:
    blocks = []

    for block in text.split("\n\n"):
        block = block.strip()

        if not block:
            continue

        escaped = html.escape(block).replace("\n", "<br>")
        blocks.append(f"<p>{escaped}</p>")

    return "\n".join(blocks)


def page_start(title: str, active: str) -> str:

    links = []

    for name, href in [
        ("HOME", "index.html"),
        ("ABOUT", "about.html"),
        ("PROJECTS", "projects.html"),
    ]:
        links.append(f'<a href="{href}">{name}</a>')

    return f"""<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>{html.escape(title)}</title>

    <link rel="stylesheet" href="css/style.css?v=3">
</head>

<body>

<header>
    <h1 class="site-title">personal website</h1>

    <p class="site-subtitle">
        notes / projects / miscellaneous things
    </p>
<button id="audio-button"
        class="bgm-button"
        type="button"
        title="BGM ON / OFF">

    <img id="audio-icon"
         src="images/speaker.png"
         alt="BGM ON">

</button>
</header>

<nav>
    {' '.join(links)}
</nav>

<main>
"""


def page_end(audio_name: str) -> str:
    return f"""
    <audio id="bgm" loop autoplay>
    <source src="audio/{audio_name}"
            type="audio/mpeg">
    </audio>

</main>

<footer>
    personal website
</footer>

<script src="js/audio.js"></script>

</body>
</html>
"""

def generate_home() -> None:

    data = load_json(CONTENT / "home.json")

    left_image = ""

    if data.get("left_image"):
        left_image = f"""
        <div class="home-side-image">
            <img
                class="blink-image"
                src="{html.escape(data["left_image"])}"
                alt="left image"
                data-blink="{str(data.get("blink_enabled", False)).lower()}"
                data-visible="{data.get("blink_visible_seconds", 2)}"
                data-hidden="{data.get("blink_hidden_seconds", 1)}">
        </div>
"""

    right_image = ""

    if data.get("right_image"):
        right_image = f"""
        <div class="home-side-image">
            <img
                class="blink-image"
                src="{html.escape(data["right_image"])}"
                alt="right image"
                data-blink="{str(data.get("blink_enabled", False)).lower()}"
                data-visible="{data.get("blink_visible_seconds", 2)}"
                data-hidden="{data.get("blink_hidden_seconds", 1)}">
        </div>
"""

    # IMPORTANT: output must be created before output +=
    output = page_start("Home", "HOME")
    
    output += """
    <div id="entrance-screen" class="entrance-screen">

        <div class="entrance-box">

            <div class="entrance-title">
                WEBSITE BOMBA
            </div>

            <button id="entrance-button"
                    class="entrance-button"
                    type="button">
                ENTER
            </button>

            <div class="entrance-note">
                sound will play
            </div>

        </div>

    </div>
"""

    output += f"""
    <div class="outside-image outside-image-left">
        {left_image}
    </div>

    <div class="outside-image outside-image-right">
        {right_image}
    </div>

    <h2 class="page-heading">HOME</h2>

    <article class="entry">

        <div class="entry-date">
            {html.escape(data.get("date", ""))}
        </div>

        <h3 class="entry-title">
            {html.escape(data.get("title", ""))}
        </h3>

        {paragraphs(data.get("body", ""))}

    </article>

    <hr>

    <div class="small">
        last updated:
        {html.escape(data.get("last_updated", ""))}
    </div>
"""

    output += page_end("home.mp3")

    output = output.replace(
        "</body>",
        '<script src="js/blink.js"></script>\n'
        '<script src="js/entrance.js"></script>\n'
        '</body>'
    )

    (ROOT / "index.html").write_text(
        output,
        encoding="utf-8"
    )

def generate_about() -> None:

    data = load_json(CONTENT / "about.json")

    image = ""

    if data.get("image"):
        image = (
            f'<img src="{html.escape(data["image"])}" '
            f'alt="about image">'
        )

    github = ""

    if data.get("github"):
        github = f"""
        <p>
            GitHub:
            <a href="{html.escape(data["github"])}">
                {html.escape(data["github"])}
            </a>
        </p>
"""

    email = ""

    if data.get("email"):
        address = html.escape(data["email"])

        email = f"""
        <p>
            Email:
            <a href="mailto:{address}">
                {address}
            </a>
        </p>
"""

    output = page_start("About", "ABOUT")

    output += f"""
    <h2 class="page-heading">ABOUT</h2>

    <article class="entry">

        <h3 class="entry-title">
            {html.escape(data.get("title", ""))}
        </h3>

        {image}

        {paragraphs(data.get("body", ""))}

        <hr>

        <h3 class="entry-title">
            Interests
        </h3>

        <p>
            {html.escape(data.get("interests", ""))}
        </p>

        <hr>

        <h3 class="entry-title">
            Contact
        </h3>

        {github}
        {email}

    </article>
"""

    output += page_end("about.mp3")

    (ROOT / "about.html").write_text(
        output,
        encoding="utf-8"
    )


def generate_projects() -> None:

    data = load_json(CONTENT / "projects.json")

    items = []

    for project in data.get("projects", []):

        slug = html.escape(project.get("slug", ""))
        title = html.escape(project.get("title", ""))
        date = html.escape(project.get("date", ""))
        description = html.escape(
            project.get("description", "")
        )

        image = project.get("image", "")

        image_html = ""

        if image:
            image_html = f"""
        <a href="projects/{slug}.html"
           class="project-image-link">

            <img src="{html.escape(image)}"
                 alt="{title}"
                 class="project-thumbnail">

        </a>
"""

        items.append(f"""
    <article class="project-item">

        {image_html}

        <div class="project-info">

            <div class="entry-date">
                {date}
            </div>

            <h3 class="project-title">
                <a href="projects/{slug}.html">
                    {title}
                </a>
            </h3>

            <p>
                {description}
            </p>

        </div>

    </article>
""")

    output = page_start("Projects", "PROJECTS")

    output += """
    <h2 class="page-heading">PROJECTS</h2>

    <p class="small">
        projects / experiments / unfinished things
    </p>
"""

    output += "\n".join(items)

    output += page_end("projects.mp3")

    (ROOT / "projects.html").write_text(
        output,
        encoding="utf-8"
    )


def generate_project_pages() -> None:

    PROJECT_OUTPUT.mkdir(exist_ok=True)

    index = load_json(CONTENT / "projects.json")

    for project in index.get("projects", []):

        slug = project.get("slug")

        if not slug:
            continue

        source = PROJECT_CONTENT / f"{slug}.json"

        if not source.exists():
            continue

        data = load_json(source)

        title = html.escape(data.get("title", ""))
        date = html.escape(data.get("date", ""))
        status = html.escape(data.get("status", ""))
        body = paragraphs(data.get("body", ""))

        image_html = ""

        if data.get("image"):
            image_html = (
                f'<img src="../{html.escape(data["image"])}" '
                f'alt="{title}">'
            )

        github_html = ""

        if data.get("github"):
            github_html = f"""
        <p>
            <a href="{html.escape(data["github"])}">
                GitHub repository
            </a>
        </p>
"""

        output = f"""<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>{title}</title>

    <link rel="stylesheet"
          href="../css/style.css">
</head>

<body>

<header>
    <h1 class="site-title">personal website</h1>

    <p class="site-subtitle">
        notes / projects / miscellaneous things
    </p>
</header>

<nav>
    <a href="../index.html">HOME</a>
    <a href="../about.html">ABOUT</a>
    <a href="../projects.html">PROJECTS</a>
</nav>

<main>

    <h2 class="page-heading">PROJECT</h2>

    <article class="entry">

        <div class="entry-date">
            {date}
        </div>

        <h3 class="entry-title">
            {title}
        </h3>

        <p class="small">
            status: {status}
        </p>

        {image_html}

        {body}

        {github_html}

        <hr>

        <p>
            <a href="../projects.html">
                &lt;&lt; back to projects
            </a>
        </p>

    </article>

    <div class="audio-control">

        BGM:

        <button id="audio-button">
            PLAY
        </button>

        <audio id="bgm" loop>
            <source src="../audio/projects.mp3"
                    type="audio/mpeg">
        </audio>

    </div>

</main>

<footer>
    personal website
</footer>

<script src="../js/audio.js"></script>

</body>
</html>
"""

        destination = PROJECT_OUTPUT / f"{slug}.html"

        destination.write_text(
            output,
            encoding="utf-8"
        )


def generate_all() -> None:
    generate_home()
    generate_about()
    generate_projects()
    generate_project_pages()


if __name__ == "__main__":
    generate_all()

    print("Site generated successfully.")