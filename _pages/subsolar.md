---
title: "subsolar_mergers"
# layout: default
excerpt:
sitemap: false
permalink: /subsolar/
date: 2026-06-27
modified: 2026-06-27
tags: animation
---
# Subsolar-mass binary mergers of strange stars and neutron stars
<hr style="border:1px solid gray">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <!-- 引入 MathJax -->
  <script>
    MathJax = {
      tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']]
      }
    };
  </script>
  <script id="MathJax-script" async
    src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js">
  </script>

  <style>
    figure {
      width: 100%;
      padding: 10px;
      box-sizing: border-box;
      text-align: center;
    }

    video {
      width: 100%;
      height: auto;
      border: 2px solid #555;
    }

    figcaption {
      margin-top: 15px;
      font-size: 20px;
      color: #333;
      line-height: 1.5;
      text-align: left;
    }
  </style>
</head>
<body>
  <p style="font-size: 18px; line-height: 1.6; color: #333;">
    These movies accompany the first numerical-relativity simulations of
    subsolar-mass binary <em>strange star</em> (SS) mergers, contrasted with
    subsolar-mass binary <em>neutron star</em> (NS) mergers. A strange star is
    self-bound by the strong interaction and of nearly uniform density, ending in
    a sharp surface, whereas a neutron star is gravitationally bound, centrally
    condensed, and more extended. The two below are representative equal-mass
    $0.5{+}0.5\,M_\odot$ binaries with the same chirp mass, so they follow an
    almost identical point-particle inspiral and diverge only as matter effects
    take over near merger.
  </p>

  <!-- Strange star (MIT bag model) -->
  <section>
    <h2>Strange star &mdash; SS1 (modified MIT bag model)</h2>
    <figure>
      <video controls>
        <source src="https://gravyong.github.io/assets/videos/MIT_05_05_N100_gwsnap.mp4" type="video/mp4">
      </video>
      <figcaption>
        Fig. 1: Equal-mass $0.5{+}0.5\,M_\odot$ binary <em>strange star</em> merger
        with the modified MIT bag-model EOS (model <tt>SS1</tt>), showing the
        gravitational-wave signal alongside the evolving equatorial-plane rest-mass
        density $\log_{10}[\rho/(\mathrm{g\,cm^{-3}})]$. The self-bound star is
        compact ($R\simeq8.4\,\mathrm{km}$, compactness $C\simeq0.088$, tidal
        deformability $\Lambda=5.2\times10^4$) and only weakly deformed through the
        inspiral, so it keeps its double-peaked binary structure up to contact and
        reaches a high gravitational-wave cut frequency
        $f_\mathrm{cut}\simeq825\,\mathrm{Hz}$ before the cores collide. The steep
        surface drives a strong shock that heats the contact layer
        ($\epsilon_\mathrm{th}\gtrsim0.03$) and a large radial bounce that re-expands
        the merged core from $\sim7\,\mathrm{km}$ out to $\simeq14\,\mathrm{km}$,
        raising spiral arms that eject $\sim10^{-2}\,M_\odot$ of decompressed quark
        matter. The remnant settles into a differentially rotating configuration
        surrounded by an extended disk and oscillates at a post-merger frequency
        $f_2\simeq1750\,\mathrm{Hz}$.
      </figcaption>
    </figure>
  </section>

  <!-- Neutron star (SFHo) -->
  <section>
    <h2>Neutron star &mdash; SFHo</h2>
    <figure>
      <video controls>
        <source src="https://gravyong.github.io/assets/videos/SFHo_05_05_N100_gwsnap.mp4" type="video/mp4">
      </video>
      <figcaption>
        Fig. 2: Same as Fig. 1 but for the equal-mass $0.5{+}0.5\,M_\odot$ binary
        <em>neutron star</em> merger with the <tt>SFHo</tt> EOS. The gravitationally
        bound star is more extended ($R\simeq12.4\,\mathrm{km}$, $C\simeq0.060$,
        $\Lambda=8.2\times10^4$) and more tidally deformable, so it develops
        pronounced spiral arms and sheds mass already before contact, reaching merger
        at a lower cut frequency $f_\mathrm{cut}\simeq681\,\mathrm{Hz}$. Its collision
        is milder, leaving a denser oscillating remnant that radiates at a
        <em>higher</em> post-merger frequency $f_2\simeq1900\,\mathrm{Hz}$, even
        though before merger it is the <em>less</em> compact of the two stars. Because
        the strange star's $f_\mathrm{cut}$ is shifted up while its $f_2$ is shifted
        down, the ratio $f_2/f_\mathrm{cut}$ cleanly separates the two classes and
        offers a way to tell a subsolar strange star from a neutron star.
      </figcaption>
    </figure>
  </section>
</body>

