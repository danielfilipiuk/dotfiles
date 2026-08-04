









<!doctype html>
<html>
  <head>
    
  
      <meta charset="UTF-8">
       <link rel="stylesheet" type="text/css"
            href="/static/bootstrap/bootstrap.min.css" />
      <link rel="stylesheet" type="text/css"
            href="/static/css/debian.css" />
      <link rel="stylesheet" type="text/css"
            href="/static/css/base.css" />
      <link rel="shortcut icon"
            href="/static/favicon.ico" />
      
      <title>File: compton-fake-transparency-fshader-win.glsl
| Debian Sources
</title>
    

  <link rel="stylesheet"
        href="/static/javascript-lib/highlight/styles/googlecode.css">
  <script src="/static/javascript-lib/highlight/highlight.min.js"></script>

  <script src="/static/javascript/debsources.js"></script>
  <link rel="stylesheet" type="text/css"
        href="/static/css/source_file.css" />


  </head>
  <body>
    <header id="header">
      <div id="upperheader">
        <div id="logo">
          <a href="https://www.debian.org" title="Debian Home"><img src="/static/img/debian-50.png" alt="Debian"></a>
        </div> <!-- end logo -->
        <p class="section"><a href="/">DEBSOURCES</a></p>
        <div id="searchbox">
            
    
  
  <form action="/search/" name="searchform"
        method="post" style="display: inline;">
      <input id="query-1" name="query" placeholder="package name" required type="text" value="">
    
    
    <input type="submit" value="Search package" />
  </form>
            <form name="codesearch" method="get"
            action="https://codesearch.debian.net/search">
              <input name="q" value="package:picom "
              type="text" />
              <input type="submit" value="Search code" />
            </form>
        </div>   <!-- end sitetools -->
      </div> <!-- end upperheader -->

      <nav id="navbar">
        <p class="hidecss"><a href="#content">Skip Quicknav</a></p>
        
  <ul>
    <li><a href="/">Home</a></li>
    <li><a href="/advancedsearch/">Search</a></li>
    <li><a href="/doc/">Documentation</a></li>
    <li><a href="/stats/">Stats</a></li>
    <li><a href="/doc/about/">About</a></li>
  </ul>

      </nav> <!-- end navbar -->

      <p id="breadcrumbs"><a href="/">sources</a> / <a href="/src/picom">picom</a> / <a href="/src/picom/13-1">13-1</a> / compton-fake-transparency-fshader-win.glsl</p>
    </header> <!-- end header -->

    
      <div id="content">
        


<h2>File: compton-fake-transparency-fshader-win.glsl</h2>



<script type="text/javascript">
    function toggle(id)
    {
    var elem = document.getElementById(id);
    if(elem.style.display == "none")
      elem.style.display = "block";
    else
      elem.style.display = "none";
    }
  </script>


<div id="pkginfobox" class="pkginfobox_fixed">

  
  <span onclick="toggle('infobox_content')">package info
    <small>(click to toggle)</small></span>
  
  <div id="infobox_content">
    
    <em>picom 13-1</em>
    
    <ul>
    <!--
    
      <li><a href="/copyright/license/picom/13-1/">view license information</a></li>
    
    -->
      <li>links:
  <a href="https://tracker.debian.org/pkg/picom"><abbr title="Debian Package Tracking
                 System">PTS</abbr></a>,
  <a href="https://salsa.debian.org/nikos/picom"><abbr title="Version Control System">VCS</abbr></a>
  </li>
      <li>area: main</li>
      <li>in suites: forky, sid</li>
      
        <li>size: 2,432 kB</li>
      

      

      
        <li><abbr title="source lines of code">sloc</abbr>:
    
            
              ansic: 25,725; 
            
              python: 685; 
            
              sh: 365; 
            
              makefile: 11
            
    
        </li>
      
    </ul>
  </div>
</div>


