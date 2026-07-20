#!/usr/bin/env python3
"""Generate index.html (en) and zh/index.html from data/{locale}/*.json."""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SHARED = DATA / "shared.json"
PUBLICATIONS = DATA / "publications.json"
TEMPLATE = ROOT / "templates" / "base.html"

LOCALES = {
    "en": {
        "output": ROOT / "index.html",
        "asset_prefix": "",
    },
    "zh": {
        "output": ROOT / "zh" / "index.html",
        "asset_prefix": "../",
    },
}

UI_DEFAULTS = {
    "skip_link": "Skip to content",
    "nav_toggle": "Open menu",
    "nav_aria": "Main navigation",
    "lang_switch_aria": "Language switcher",
    "lang_current": "EN",
    "lang_other": "中文",
    "lang_other_href": "zh/",
    "alternate_hreflang": "zh-CN",
    "alternate_href": "zh/",
    "download_cv": "Download CV",
    "send_email": "Email Me",
    "social_aria": "Social links",
    "photo_alt_suffix": "profile photo",
    "footer_rights": "All rights reserved.",
    "footer_hosted": "",
    "footer_updated": "Last updated",
}

SECTION_TITLES = {
    "about": ("关于我", "About Me"),
    "research": ("研究兴趣", "Research Interests"),
    "publications": ("发表论文", "Publications"),
    "projects": ("项目与开源", "Projects & Open Source"),
    "teaching": ("教学与服务", "Teaching & Service"),
    "contact": ("联系我", "Contact"),
    "games": ("趣味小游戏", "Mini Games"),
}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_json_optional(path: Path) -> dict | None:
    if not path.is_file():
        return None
    return load_json(path)


def deep_merge(base: dict, override: dict) -> dict:
    merged = base.copy()
    for key, value in override.items():
        if (
            key in merged
            and isinstance(merged[key], dict)
            and isinstance(value, dict)
        ):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_site(locale: str) -> dict:
    site = load_json(DATA / locale / "site.json")
    shared = load_json_optional(SHARED)
    if shared:
        site = deep_merge(shared, site)
    return site


def load_publications() -> dict | None:
    return load_json_optional(PUBLICATIONS)


def format_authors(authors: list[dict]) -> str:
    parts: list[str] = []
    for author in authors:
        name = html.escape(author["name"])
        if author.get("me"):
            name = f"<strong>{name}</strong>"
        if author.get("equal"):
            name += "<sup>†</sup>"
        if author.get("corresponding"):
            name += "<sup>*</sup>"
        parts.append(name)
    return ", ".join(parts)


def item_visible(item: dict, *required_keys: str) -> bool:
    if item.get("enabled") is False:
        return False
    for key in required_keys:
        value = item.get(key)
        if value is None:
            return False
        if isinstance(value, str) and not value.strip():
            return False
    return True


def visible_items(items: list[dict] | None, *required_keys: str) -> list[dict]:
    if not items:
        return []
    return [item for item in items if item_visible(item, *required_keys)]


def ui_value(ui: dict, key: str) -> str:
    return ui.get(key) or UI_DEFAULTS.get(key, "")


def asset_url(path: str, prefix: str) -> str:
    return html.escape(f"{prefix}{path}")


def external_link(url: str) -> str:
    if url.startswith("http") or url.startswith("mailto:"):
        return ' target="_blank" rel="noopener"' if url.startswith("http") else ""
    return ""


def has_list_items(section: dict | None, *required_keys: str) -> bool:
    return bool(section and visible_items(section.get("items"), *required_keys))


def has_about(section: dict | None) -> bool:
    if not section:
        return False
    paragraphs = [p for p in section.get("paragraphs") or [] if str(p).strip()]
    info = visible_items(section.get("info"), "label", "value")
    return bool(paragraphs or info)


def has_publications(data: dict | None) -> bool:
    if not data:
        return False
    for group in data.get("groups", []):
        if group.get("papers"):
            return True
    return False


def has_projects(data: dict | None) -> bool:
    return bool(data and data.get("items"))


def has_contact(section: dict | None) -> bool:
    if not section:
        return False
    return bool(
        section.get("intro")
        or section.get("items")
        or (section.get("location") and section["location"].get("name"))
    )


def has_games(site: dict) -> bool:
    section = site.get("games_section")
    if not section or section.get("enabled") is False:
        return False
    return bool(visible_items(section.get("items"), "id", "title"))


