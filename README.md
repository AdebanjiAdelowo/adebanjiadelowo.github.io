# adebanjiadelowo.github.io

Source for my personal website, published via GitHub Pages at
[adebanjiadelowo.github.io](https://adebanjiadelowo.github.io/).

The site presents my work as an applied mathematician and machine learning
researcher, covering PDEs, numerical methods, inverse problems, and
scientific/engineering ML systems.

## Structure

```
adebanjiadelowo.github.io/
├── index.html              Landing page
├── projects.html           Project portfolio
├── research.html           Research interests
├── research-outputs.html   Papers, reports, and thesis writeups
├── experience.html         Professional experience
├── education.html          Education
├── skills.html             Technical skills
├── contact.html            Contact page
├── assets/
│   ├── css/site.css        Site styling
│   └── js/nav.js           Navigation behaviour
└── images/                 Project and profile images, by project
```

Plain HTML, CSS, and JavaScript are served directly by GitHub Pages. Individual
case studies live in `projects/`. Shared layout is in `templates/base.html`; editable
page content and project summaries are in `content/`. After editing these sources,
regenerate and check the published HTML with Python (no external dependencies):

```bash
python3 scripts/build.py
python3 scripts/build.py --check
python3 scripts/check_site.py
```

## Local preview

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000` in a browser.

## License

Site content and code are personal work; not licensed for reuse.
