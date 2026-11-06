---
layout: page
title: Projects
permalink: /projects/
---

# Selected projects

A curated portfolio of scientific computing, numerical modeling, scientific machine learning, and applied AI. Results below are drawn from completed experiments or reported project evaluations; links provide further technical context.

## Scientific machine learning

<div class="project-grid">
  <article class="project-card"><span class="eyebrow">Inverse problems</span><h3><a href="https://github.com/AdebanjiAdelowo/darcy-inverse-problem">Darcy inverse problem</a></h3><p>Physics-informed reconstruction of unknown coefficients; five-seed study with relative parameter error below 1%.</p></article>
  <article class="project-card"><span class="eyebrow">Neural operators</span><h3><a href="https://github.com/AdebanjiAdelowo/physicsnemo-pino-darcy">PhysicsNeMo PINO Darcy</a></h3><p>Evaluated physics weighting across multiple runs, observing lower PDE residuals with physics regularization.</p></article>
  <article class="project-card"><span class="eyebrow">Physics-informed neural networks</span><h3><a href="https://github.com/AdebanjiAdelowo/pinn-advection-diffusion">PINN advection–diffusion</a></h3><p>Numerical solution of an advection–diffusion problem with reported relative L2 error of approximately 5 × 10⁻³.</p></article>
  <article class="project-card"><span class="eyebrow">Reduced-order modeling</span><h3><a href="https://github.com/AdebanjiAdelowo/neural-surrogate-burgers">Burgers PDE: POD, DEIM and neural surrogates</a></h3><p>Compared pseudo-spectral simulations, tensorial POD–Galerkin and DEIM reduced models, and MLP/FNO surrogates. Verified spatial convergence and tested adaptive integration; results depend on the tested parameter family and reference resolution.</p></article>
  <article class="project-card"><span class="eyebrow">Dynamical systems</span><h3><a href="https://github.com/AdebanjiAdelowo/lorenz96-data-assimilation">Lorenz-96 data assimilation</a></h3><p>Ensemble-based state estimation for chaotic dynamical systems.</p></article>
</div>

## Numerical modeling and inverse methods

- **[FEM cylinder flow](https://github.com/AdebanjiAdelowo/fem-cylinder-flow)** — incompressible flow simulation and drag, lift, and vortex-shedding diagnostics.
- **[Photoacoustic reconstruction](https://github.com/AdebanjiAdelowo/photoacoustic-reconstruction)** — inverse image reconstruction from indirect observations.
- **[Optimal mixing of passive scalars](https://github.com/AdebanjiAdelowo/Master-Thesis)** — mathematical analysis of mixing under incompressibility and energy/enstrophy constraints, with pseudo-spectral numerical investigations.
- **[Burgers reduced-order modeling](https://github.com/AdebanjiAdelowo/neural-surrogate-burgers)** — tensorial POD–Galerkin, spectral-consistent DEIM, grid-convergence checks and adaptive time integration. In the documented controlled benchmark, rank-16 tensorial POD with Radau at Nx = 2048 was 1.6–1.75× faster than the Nx = 512 full solver while meeting its mean and worst-case error benchmark; Performance varies by test case.
- **[Navier–Stokes 2D](https://github.com/AdebanjiAdelowo/navier-stokes-2d)** — fluid simulation and reduced-order modeling.

## Generative AI and efficient ML

- **[FinBERT distillation](https://github.com/AdebanjiAdelowo/ai-projects-portfolio)** — evaluated a distilled model that was **19% smaller**, with inference up to **1.46× faster**.

## Additional research and experimental work

Additional projects exploring neural operators, graph-based simulation, and reproducible scientific computing. Individual repositories document their experimental status and findings.

- **[PhysicsNeMo FNO Darcy](https://github.com/AdebanjiAdelowo/physicsnemo-fno-darcy)** — neural operator mode and training-budget studies.
- **[PhysicsNeMo MeshGraphNet Vortex](https://github.com/AdebanjiAdelowo/physicsnemo-meshgraphnet-vortex)** — graph-based flow prediction and long-horizon diagnostics.
- **[PhysicsNeMo Stokes Fine-Tuning](https://github.com/AdebanjiAdelowo/physicsnemo-stokes-finetuning)** — mesh-based fine-tuning experiments.
- **[Scientific project audit](https://github.com/AdebanjiAdelowo/selected-projects-scientific-audit)** — validation and reproducibility records.

For research themes and methodology, see [Research]({{ '/research/' | relative_url }}).
