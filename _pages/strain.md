---
title: "convection_animation"
# layout: default
excerpt: 
sitemap: false
permalink: /convection/
date: 2024-12-20
modified: 2024-12-20
tags: animation
header:
    overlay_image: header.png
    overlay_filter: 0.1 
---
# Convective stability analysis of massive neutron stars formed in binary mergers
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
  <!-- Criterion I group -->
  <section>
    <h2>Criterion I</h2>
    <figure>
      <video controls>
        <source src="https://gravyong.github.io/assets/videos/strain_evolution.mp4" type="video/mp4">
      </video>
      <figcaption>
        Fig. 1: The time evolution of the Schwarzschild criterion (first column), the Reyleigh-Solberg criterion (second column), and Criterion I (third column) in the $x\text{-}z$ (first row) and $x\text{-}y$ (second row) planes for the model <tt>APR4-135135</tt>. The black dashed line marks the place where the criterion equals zero. The black solid line represents the density contour at restmass density $\rho = 10^{11.5} \, \mathrm{g\,cm^{-3}}$.
      </figcaption>
  </section>
</body>