def visible_sections(site: dict, publications: dict | None, projects: dict | None) -> set[str]:
    visible: set[str] = set()
    if has_about(site.get("about")):
        visible.add("about")
    if has_list_items(site.get("research"), "title", "description"):
        visible.add("research")
    if has_publications(publications):
        visible.add("publications")
    if has_projects(projects):
        visible.add("projects")
    if has_list_items(site.get("teaching"), "date", "role", "detail"):
        visible.add("teaching")
    if has_contact(site.get("contact")):
        visible.add("contact")
    if has_games(site):
        visible.add("games")
    return visible


def section_title(site: dict, section_id: str, locale: str) -> str:
    key_map = {
        "about": "about",
        "research": "research",
        "publications": "publications_section",
        "projects": "projects_section",
        "teaching": "teaching",
        "contact": "contact",
        "games": "games_section",
    }
    config_key = key_map[section_id]
    section = site.get(config_key) or site.get(section_id)
    if section and section.get("title"):
        return section["title"]
    defaults = SECTION_TITLES.get(section_id, ("", ""))
    return defaults[0] if locale == "zh" else defaults[1]


def render_info_value(item: dict) -> str:
    value = html.escape(item["value"])
    if item.get("type") == "email":
        return f'<a href="mailto:{value}">{value}</a>'
    return f"<span>{value}</span>"


def render_nav(nav: list[dict], visible: set[str]) -> str:
    items = [
        item for item in nav
        if item_visible(item, "id", "label") and item["id"] in visible
    ]
    if not items:
        return ""
    lines = "\n".join(
        f'          <li><a href="#{html.escape(item["id"])}">{html.escape(item["label"])}</a></li>'
        for item in items
    )
    return f"""      <nav class="site-nav" aria-label="{{nav_aria}}">
        <ul>
{lines}
        </ul>
      </nav>"""


def render_lang_switch(ui: dict) -> str | None:
    required = ("lang_current", "lang_other", "lang_other_href", "alternate_hreflang")
    if not all(ui.get(key) for key in required):
        return None
    return f"""  <div class="lang-switch-bar">
    <div class="lang-switch" aria-label="{html.escape(ui_value(ui, "lang_switch_aria"))}">
      <span class="lang-switch-current" aria-current="true">{html.escape(ui["lang_current"])}</span>
      <span class="lang-switch-sep" aria-hidden="true">|</span>
      <a class="lang-switch-link" href="{html.escape(ui["lang_other_href"])}" hreflang="{html.escape(ui["alternate_hreflang"])}" rel="alternate">{html.escape(ui["lang_other"])}</a>
    </div>
  </div>"""


def render_alternate_link(ui: dict) -> str:
    hreflang = ui.get("alternate_hreflang")
    href = ui.get("alternate_href")
    if not hreflang or not href:
        return ""
    return f'  <link rel="alternate" hreflang="{html.escape(hreflang)}" href="{html.escape(href)}">'


def render_social(social: list[dict], social_aria: str) -> str:
    entries = visible_items(social, "label", "url")
    if not entries:
        return ""
    items = "\n".join(
        f'            <li><a href="{html.escape(item["url"])}"{external_link(item["url"])} '
        f'aria-label="{html.escape(item.get("aria", item["label"]))}">{html.escape(item["label"])}</a></li>'
        for item in entries
    )
    return f'          <ul class="social-links" aria-label="{html.escape(social_aria)}">\n{items}\n          </ul>'


def render_affiliation(affiliation: dict) -> str:
    university = affiliation.get("university")
    department = affiliation.get("department")
    if not university and not department:
        return ""

    parts: list[str] = []
    if university:
        uni_html = html.escape(university)
        url = affiliation.get("university_url")
        if url:
            uni_html = (
                f'<a href="{html.escape(url)}" target="_blank" rel="noopener">{uni_html}</a>'
            )
        parts.append(uni_html)
    if department:
        parts.append(html.escape(department))

    return f'          <p class="hero-affiliation">\n            {" · ".join(parts)}\n          </p>'


