"""Render the static portfolio from shared templates and editable content.

Run `python3 scripts/build.py` after editing content or templates.
Run `python3 scripts/build.py --check` to verify generated files are current.
No third-party dependencies are required. GitHub Pages serves the generated HTML.
"""
from pathlib import Path
from html import escape
import argparse
import json
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://adebanjiadelowo.github.io/'
PROJECTS = json.loads((ROOT/'content/projects.json').read_text())
BY_SLUG = {p['slug']: p for p in PROJECTS}
SIZES = json.loads((ROOT/'content/image-sizes.json').read_text())
TEMPLATE = (ROOT/'templates/base.html').read_text()

def image(path, alt, cls='', lazy=True):
    dimensions = SIZES.get(path)
    size = f' width="{dimensions[0]}" height="{dimensions[1]}"' if dimensions else ''
    loading = ' loading="lazy"' if lazy else ''
    return f'<img src="./{path}" alt="{escape(alt)}" class="{cls}"{size}{loading} decoding="async">'

def status_line(p):
    badge = p.get('badge')
    label = f'<span class="status-badge status-{badge.lower().replace(" ", "-")}">{escape(badge)}</span>' if badge else ''
    return f'<p class="project-status">{label}{escape(p["status"])}</p>'

def card(p, featured=False):
    illustration = ''
    if featured and p['image']:
        label = {'navier-stokes': 'Full-order vorticity at t = 3', 'darcy': 'Reconstructed log permeability', 'topology-optimization': 'Optimised material layout'}.get(p['slug'], p['image_caption'])
        illustration = f'<div class="card-visual"><div class="thumbnail thumbnail-{p["slug"]}">{image(p["image"], label)}</div><p class="thumbnail-caption">{label}</p></div>'
    elif p['image']:
        illustration = f'<a class="project-preview" href="./projects/{p["slug"]}.html">{image(p["image"], p["image_alt"])}<span>{escape(p["image_caption"])}</span></a>'
    return f'''<article class="project-card{' featured-card' if featured else ''}" id="{p['slug']}" data-group="{p['group']}">
    {illustration}<div class="card-body"><p class="eyebrow">{escape(p['category'])}</p>
    <h3><a href="./projects/{p['slug']}.html">{escape(p['title'])}</a></h3>
    <p class="card-purpose">{escape(p['purpose'])}</p><p>{escape(p.get('summary', p['result']))}</p><a class="section-link" href="./projects/{p['slug']}.html" aria-label="Read case study: {escape(p['title'])}">Read case study →</a></div></article>'''

def order_project_lists(content):
    ranks = {p['slug']: i for i, p in enumerate(PROJECTS)}
    urls = {p['code'].rstrip('/'): p['slug'] for p in PROJECTS}
    def reorder(match):
        items = re.findall(r'<li\b[^>]*>.*?</li>', match.group(2), re.S)
        def priority(item):
            local = re.search(r'href="\./projects/([^"/]+)\.html"', item)
            if local:
                return ranks.get(local.group(1), len(ranks))
            external = re.search(r'href="([^"]+)"', item)
            return ranks.get(urls.get(external.group(1).rstrip('/'), ''), len(ranks)) if external else len(ranks)
        return match.group(1) + '\n' + '\n'.join(sorted(items, key=priority)) + '\n</ul>'
    return re.sub(r'(<ul[^>]*class="[^"]*\bproject-order\b[^"]*"[^>]*>)(.*?)</ul>', reorder, content, flags=re.S)

def visual_gallery(slugs):
    items=[]
    for p in PROJECTS:
        if p['slug'] not in slugs:
            continue
        slug=p['slug']
        items.append(f'<a class="gallery-item" href="./projects/{slug}.html">{image(p["image"], p["image_alt"])}<span>{escape(p["title"])}</span></a>')
    return '<div class="visual-gallery">'+''.join(items)+'</div>'

