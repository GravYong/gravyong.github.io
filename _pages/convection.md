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
    <h3>Criterion I</h3>
    <figure>
      <video controls>
        <source src="https://gravyong.github.io/assets/videos/APR4_2_4.mp4" type="video/mp4">
      </video>
      <figcaption>
        Fig. 1: The time evolution of the Schwarzschild criterion (first column), the Reyleigh-Solberg criterion (second column), and Criterion I (third column) in the $x\text{-}z$ (first row) and $x\text{-}y$ (second row) planes for the model <tt>APR4-135135</tt>. The black dashed line marks the place where the criterion equals zero. The black solid line represents the density contour at restmass density $\rho = 10^{11.5} \, \mathrm{g\,cm^{-3}}$.
      </figcaption>
    </figure>
    <figure>
      <video controls>
        <source src="https://gravyong.github.io/assets/videos/MPA1_1_4.mp4" type="video/mp4">
      </video>
      <figcaption>
        Fig. 2: Same as Fig. 1 but for the model <tt>MPA1-135135</tt>.
      </figcaption>
    </figure>
    <figure>
      <video controls>
        <source src="https://gravyong.github.io/assets/videos/SLy4_2_5.mp4" type="video/mp4">
      </video>
      <figcaption>
        Fig. 3: Same as Fig. 1 but for the model <tt>SLy4-128128</tt>.
      </figcaption>
    </figure>
  </section>
  <!-- Criterion II group -->
  <section>
    <h3>Criterion II</h3>
    <figure>
      <video controls>
        <source src="https://gravyong.github.io/assets/videos/APR4_CritII.mp4" type="video/mp4">
      </video>
      <figcaption>
        Fig. 4: The time evolution of Criterion II in the $x\text{-}z$ (first row) and $x\text{-}y$ (second row) planes for the model <tt>APR4-135135</tt>. The black dashed line marks where the criterion equals zero. The black solid line represents the density contour at $\rho = 10^{11.5} \, \mathrm{g\,cm^{-3}}$.
      </figcaption>
    </figure>
    <figure>
      <video controls>
        <source src="https://gravyong.github.io/assets/videos/MPA1_CritII.mp4" type="video/mp4">
      </video>
      <figcaption>
        Fig. 5: Same as Fig. 1 but for the model <tt>MPA1-135135</tt>.
      </figcaption>
    </figure>
    <figure>
      <video controls>
        <source src="https://gravyong.github.io/assets/videos/SLy4_CritII.mp4" type="video/mp4">
      </video>
      <figcaption>
        Fig.6: Same as Fig. 4 but for the model <tt>SLy4-128128</tt>.
      </figcaption>
    </figure>
  </section>
</body>