<table id="file_metadata">
  <tr>
    <td>
    file content (19 lines)
    | stat: -rw-r--r-- 487 bytes
    </td>
    <td style="text-align: right;">
    <a id="link_parent_folder" href="/src/picom/13-1">parent folder</a>
    | <a id="link_download" href="/data/main/p/picom/13-1/compton-fake-transparency-fshader-win.glsl">download</a>
    
    | <a id="link_duplicates" href="/sha256/?checksum=aa8f97a896eb7ead02cc617af44a7e08db872c6ee199303575117c400c6b206c&amp;page=1">
	  duplicates (8)</a>
    
    </td>
  </tr>
</table>
<table id="codetable">
  <tr>
    <td>
      <pre id="sourceslinenumbers"><a id="L1" href="#L1">1</a><br /><a id="L2" href="#L2">2</a><br /><a id="L3" href="#L3">3</a><br /><a id="L4" href="#L4">4</a><br /><a id="L5" href="#L5">5</a><br /><a id="L6" href="#L6">6</a><br /><a id="L7" href="#L7">7</a><br /><a id="L8" href="#L8">8</a><br /><a id="L9" href="#L9">9</a><br /><a id="L10" href="#L10">10</a><br /><a id="L11" href="#L11">11</a><br /><a id="L12" href="#L12">12</a><br /><a id="L13" href="#L13">13</a><br /><a id="L14" href="#L14">14</a><br /><a id="L15" href="#L15">15</a><br /><a id="L16" href="#L16">16</a><br /><a id="L17" href="#L17">17</a><br /><a id="L18" href="#L18">18</a><br /><a id="L19" href="#L19">19</a><br /></pre>
    </td>
    <td>
      <pre><code id="sourcecode" class="no-highlight"><span id="line1" class="codeline ">uniform float opacity;
</span><span id="line2" class="codeline ">uniform bool invert_color;
</span><span id="line3" class="codeline ">uniform sampler2D tex;
</span><span id="line4" class="codeline ">
</span><span id="line5" class="codeline ">void main() {
</span><span id="line6" class="codeline ">	vec4 c = texture2D(tex, gl_TexCoord[0]);
</span><span id="line7" class="codeline ">	{
</span><span id="line8" class="codeline ">		// Change vec4(1.0, 1.0, 1.0, 1.0) to your desired color
</span><span id="line9" class="codeline ">		vec4 vdiff = abs(vec4(1.0, 1.0, 1.0, 1.0) - c);
</span><span id="line10" class="codeline ">		float diff = max(max(max(vdiff.r, vdiff.g), vdiff.b), vdiff.a);
</span><span id="line11" class="codeline ">		// Change 0.8 to your desired opacity
</span><span id="line12" class="codeline ">		if (diff &lt; 0.001)
</span><span id="line13" class="codeline ">			c *= 0.8;
</span><span id="line14" class="codeline ">	}
</span><span id="line15" class="codeline ">	if (invert_color)
</span><span id="line16" class="codeline ">		c = vec4(vec3(c.a, c.a, c.a) - vec3(c), c.a);
</span><span id="line17" class="codeline ">	c *= opacity;
</span><span id="line18" class="codeline ">	gl_FragColor = c;
</span><span id="line19" class="codeline ">}
</span></code></pre>
    </td>
  </tr>
</table>

<script type="text/javascript">
  debsources.source_file();
  hljs.highlightBlock(document.getElementById('sourcecode'))

</script>




      </div>

      <footer id="footer">
        
          

    
  