GENAI_PROJECTS = "<section class=\"home-section\" aria-labelledby=\"genai-projects\"><h2 id=\"genai-projects\">Generative AI &amp; LLM Applications</h2><p>Retrieval-augmented generation systems developed with explicit evaluation of retrieval quality, evidence grounding and failure modes. These are research implementations, not claims of production deployment.</p><div class=\"project-grid\"><article class=\"project-card\"><div class=\"card-body\"><p class=\"eyebrow\">Multimodal RAG · Document understanding</p><h3><a href=\"https://github.com/AdebanjiAdelowo/multimodal-visual-rag\">Multimodal Visual RAG ↗</a></h3><p class=\"card-purpose\">Question answering over document pages containing text, tables, charts and images.</p><p>Compares OCR-based keyword and dense retrieval with image embeddings, hybrid fusion and reranking; evaluates answer grounding, page citations and abstention. On the documented textbook corpus, text hybrid retrieval was a strong baseline and visual retrieval did not show a meaningful improvement. GPU experiments remain separately pending.</p><p class=\"project-status\">Research evaluation · corpus-specific results</p><a class=\"section-link\" href=\"https://github.com/AdebanjiAdelowo/multimodal-visual-rag\">Methods, results and limitations ↗</a></div></article><article class=\"project-card\"><div class=\"card-body\"><p class=\"eyebrow\">Legal RAG · Citation verification</p><h3><a href=\"https://github.com/AdebanjiAdelowo/legal-research-rag\">Legal Research RAG ↗</a></h3><p class=\"card-purpose\">Source-grounded case-law retrieval and research summaries with citation checks.</p><p>Evaluates BM25, dense and hybrid retrieval, reranking, jurisdiction and date constraints, citation support and abstention. On 2,000 test queries, BM25 reached nDCG@10 of 0.176; normalized-score hybrid reached 0.186. Citation existence checks worked reliably, but substantive support and abstention remain limitations.</p><p class=\"project-status\">Research implementation · not legal advice; no citator</p><a class=\"section-link\" href=\"https://github.com/AdebanjiAdelowo/legal-research-rag\">Methods, results and limitations ↗</a></div></article></div></section>"
ADDITIONAL_PROJECTS = "<section class=\"home-section\" aria-labelledby=\"additional-projects\"><h2 id=\"additional-projects\">Additional projects</h2><p>Further research and engineering work; consult each repository for current evaluation status.</p><ul><li><a href=\"https://github.com/AdebanjiAdelowo/darcy-inverse-problem\">Darcy inverse problem</a> — PDE-constrained and Bayesian inversion</li><li><a href=\"https://github.com/AdebanjiAdelowo/fem-topology-optimization\">Topology optimisation</a> — finite elements and SIMP</li><li><a href=\"https://github.com/AdebanjiAdelowo/course-learning-portal\">DSA learning portal</a> — educational software</li><li><a href=\"https://github.com/AdebanjiAdelowo/ai-projects-portfolio\">FinBERT distillation</a> — 19% smaller model and up to 1.46× faster inference in the reported evaluation</li></ul></section>"

def home():
    selected=''.join(card(p) for p in PROJECTS)
    return '<p class="hero-role">Applied Mathematician &amp; Machine Learning Engineer</p><p class="lede">I am an applied mathematician and machine learning engineer with a background in numerical PDEs, scientific computing and mathematical modelling. My work combines computational methods, machine learning and software engineering to investigate scientific problems and develop practical data-driven systems.</p><p class="availability">Open to machine learning, data science, software engineering, research and PhD opportunities.</p><div class="cta-row hero-actions"><a href="./projects.html" class="btn btn-primary">Explore projects</a><a href="./cv.html" class="btn btn-outline">View CV</a></div><section class="home-section" aria-labelledby="selected-work"><div class="section-heading"><h2 id="selected-work">Selected research</h2></div><div class="project-grid">'+selected+'</div></section>'+GENAI_PROJECTS+ADDITIONAL_PROJECTS+'<section class="home-section" aria-labelledby="industry"><h2 id="industry">Professional experience</h2><p>My industry experience spans aviation analytics, predictive modelling, data analysis and engineering software.</p><a href="./experience.html">Professional experience →</a></section><section class="home-section" aria-labelledby="background"><h2 id="background">Background</h2><p>M.Sc. in Mathematical Engineering, University of L’Aquila; B.Sc. in Mathematics, Obafemi Awolowo University.</p><a href="./education.html">Education →</a></section><section class="contact-panel" aria-labelledby="collaboration"><h2 id="collaboration">Research and collaboration</h2><a class="btn btn-primary" href="./contact.html">Get in touch</a></section>'

