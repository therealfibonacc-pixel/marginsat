/* Margin landing pages: top bar state, visit counts and the one ad slot.
   tools/configure.py rewrites the CFG line; keep it on one line. */
(function(){
"use strict";
var CFG = {"goatcounter": "marginsat", "ads": {"client": "", "slot": ""}};

/* top bar: glass over the dark band, paper once the page scrolls past it */
var tb = document.getElementById("topbar"), band = document.querySelector(".band");
function bar(){
  if(!tb) return;
  var y = window.scrollY || 0, h = tb.offsetHeight || 60;
  tb.classList.toggle("stuck", y > 4);
  tb.classList.toggle("light", !!band && band.getBoundingClientRect().bottom < h);
}
window.addEventListener("scroll", bar, {passive: true});
bar();

/* on phones the nav scrolls sideways: bring the current page's link into view */
var nv = document.querySelector(".nav"), cur = nv && nv.querySelector("[aria-current]");
if(cur && nv.scrollWidth > nv.clientWidth) nv.scrollLeft = Math.max(0, cur.offsetLeft - nv.offsetLeft - (nv.clientWidth - cur.offsetWidth) / 2);

/* visit counts (GoatCounter: no cookies, no personal data) */
var gc = String(CFG.goatcounter || "").trim().toLowerCase();
if(/^[a-z0-9-]{2,50}$/.test(gc)){
  var s = document.createElement("script");
  s.async = true; s.src = "https://gc.zgo.at/count.js";
  s.setAttribute("data-goatcounter", "https://" + gc + ".goatcounter.com/count");
  document.head.appendChild(s);
}

/* one manual AdSense unit at the bottom of the page, labeled as an advertisement */
var host = document.getElementById("ad-host"), ads = CFG.ads || {};
var live = /^ca-pub-\d{10,20}$/.test(ads.client || "") && /^\d{5,14}$/.test(ads.slot || "");
var preview = false;
try{
  if(/[?&]adpreview=1\b/.test(location.search)) localStorage.setItem("m:adpreview", "1");
  if(/[?&]adpreview=0\b/.test(location.search)) localStorage.removeItem("m:adpreview");
  preview = localStorage.getItem("m:adpreview") === "1";
}catch(e){}
if(host && (live || preview)){
  host.hidden = false;
  host.innerHTML = '<div class="adbox"><span class="adlabel">Advertisement</span>' + (live
    ? '<ins class="adsbygoogle" style="display:block" data-ad-client="' + ads.client + '" data-ad-slot="' + ads.slot + '" data-ad-format="auto" data-full-width-responsive="true"></ins>'
    : '<div class="adph">Ad slot preview. Real ads appear here once AdSense is set up.</div>') + "</div>";
  if(live){
    if(!document.querySelector('script[src*="adsbygoogle.js"]')){
      var a = document.createElement("script"); a.async = true; a.crossOrigin = "anonymous";
      a.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" + encodeURIComponent(ads.client);
      document.head.appendChild(a);
    }
    try{ (window.adsbygoogle = window.adsbygoogle || []).push({}); }catch(e){}
  }
}
})();
