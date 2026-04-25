---
permalink: /
title: "Yong Gao"
seo_title: "Yong Gao"
hide_title: true
author_profile: true
header:
  overlay_image: header.png
  overlay_filter: 0.3
---

I'm a postdoctoral researcher in the [Computational Relativistic Astrophysics group](https://www.aei.mpg.de/comp-rel-astro) led by [Masaru Shibata](https://www2.yukawa.kyoto-u.ac.jp/~masaru.shibata/indexj.html) at the [Albert Einstein Institute](https://www.aei.mpg.de/2772/de), Potsdam, working on **neutron-star physics** and **strong-field tests of gravity**. See the [research]({{ site.url }}/research/), [publications]({{ site.url }}/publication/), and [links]({{ site.url }}/Links/) pages for more.

<h2 class="home-section">Recent work</h2>
<hr style="border:1px solid gray">

<div class="paper-spotlight">
  <div class="paper-spotlight__tag">New · 2026</div>
  <h3 class="paper-spotlight__title"><a href="{{ site.url }}/convection/">Convective stability of massive neutron stars formed in binary mergers</a></h3>
  <p class="paper-spotlight__venue">Y. Gao, K. Hayashi, K. Kiuchi, A. T.-L. Lam, H.-J. Kuan, M. Shibata — Phys. Rev. D <strong>113</strong>, 023011 (2026)</p>
  <p class="paper-spotlight__summary is-clamped">We run fully general-relativistic hydrodynamics simulations of binary neutron-star mergers out to 100 ms post-merger and derive — then apply for the first time — convective-stability criteria for hot, differentially rotating relativistic stars that include both buoyancy and rotation. The remnant massive neutron stars show no large-scale convective instability: entropy and angular momentum both increase outward, and rotation stabilizes regions that the Schwarzschild criterion would call unstable. Mode analysis reveals no observable inertial modes after the quadrupolar <em>f</em>-modes damp, while the persistent <em>m</em>=1 one-armed mode correlates strongly with violations of linear-momentum conservation — suggesting it may be numerical rather than physical.</p>
  <button type="button" class="paper-spotlight__more" aria-expanded="false">Show more</button>
  <p class="paper-spotlight__links">
    <a class="btn" href="https://doi.org/10.1103/w8gq-3d54">Paper</a>
    <a class="btn" href="https://arxiv.org/abs/2501.19053" style="color: #F48FB1;">arXiv</a>
    <a class="btn" href="{{ site.url }}/convection/">Watch the simulations →</a>
  </p>
</div>

<div class="paper-spotlight">
  <div class="paper-spotlight__tag">Recent · 2025</div>
  <h3 class="paper-spotlight__title"><a href="{{ site.url }}/strain/">Nonradial oscillations of stratified neutron stars with solid crusts</a></h3>
  <p class="paper-spotlight__venue">Y. Gao, H.-J. Kuan, C.-J. Xia, H. O. Silva, M. Shibata — Phys. Rev. D <strong>112</strong>, 123006 (2025)</p>
  <p class="paper-spotlight__summary is-clamped">We model the dynamical tide of an inspiraling neutron star as a set of driven harmonic oscillators whose natural frequencies are the quasinormal modes of a fully relativistic stellar model with a solid crust and compositional stratification. Stratification erases the canonical crust–core interface mode and replaces it with compositional gravity modes anchored in outer-core buoyancy; meanwhile, the <em>f</em>-mode and core <em>g</em>-mode can leak into the crust under a penetration criterion we derive. The headline result for multimessenger observations: both resonant <em>g</em>-mode forcing and nonresonant <em>f</em>- and crustal-shear-mode driving can overstress the crust before merger, potentially channeling energy into the magnetosphere and powering electromagnetic precursors.</p>
  <button type="button" class="paper-spotlight__more" aria-expanded="false">Show more</button>
  <p class="paper-spotlight__links">
    <a class="btn" href="https://doi.org/10.1103/nbk7-8kts">Paper</a>
    <a class="btn" href="https://arxiv.org/abs/2509.00257" style="color: #F48FB1;">arXiv</a>
    <a class="btn" href="{{ site.url }}/strain/">Watch the crust-strain evolution →</a>
  </p>
</div>

<h2 class="home-section">From the blog</h2>
<hr style="border:1px solid gray">

{% assign posts = site.posts | slice: 0, 3 %}
{% if posts.size > 0 %}
  {% for post in posts %}
  <article class="home-post">
    <h3 class="home-post__title"><a href="{{ site.url }}{{ post.url }}">{{ post.title }}</a></h3>
    <p class="home-post__meta">{{ post.date | date: "%B %-d, %Y" }}</p>
    {% if post.excerpt %}<p class="home-post__excerpt">{{ post.excerpt | markdownify | strip_html | truncate: 260 }}</p>{% endif %}
    <p><a class="btn" href="{{ site.url }}{{ post.url }}">Read →</a></p>
  </article>
  {% endfor %}
{% else %}
  <p>No posts yet.</p>
{% endif %}

<p><a href="{{ site.url }}/posts/">All posts →</a></p>

<script>
(function () {
  document.querySelectorAll('.paper-spotlight__more').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var summary = btn.previousElementSibling;
      if (!summary || !summary.classList.contains('paper-spotlight__summary')) return;
      var nowClamped = summary.classList.toggle('is-clamped');
      btn.textContent = nowClamped ? 'Show more' : 'Show less';
      btn.setAttribute('aria-expanded', nowClamped ? 'false' : 'true');
    });
  });
})();
</script>