def render_hero(site: dict, ui: dict, prefix: str) -> str:
    profile = site.get("profile") or {}
    name = profile.get("name")
    if not name:
        return ""

    blocks: list[str] = []

    if profile.get("photo"):
        photo_alt = f'{name} {ui_value(ui, "photo_alt_suffix")}'.strip()
        blocks.append(
            f"""        <figure class="hero-photo">
          <img src="{asset_url(profile["photo"], prefix)}" alt="{html.escape(photo_alt)}" width="320" height="320">
        </figure>"""
        )

    content: list[str] = []
    if profile.get("title"):
        content.append(f'          <p class="hero-label">{html.escape(profile["title"])}</p>')
    content.append(f"          <h1>{html.escape(name)}</h1>")

    affiliation = site.get("affiliation")
    if affiliation:
        aff_html = render_affiliation(affiliation)
        if aff_html:
            content.append(aff_html)

    if profile.get("bio"):
        content.append(f'          <p class="hero-bio">{html.escape(profile["bio"])}</p>')

    social: list[dict] = list(site.get("social") or [])
    if profile.get("email"):
        social.append(
            {
                "label": "Email",
                "url": f"mailto:{profile['email']}",
                "aria": "Email",
            }
        )
    if social:
        social_html = render_social(social, ui_value(ui, "social_aria"))
        if social_html:
            content.append(social_html)

    blocks.append(
        "        <div class=\"hero-content\">\n"
        + "\n".join(content)
        + "\n        </div>"
    )

    return f"""    <section class="hero">
      <div class="container hero-grid">
{chr(10).join(blocks)}
      </div>
    </section>"""


def render_about(about: dict) -> str:
    parts: list[str] = []
    paragraphs = [p for p in about.get("paragraphs") or [] if str(p).strip()]
    if paragraphs:
        para_html = "\n".join(f"          <p>{p}</p>" for p in paragraphs)
        parts.append(f"        <div class=\"prose\">\n{para_html}\n        </div>")

    info = visible_items(about.get("info"), "label", "value")
    if info:
        cards = "\n".join(
            f"""          <li>
            <span class="info-label">{html.escape(item["label"])}</span>
            {render_info_value(item)}
          </li>"""
            for item in info
        )
        if cards:
            parts.append(f"        <ul class=\"info-cards\">\n{cards}\n        </ul>")

    return "\n".join(parts)


def render_games(site: dict) -> str:
    section = site.get("games_section") or {}
    items = visible_items(section.get("items"), "id", "title")
    if not items:
        return ""

    parts: list[str] = []
    intro = section.get("intro")
    if intro and str(intro).strip():
        parts.append(f'        <p class="games-intro">{html.escape(intro)}</p>')

    cards: list[str] = []
    for item in items:
        desc = item.get("description") or item.get("desc") or ""
        desc_html = (
            f'          <p class="game-desc">{html.escape(desc)}</p>\n'
            if desc
            else ""
        )
        cards.append(
            f"""          <article class="game-card">
            <h3>{html.escape(item["title"])}</h3>
{desc_html}          <div class="game-panel" data-game="{html.escape(item["id"])}"></div>
          </article>"""
        )

    parts.append(f"        <div class=\"games-grid\">\n" + "\n".join(cards) + "\n        </div>")
    return "\n".join(parts)


def render_research(research: dict) -> str:
    items = visible_items(research.get("items"), "title", "description")
    cards = "\n".join(
        f"""          <article class="research-card">
            <h3>{html.escape(item["title"])}</h3>
            <p>{html.escape(item["description"])}</p>
          </article>"""
        for item in items
    )
    if not cards:
        return ""
    return f"        <div class=\"research-grid\">\n{cards}\n        </div>"


def render_paper_figure(paper: dict, asset_prefix: str) -> str:
    figure = paper.get("figure")
    if not figure or not figure.get("src"):
        return ""

    src = asset_url(figure["src"], asset_prefix)
    alt = html.escape(figure.get("alt") or paper.get("title", ""))
    img = f'<img src="{src}" alt="{alt}" loading="lazy" width="240" height="135">'

    link = figure.get("link")
    if link:
        inner = f'<a href="{html.escape(link)}" target="_blank" rel="noopener">{img}</a>'
    else:
        inner = img

    return f"""            <figure class="pub-figure">
              {inner}
            </figure>"""