def project_index():
    return '<p class="lede">Selected research in numerical simulation, inverse problems and scientific machine learning, with methods and evaluation in each case study.</p><section class="project-group" aria-labelledby="all-projects"><h2 id="all-projects">Research projects</h2><p class="project-count">'+str(len(PROJECTS))+' projects</p><div class="project-grid">'+''.join(card(p) for p in PROJECTS)+'</div></section>'+GENAI_PROJECTS+ADDITIONAL_PROJECTS

def case_study(p):
    detail=(ROOT/f"content/projects/{p['slug']}.html").read_text()
    # Supply dimensions and a direct full-resolution view for existing figures.
    def figure(match):
        attrs=match.group(1)
        src=re.search(r'src="([^"]+)"',attrs).group(1)
        local=src.removeprefix('./')
        if local in SIZES:
            w,h=SIZES[local]
            attrs+=f' width="{w}" height="{h}"'
        else:
            attrs+=' class="external-figure"'
        attrs+=' decoding="async"'
        return f'<a class="figure-link" href="{src}" aria-label="Open figure at full resolution"><img {attrs}></a>'
    detail=re.sub(r'<img\s+([^>]*?)/?>',figure,detail)
    detail=detail.replace('</figcaption>',' <span class="figure-hint">Select figure to enlarge.</span></figcaption>')
    # Consistent headings without changing research findings or their caveats.
    headings = {'Problem': 'Research question', 'Approach': 'Methodology', 'Verification': 'Experimental setup and verification', 'Key finding': 'Quantitative findings', 'Result': 'Quantitative findings', 'Diagnosis': 'Failure analysis'}
    for old, new in headings.items():
        detail = detail.replace(f'>{old}</h2>', f'>{new}</h2>')
    if 'Experimental setup and verification</h2>' not in detail:
        detail = '<div class="research-facet"><h2 class="facet-label">Experimental setup and verification</h2><p>See the methodology, quantitative results, and linked source repository for the documented benchmark setup and verification details. No independent verification beyond the reported study is implied.</p></div>' + detail
    if 'Quantitative findings</h2>' not in detail:
        detail = '<div class="research-facet"><h2 class="facet-label">Quantitative findings</h2><p>' + escape(p['result']) + '</p></div>' + detail
    if 'Limitations</h2>' not in detail:
        detail += '<div class="research-facet"><h2 class="facet-label">Limitations</h2><p>Interpret these results within the tested configurations and datasets described above.</p></div>'
    detail += '<div class="research-facet"><h2 class="facet-label">Reproducibility</h2><p>Source code, implementation details and available experiment records are linked in the project repository. The stated findings are specific to the documented evaluation setup.</p></div>'
    prefix=f'''<p class="eyebrow case-category">{escape(p['category'])}</p>
<div class="contribution"><h2>My contribution</h2><p>{escape(p['contribution'])}</p></div>
{status_line(p)}
<p class="case-result">{escape(p['result'])}</p>
<div class="cta-row"><a class="btn btn-primary" href="{escape(p['code'])}">View source code ↗</a><a class="btn btn-outline" href="./projects.html#{p['slug']}">All projects</a></div>'''
    return prefix+detail+f'<p class="back-link"><a href="./projects.html#{p["slug"]}">← Back to project index</a></p>'

