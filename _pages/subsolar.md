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
    These movies accompany the simulations of
    subsolar-mass binary <em>strange star</em> and binary <em>neutron star</em> mergers. 
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
        (modified MIT bag-model EOS, model <tt>SS1</tt>), with the gravitational-wave
        signal beside the equatorial-plane rest-mass density
        $\log_{10}[\rho/(\mathrm{g\,cm^{-3}})]$. After merger the green line marks the unbound
        ejecta.
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
        Fig. 2: Same as Fig. 1 but for the <tt>SFHo</tt> neutron-star EOS. 
      </figcaption>
    </figure>
  </section>
</body>