<p style="margin: 0 0 0 0; line-height: 1em;">
  Browse by prefix: &ensp;
  

    
  
    <a href="/prefix/0/">0</a>
    <a href="/prefix/1/">1</a>
    <a href="/prefix/2/">2</a>
    <a href="/prefix/3/">3</a>
    <a href="/prefix/4/">4</a>
    <a href="/prefix/6/">6</a>
    <a href="/prefix/7/">7</a>
    <a href="/prefix/8/">8</a>
    <a href="/prefix/9/">9</a>
    <a href="/prefix/a/">a</a>
    <a href="/prefix/b/">b</a>
    <a href="/prefix/c/">c</a>
    <a href="/prefix/d/">d</a>
    <a href="/prefix/e/">e</a>
    <a href="/prefix/f/">f</a>
    <a href="/prefix/g/">g</a>
    <a href="/prefix/h/">h</a>
    <a href="/prefix/i/">i</a>
    <a href="/prefix/j/">j</a>
    <a href="/prefix/k/">k</a>
    <a href="/prefix/l/">l</a>
    <a href="/prefix/lib-/">lib-</a>
    <a href="/prefix/lib1/">lib1</a>
    <a href="/prefix/lib2/">lib2</a>
    <a href="/prefix/lib3/">lib3</a>
    <a href="/prefix/lib6/">lib6</a>
    <a href="/prefix/liba/">liba</a>
    <a href="/prefix/libb/">libb</a>
    <a href="/prefix/libc/">libc</a>
    <a href="/prefix/libd/">libd</a>
    <a href="/prefix/libe/">libe</a>
    <a href="/prefix/libf/">libf</a>
    <a href="/prefix/libg/">libg</a>
    <a href="/prefix/libh/">libh</a>
    <a href="/prefix/libi/">libi</a>
    <a href="/prefix/libj/">libj</a>
    <a href="/prefix/libk/">libk</a>
    <a href="/prefix/libl/">libl</a>
    <a href="/prefix/libm/">libm</a>
    <a href="/prefix/libn/">libn</a>
    <a href="/prefix/libo/">libo</a>
    <a href="/prefix/libp/">libp</a>
    <a href="/prefix/libq/">libq</a>
    <a href="/prefix/libr/">libr</a>
    <a href="/prefix/libs/">libs</a>
    <a href="/prefix/libt/">libt</a>
    <a href="/prefix/libu/">libu</a>
    <a href="/prefix/libv/">libv</a>
    <a href="/prefix/libw/">libw</a>
    <a href="/prefix/libx/">libx</a>
    <a href="/prefix/liby/">liby</a>
    <a href="/prefix/libz/">libz</a>
    <a href="/prefix/m/">m</a>
    <a href="/prefix/n/">n</a>
    <a href="/prefix/o/">o</a>
    <a href="/prefix/p/">p</a>
    <a href="/prefix/q/">q</a>
    <a href="/prefix/r/">r</a>
    <a href="/prefix/s/">s</a>
    <a href="/prefix/t/">t</a>
    <a href="/prefix/u/">u</a>
    <a href="/prefix/v/">v</a>
    <a href="/prefix/w/">w</a>
    <a href="/prefix/x/">x</a>
    <a href="/prefix/y/">y</a>
    <a href="/prefix/z/">z</a>

  &ensp; | &ensp;
  Browse <a href="/list/1/">by page</a>
</p>
<hr />
<div style="position: relative">

<p>
  Debsources &mdash; Copyright (C) 2011&ndash;2021,
  <a href="https://salsa.debian.org/qa/debsources/blob/master/AUTHORS">The Debsources developers</a>.
  License:
  <a href="https://www.gnu.org/licenses/agpl.html">GNU AGPLv3+</a>.
  <br />
  Hosted source files are available under their own
  <a href="https://www.debian.org/doc/debian-policy/ch-source.html#s-dpkgcopyright">copyright
  and licenses</a>.
  <br />
  Source code: <a href="https://salsa.debian.org/qa/debsources">Git</a>.
  Contact: <a href="mailto:qa-debsources@lists.alioth.debian.org">qa-debsources@lists.alioth.debian.org</a>.
  Last update: Thu, 02 Jul 2026 20:15:58 -0000.
</p>
</div>

<script type="text/javascript">
// @license magnet:?xt=urn:btih:0b31508aeb0634b347b8270c7bee4d411b5d4109&dn=agpl-3.0.txt AGPL-3.0
var elems = document.querySelectorAll('.js-append-window-location-hash');

for (var i = 0; i < elems.length; ++i) {
  elems[i].setAttribute('href', elems[i].getAttribute('href') + window.location.hash);
}
// @license-end
</script>
        
      </footer>
    
  </body>
</html>