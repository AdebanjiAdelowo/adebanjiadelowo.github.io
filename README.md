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
├── physicsnemo.html        Five ongoing PhysicsNeMo studies and interim results
├── research-outputs.html   Papers, reports, and thesis writeups
├── experience.html         Professional experience
├── education.html          Education
├── skills.html             Technical skills
├── cv.html                 CV downloads
├── contact.html            Contact page
├── assets/
│   ├── css/site.css        Site styling
│   └── js/nav.js           Navigation behaviour
├── downloads/cv/           Industry CV PDF, academic CV PDF and its LaTeX source
└── images/                 Project and profile images, by project
```

`cv.pdf`, `downloads/Academic_CV_Adelowo.pdf` and
`downloads/Adebanji_Adelowo_CV_ML_Data_Science.pdf` are byte-identical copies kept
so that older links keep working; the link check fails if they drift from
`downloads/cv/`.

Plain HTML, CSS, and JavaScript are served directly by GitHub Pages. Individual
case studies live in `projects/`. Shared layout is in `templates/base.html`; editable
page content and project summaries are in `content/`. After editing these sources,
regenerate and check the published HTML with Python (no external dependencies):

```bash
python3 scripts/build.py
python3 scripts/build.py --check
python3 scripts/check_site.py
python3 scripts/test_check_links.py
python3 scripts/check_links.py              # local links, assets and downloads
python3 scripts/check_links.py --external   # also request external URLs, signed out
```

`check_links.py` checks every `href`, `src`, `srcset` and CSS `url()` reference
with exact filename case, validates the CV downloads, and rejects links into
private repositories. With `--external` it requests each external URL without
credentials, as an ordinary visitor would, and separates confirmed broken links
(which fail the check) from timeouts and sites that refuse automated clients
(which are reported as warnings). `--live BASE_URL` checks a deployed copy.

## Local preview

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000` in a browser.

## License

Site content and code are personal work; not licensed for reuse.

## Publishing

`main` is the default and production branch. Every push to `main` runs
`.github/workflows/site-checks.yml`: it rebuilds and validates the pages, runs
the link audit and the layout tests, and deploys to GitHub Pages only if all of
them pass. After deployment it checks the live site, including the CV downloads.
The same checks run weekly to catch external links that stop working. The older
`master` branch holds a previous blog and is kept for reference only.

Edit the sources in `content/`, `templates/` and `scripts/build.py`, then
regenerate the published pages before committing.