def render_publications(
    section: dict | None, publications: dict, asset_prefix: str
) -> str:
    blocks: list[str] = []
    for group in publications.get("groups", []):
        papers = group.get("papers") or []
        if not papers:
            continue

        papers_html: list[str] = []
        for paper in papers:
            if not paper.get("title"):
                continue

            links = "\n              ".join(
                f'<a href="{html.escape(link["url"])}"{external_link(link["url"])}>'
                f'{html.escape(link["label"])}</a>'
                for link in visible_items(paper.get("links"), "label", "url")
            )

            body_parts = [f"""            <p class="pub-title">
              <strong>{html.escape(paper["title"])}</strong>
            </p>"""]

            if paper.get("authors"):
                body_parts.append(
                    f"""            <p class="pub-authors">
              {format_authors(paper["authors"])}
            </p>"""
                )

            if paper.get("venue") and paper.get("year") is not None:
                body_parts.append(
                    f"""            <p class="pub-venue">
              <em>{html.escape(paper["venue"])}</em>, {paper["year"]}.
            </p>"""
                )

            if links:
                body_parts.append(f"            <p class=\"pub-links\">\n              {links}\n            </p>")

            body = "\n".join(body_parts)
            figure_html = render_paper_figure(paper, asset_prefix)

            if figure_html:
                papers_html.append(
                    f"""          <li class="pub-item pub-item--has-figure">
{figure_html}
            <div class="pub-body">
{body}
            </div>
          </li>"""
                )
            else:
                papers_html.append(
                    f"""          <li class="pub-item">
{body}
          </li>"""
                )

        if papers_html:
            year = group.get("year", "")
            blocks.append(
                f"""        <h3 class="pub-year">{year}</h3>
        <ol class="pub-list">
{chr(10).join(papers_html)}
        </ol>"""
            )

    if not blocks:
        return ""

    note = (section or {}).get("note")
    note_html = f'        <p class="section-note">\n          {note}\n        </p>\n\n' if note else ""
    return note_html + "\n".join(blocks)


def render_projects(projects: dict) -> str:
    items = visible_items(projects.get("items"), "name")
    cards = "\n".join(
        f"""          <article class="project-card">
            <h3>{f'<a href="{html.escape(item["url"])}" target="_blank" rel="noopener">{html.escape(item["name"])}</a>' if item.get("url") else html.escape(item["name"])}</h3>
            {f'<p>{html.escape(item["description"])}</p>' if item.get("description") else ""}
            {f'<p class="project-tags">{"".join(f"<span>{html.escape(tag)}</span>" for tag in item.get("tags", []))}</p>' if item.get("tags") else ""}
          </article>"""
        for item in items
    )
    if not cards:
        return ""
    return f"        <div class=\"project-grid\">\n{cards}\n        </div>"


def render_teaching(teaching: dict) -> str:
    items = visible_items(teaching.get("items"), "date", "role", "detail")
    lines = "\n".join(
        f"""          <li>
            <span class="timeline-date">{html.escape(item["date"])}</span>
            <div>
              <strong>{html.escape(item["role"])}</strong> — {html.escape(item["detail"])}
            </div>
          </li>"""
        for item in items
    )
    if not lines:
        return ""
    return f"        <ul class=\"timeline\">\n{lines}\n        </ul>"


def render_contact(contact: dict) -> str:
    parts: list[str] = []
    intro = contact.get("intro")
    items = contact.get("items") or []
    location = contact.get("location") or {}

    item_lines = "\n".join(
        f"""              <li>
                <span>{html.escape(item["label"])}</span>
                {render_info_value(item) if item.get("type") == "email" else f"<span>{html.escape(item['value'])}</span>"}
              </li>"""
        for item in visible_items(items, "label", "value")
    )

    left_parts: list[str] = []
    if intro:
        left_parts.append(f"            <p>{html.escape(intro)}</p>")
    if item_lines:
        left_parts.append(f"            <ul class=\"contact-list\">\n{item_lines}\n            </ul>")

    if left_parts:
        parts.append(
            "          <div>\n"
            + "\n".join(left_parts)
            + "\n          </div>"
        )

    if location.get("name") or location.get("address"):
        parts.append(
            f"""          <div class="contact-map">
            {f'<p class="contact-map-label">{html.escape(location["name"])}</p>' if location.get("name") else ""}
            {f'<p>{html.escape(location["address"])}</p>' if location.get("address") else ""}
          </div>"""
        )

    if not parts:
        return ""

    return f"        <div class=\"contact-grid\">\n{chr(10).join(parts)}\n        </div>"


def wrap_section(section_id: str, title: str, content: str, alt: bool) -> str:
    alt_class = " section-alt" if alt else ""
    return f"""    <section id="{section_id}" class="section{alt_class}">
      <div class="container">
        <h2 class="section-title">{html.escape(title)}</h2>
{content}
      </div>
    </section>"""