PAGES={
 'index':('Adebanji Adelowo','Machine learning engineer and applied mathematician building data systems, ML applications, and scientific computing software.'),
 'cv':('CV','Download my industry CV for machine learning, data science, and engineering roles.'),
 'projects':('Projects','Numerical simulation, inverse problems, scientific ML, and engineering case studies with evaluation settings and limitations.'),
 'research':('Research','Research in numerical PDEs, inverse problems, uncertainty quantification, reduced-order modelling, and scientific machine learning.'),
 'experience':('Experience','Professional experience in data science, machine learning, aviation analytics, and engineering software.'),
 'education':('Education','Mathematics and mathematical engineering education, thesis work, academic awards, and mentorship.'),
 'skills':('Skills','Mathematical methods, scientific computing, machine learning, and software engineering skills.'),
 'contact':('Contact','Contact Adebanji Adelowo about research, PhD opportunities, scientific computing, and machine learning roles.'),
 'research-outputs':('Research Outputs','Theses and open-source research software in applied mathematics, numerical simulation, and scientific ML.'),
}

def render(filename,heading,description,content,active='',home_page=False):
    content=order_project_lists(content)
    nested='/' in filename
    root='../' if nested else './'
    links=[]
    for slug,label in [('index','Home'),('research','Research'),('projects','Projects'),('experience','Experience'),('cv','CV'),('contact','Contact')]:
        href=root+(slug+'.html')
        attrs=' aria-current="page"' if active==slug else ''
        links.append(f'<li><a href="{href}"{attrs}>{label}</a></li>')
    # Replace legacy project anchors with direct case-study routes, preserving index anchors externally.
    for slug in BY_SLUG:
        content=content.replace(f'href="./projects.html#{slug}"',f'href="./projects/{slug}.html"') if not nested else content
    if nested:
        content=re.sub(r'(href|src)="\./',r'\1="../',content)
    title='Adebanji Adelowo | Machine Learning & Applied Mathematics' if home_page else heading+' | Adebanji Adelowo'
    before_title=f'<a class="breadcrumb" href="{root}projects.html">← Projects</a>' if nested else ''
    if home_page:
        before_title='<img class="home-avatar" src="./images/profile/adebanji_avatar.png" alt="Cartoon avatar with glasses" width="1254" height="1254" decoding="async">'
        aliases={'selected-work':['research-projects-h'], 'research-themes':['areas-h','interests-h'], 'industry':['applied-projects-h'], 'background':['about-h','profile-h'], 'collaboration':['contact-h']}
        for target,old_ids in aliases.items():
            marker=''.join(f'<span id="{old}" class="anchor-alias"></span>' for old in old_ids)
            content=re.sub(r'(<section[^>]+aria-labelledby="'+target+r'">)',lambda m: marker+m.group(1),content)
    values=dict(title=escape(title),description=escape(description),canonical=BASE+('' if home_page else filename),root=root,navigation=''.join(links),body_class='home' if home_page else ('case-study' if nested else ''),heading=escape(heading),before_title=before_title,content=content)
    result=TEMPLATE
    for key,value in values.items():result=result.replace('{{'+key+'}}',value)
    return "\n".join(line.rstrip() for line in result.splitlines())+"\n"

def outputs():
    result={}
    for slug,(heading,description) in PAGES.items():
        content=home() if slug=='index' else project_index() if slug=='projects' else (ROOT/f'content/{slug}.html').read_text()
        result[slug+'.html']=render(slug+'.html',heading,description,content,slug,slug=='index')
    for p in PROJECTS:
        name='projects/'+p['slug']+'.html'
        result[name]=render(name,p['title'],p['result'],case_study(p),'projects')
    urls=[BASE+('' if name=='index.html' else name) for name in result]
    result['sitemap.xml']='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url><loc>{url}</loc></url>\n' for url in urls)+'</urlset>\n'
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    stale=[]
    rendered=outputs()
    for filename,text in rendered.items():
        path=ROOT/filename
        if args.check:
            if not path.exists() or path.read_text()!=text:stale.append(filename)
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(text)
    if stale:raise SystemExit('Generated files are stale: '+', '.join(stale))
    print(('Checked' if args.check else 'Rendered')+f' {len(rendered)-1} HTML pages and sitemap.')