def build_main_sections(
    site: dict,
    publications: dict | None,
    projects: dict | None,
    prefix: str,
    locale: str,
) -> str:
    sections: list[str] = []

    hero = render_hero(site, site.get("ui") or {}, prefix)
    if hero:
        sections.append(hero)

    body_sections: list[tuple[str, str]] = []

    about = site.get("about")
    if has_about(about):
        content = render_about(about)
        if content:
            body_sections.append(("about", content))

    research = site.get("research")
    if has_list_items(research, "title", "description"):
        content = render_research(research)
        if content:
            body_sections.append(("research", content))

    if has_publications(publications):
        content = render_publications(
            site.get("publications_section"),
            publications,
            prefix,
        )
        if content:
            body_sections.append(("publications", content))

    if has_projects(projects):
        content = render_projects(projects)
        if content:
            body_sections.append(("projects", content))

    teaching = site.get("teaching")
    if has_list_items(teaching, "date", "role", "detail"):
        content = render_teaching(teaching)
        if content:
            body_sections.append(("teaching", content))

    contact = site.get("contact")
    if has_contact(contact):
        content = render_contact(contact)
        if content:
            body_sections.append(("contact", content))

    if has_games(site):
        content = render_games(site)
        if content:
            body_sections.append(("games", content))

    for index, (section_id, content) in enumerate(body_sections):
        alt = index % 2 == 1
        title = section_title(site, section_id, locale)
        sections.append(wrap_section(section_id, title, content, alt))

    return "\n\n".join(sections)


def build_locale(locale: str, config: dict) -> None:
    locale_dir = DATA / locale
    site_path = locale_dir / "site.json"
    if not site_path.is_file():
        print(f"Skip {locale}: missing {site_path.relative_to(ROOT)}", file=sys.stderr)
        return

    site = load_site(locale)
    publications = load_publications()
    projects = load_json_optional(locale_dir / "projects.json")

    profile = site.get("profile") or {}
    meta = site.get("meta") or {}
    ui = {**UI_DEFAULTS, **(site.get("ui") or {})}
    prefix = config["asset_prefix"]
    name = profile.get("name", "Academic Homepage")

    visible = visible_sections(site, publications, projects)
    nav_template = render_nav(site.get("nav") or [], visible)
    nav_block = nav_template.replace("{nav_aria}", html.escape(ui_value(ui, "nav_aria"))) if nav_template else ""

    lang_switch = render_lang_switch(ui)
    footer_parts: list[str] = []
    if ui.get("footer_hosted"):
        footer_parts.append(f"        {ui['footer_hosted']}")
    if meta.get("last_updated"):
        footer_parts.append(
            f'        {html.escape(ui_value(ui, "footer_updated"))}：'
            f'<time datetime="{html.escape(meta["last_updated"])}">'
            f'{html.escape(meta["last_updated"])}</time>'
        )
    footer_note_block = (
        f'      <p class="footer-note">\n' + "\n".join(footer_parts) + "\n      </p>"
        if footer_parts
        else ""
    )

    template = TEMPLATE.read_text(encoding="utf-8")
    output = template.format(
        lang=html.escape(meta.get("lang", locale)),
        title=html.escape(meta.get("title", name)),
        description=html.escape(meta.get("description", name)),
        alternate_link=render_alternate_link(ui),
        asset_prefix=prefix,
        skip_link=html.escape(ui_value(ui, "skip_link")),
        nav_toggle=html.escape(ui_value(ui, "nav_toggle")),
        lang_switch_bar=lang_switch or "",
        name=html.escape(name),
        nav_block=nav_block,
        main_sections=build_main_sections(site, publications, projects, prefix, locale),
        footer_rights=html.escape(ui_value(ui, "footer_rights")),
        footer_note_block=footer_note_block,
    )

    out_path = config["output"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(output, encoding="utf-8")
    print(f"Built {out_path.relative_to(ROOT)}")


def cleanup_stale_outputs() -> None:
    stale = ROOT / "en" / "index.html"
    if stale.is_file():
        stale.unlink()
        print(f"Removed stale {stale.relative_to(ROOT)}")


def build() -> None:
    for locale, config in LOCALES.items():
        build_locale(locale, config)
    cleanup_stale_outputs()


if __name__ == "__main__":
    try:
        build()
    except json.JSONDecodeError as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        sys.exit(1)
