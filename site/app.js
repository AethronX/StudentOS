/* ============================================================
   Student OS Pro — landing page behaviour
   Bilingual (EN/AR + RTL), sticky nav, scroll reveal, checkout.
   ============================================================ */
(function () {
  "use strict";

  var CFG = window.STUDENTOS_CONFIG || {};

  /* Keys whose values contain markup and must be set via innerHTML. */
  var HTML_KEYS = { "hero.title": true };

  var I18N = {
    en: {}, // English lives in the HTML itself; this stays empty by design.
    ar: {
      "skip": "تخطَّ إلى المحتوى",

      "nav.features": "المزايا",
      "nav.inside": "المحتويات",
      "nav.pricing": "السعر",
      "nav.faq": "أسئلة شائعة",
      "nav.cta": "احصل عليه",

      "hero.eyebrow": "مصمَّم لطلاب الجامعات",
      "hero.title": "حياتك الدراسية كاملة،<br>في نظام <em>واحد</em> أخيراً.",
      "hero.sub": "ليست مجرد قائمة مهام أنيقة. Student OS Pro هو ٢٠ قاعدة بيانات مترابطة تحسب معدلك التراكمي، وتعدّ أيام تسليماتك، وتتابع مصروفك — تلقائياً.",
      "hero.cta": "احصل على Student OS Pro",
      "hero.cta2": "شاهد كيف يعمل",
      "hero.b1": "يعمل على خطة نوشن المجانية",
      "hero.b2": "هاتف وتابلت وكمبيوتر",
      "hero.b3": "تحديثات مدى الحياة",

      "prev.gpa": "معدل الفصل",
      "prev.credits": "ساعة",
      "prev.due": "تسليمات قريبة",
      "prev.progress": "التقدّم",
      "prev.balance": "رصيد هذا الشهر",
      "prev.note": "رسم توضيحي للنظام — وليس لقطة شاشة.",

      "stat.db": "قاعدة بيانات مترابطة",
      "stat.views": "عرضاً جاهزاً",
      "stat.math": "حساب يدوي للمعدل",
      "stat.setup": "للإعداد",

      "prob.title": "معظم قوالب الطلاب تنهار في الأسبوع الثالث",
      "prob.sub": "تبدو جميلة في اليوم الأول. ثم تكتشف أن لا شيء مترابط — تنسخ الموعد نفسه في أربعة أماكن، وتحسب معدلك على الآلة الحاسبة، وتخمّن أين ذهب مصروفك.",
      "prob.bad": "القالب العادي",
      "prob.bad1": "قوائم منفصلة لا يتحدث بعضها إلى بعض",
      "prob.bad2": "تحسب معدلك التراكمي بنفسك",
      "prob.bad3": "المواعيد موزّعة في ثلاثة أماكن",
      "prob.bad4": "غير صالح للهاتف — تمرير أفقي لا ينتهي",
      "prob.bad5": "يصلك فارغاً، فلا تبدأ أبداً",
      "prob.good": "‏Student OS Pro",
      "prob.good1": "المادة الواحدة مرتبطة بواجباتها واختباراتها وملاحظاتها وموادها",
      "prob.good2": "المعدل التراكمي يحسب نفسه من درجاتك",
      "prob.good3": "كل المواعيد تجتمع في أجندة واحدة",
      "prob.good4": "مبني للهاتف أولاً — ٣ أعمدة، بلا تمرير أفقي",
      "prob.good5": "يصلك مملوءاً ببيانات، فترى النظام يعمل فوراً",

      "feat.title": "المحرّك الذي يعمل في الخلفية",
      "feat.sub": "هذه الروابط هي الفرق بين نظام حقيقي ومجموعة قوائم.",
      "feat.1t": "معدلك التراكمي يحسب نفسه",
      "feat.1b": "ضع تقدير الحرف على المادة، فيتحوّل إلى نقاط، ويُوزن بالساعات المعتمدة، ثم يتجمّع في معدل الفصل. غيّر تقديراً واحداً فيتحدّث كل شيء. بلا جداول ولا آلة حاسبة.",
      "feat.cr": "س",
      "feat.2t": "كل شيء مرتبط بالمادة",
      "feat.2b": "الواجبات والاختبارات والملاحظات والمواد والمشاريع كلها ترتبط بالمادة. تفتح مادة واحدة فترى صورتها كاملة — دون أي عمل يدوي.",
      "feat.3t": "عدّاد مباشر للمواعيد",
      "feat.3b": "كل واجب يعرض الأيام المتبقية وشريط تقدّم بصري، فتتحول كلمة «لاحقاً» إلى رقم حقيقي قبل أن تتحول إلى مشكلة.",
      "feat.4t": "أموال تُحسب صح",
      "feat.4b": "الدخل والمصروف في سجل واحد. الجمع يتكفّل بالإشارات الموجبة والسالبة، فيصبح رصيدك الحقيقي نظرة واحدة لا أمسية حسابات.",
      "feat.5t": "عمل يعود عليك",
      "feat.5b": "سجّل ورديّة بساعاتها وأجرها، فيُحسب أجر كل ورديّة وإجمالي كل وظيفة. وتابع طلبات التدريب من الرغبة حتى العرض.",
      "feat.6t": "يعمل فعلاً على هاتفك",
      "feat.6b": "كل عرض محدود بثلاثة أعمدة ظاهرة مع تثبيت العنوان. معظم القوالب تعطيك جدولاً بخمسة عشر عموداً وتسميه متوافقاً مع الهاتف.",

      "in.title": "ماذا يوجد بالداخل",
      "in.sub": "أربع مساحات مترابطة تغطي حياة الطالب كاملة.",
      "in.a1t": "المساحة الدراسية",
      "in.a1b": "المواد، الجدول الأسبوعي، الأهداف، الاختبارات، المواد الدراسية، الملاحظات، المشاريع، الأجندة، المهام، والمهارات.",
      "in.a1p1": "المواد والمعدل",
      "in.a1p2": "الواجبات",
      "in.a1p3": "الاختبارات",
      "in.a1p4": "الملاحظات",
      "in.a1p5": "الأجندة",
      "in.a1p6": "المهام",
      "in.a2t": "مساحة العمل",
      "in.a2b": "عمل جزئي مع تتبّع الورديات والدخل، إضافة إلى مسار كامل لطلبات التدريب.",
      "in.a2p1": "الورديات والأجر",
      "in.a2p2": "الطلبات",
      "in.a2p3": "المقابلات",
      "in.a3t": "مدير المالية",
      "in.a3b": "سجل واحد للدخل والمصروف، مصنّف، مع إجماليات يمكن الوثوق بها.",
      "in.a3p1": "الدخل",
      "in.a3p2": "المصروفات",
      "in.a3p3": "التصنيفات",
      "in.a4t": "المساحة الشخصية",
      "in.a4b": "لأن الإرهاق أسرع طريق لخسارة فصل كامل. الرياضة، الوجبات، اليوميات، الكتب، العادات، وجهات الاتصال.",
      "in.a4p1": "العادات",
      "in.a4p2": "اليوميات",
      "in.a4p3": "الوجبات",
      "in.a4p4": "الكتب",

      "pr.title": "دفعة واحدة. وهو لك للأبد.",
      "pr.sub": "بلا اشتراك. وتحديثات مجانية مدى الحياة.",
      "pr.tag": "‏Student OS Pro",
      "pr.note": "دفعة واحدة · وصول دائم",
      "pr.f1": "كل قواعد البيانات الـ٢٠ المترابطة",
      "pr.f2": "٢٦ عرضاً جاهزاً (لوحة، تقويم، معرض، جدول)",
      "pr.f3": "محرّك المعدل التراكمي التلقائي",
      "pr.f4": "محسّن للهاتف والتابلت والكمبيوتر",
      "pr.f5": "بيانات تجريبية مضمّنة — ترى النظام يعمل فوراً",
      "pr.f6": "دليل «ابدأ من هنا» خطوة بخطوة",
      "pr.f7": "تحديثات مجانية، للأبد",
      "pr.cta": "احصل عليه الآن",
      "pr.fine": "دفع آمن عبر Stripe. يصلك رابط قالب نوشن مباشرة بعد الدفع.",

      "faq.title": "أسئلة",
      "faq.q1": "هل أحتاج اشتراكاً مدفوعاً في نوشن؟",
      "faq.a1": "لا. كل شيء يعمل على خطة نوشن الشخصية المجانية.",
      "faq.q2": "هل يعمل فعلاً على الهاتف؟",
      "faq.a2": "نعم — وهذا كان قيداً في التصميم لا فكرة لاحقة. كل جدول يعرض ثلاثة أعمدة كحد أقصى مع تثبيت العنوان، واللوحات والتقاويم مبنية لشاشة صغيرة.",
      "faq.q3": "جامعتي لا تستخدم مقياس ٤٫٠ للمعدل.",
      "faq.a3": "افتح قاعدة بيانات المواد وعدّل صيغة «نقاط التقدير» لتطابق مقياسك. وكل ما يعتمد عليها يُعاد حسابه تلقائياً.",
      "faq.q4": "كيف أستلمه بعد الدفع؟",
      "faq.a4": "يصلك رابط قالب نوشن فور إتمام الدفع. اضغط «Duplicate» فيُنسخ النظام كاملاً — قواعد البيانات والصيغ والروابط — إلى مساحتك.",
      "faq.q5": "هل يمكنني حذف أجزاء لا أحتاجها؟",
      "faq.a5": "نعم. لا تعمل؟ احذف مساحة العمل. الصفحة الوحيدة التي يجب تركها هي «System Databases» لأن كل العروض تقرأ منها.",
      "faq.q6": "هل القالب باللغة العربية؟",
      "faq.a6": "القالب نفسه بالإنجليزية، وهي لغة التدريس في معظم الجامعات. هذه الصفحة ثنائية اللغة، ويمكنك إعادة تسمية أي صفحة أو حقل في نوشن إلى العربية خلال ثوانٍ.",

      "fin.title": "توقّف عن الترتيب. وابدأ الدراسة.",
      "fin.sub": "أعدّه مرة واحدة هذا الأسبوع، ثم اقضِ بقية الفصل وأنت تستخدمه فعلاً.",
      "fin.cta": "احصل على Student OS Pro",
    },
  };

  /* ── language ─────────────────────────────────────────── */
  var STORE_KEY = "studentos.lang";
  var els = document.querySelectorAll("[data-i18n]");
  var originals = null;

  function snapshotEnglish() {
    originals = {};
    els.forEach(function (el) {
      originals[el.getAttribute("data-i18n")] = el.innerHTML;
    });
  }

  function applyLang(lang) {
    var html = document.documentElement;
    var isAr = lang === "ar";

    html.lang = isAr ? "ar" : "en";
    html.dir = isAr ? "rtl" : "ltr";

    var dict = isAr ? I18N.ar : originals;
    els.forEach(function (el) {
      var key = el.getAttribute("data-i18n");
      var val = dict[key];
      if (val == null) return;
      if (HTML_KEYS[key] || !isAr) el.innerHTML = val;
      else el.textContent = val;
    });

    var label = document.querySelector("[data-lang-label]");
    if (label) label.textContent = isAr ? "English" : "العربية";

    try { localStorage.setItem(STORE_KEY, lang); } catch (e) { /* private mode */ }
  }

  snapshotEnglish();

  var saved = null;
  try { saved = localStorage.getItem(STORE_KEY); } catch (e) { /* ignore */ }
  var start = saved || CFG.defaultLang || "en";
  if (start === "ar") applyLang("ar");

  var toggle = document.getElementById("langToggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      applyLang(document.documentElement.lang === "ar" ? "en" : "ar");
    });
  }

  /* ── price ────────────────────────────────────────────── */
  var nowEl = document.querySelector("[data-price-now]");
  var wasEl = document.querySelector("[data-price-was]");
  if (nowEl && CFG.price) nowEl.textContent = CFG.price;
  if (wasEl) {
    if (CFG.priceWas) wasEl.textContent = CFG.priceWas;
    else wasEl.remove();
  }

  /* ── checkout ─────────────────────────────────────────── */
  document.querySelectorAll("[data-checkout]").forEach(function (btn) {
    var link = (CFG.stripePaymentLink || "").trim();
    if (link) {
      btn.href = link;
      btn.rel = "noopener";
      return;
    }
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      var isAr = document.documentElement.lang === "ar";
      alert(isAr
        ? "لم يتم ربط الدفع بعد.\n\nافتح ملف config.js وضع رابط Stripe Payment Link في الحقل stripePaymentLink."
        : "Checkout isn't connected yet.\n\nOpen config.js and paste your Stripe Payment Link into stripePaymentLink.");
    });
  });

  /* ── sticky nav shadow ────────────────────────────────── */
  var nav = document.getElementById("nav");
  if (nav) {
    var onScroll = function () {
      nav.classList.toggle("is-stuck", window.scrollY > 8);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ── scroll reveal ────────────────────────────────────── */
  var targets = document.querySelectorAll(
    ".card, .area, .split__col, .stat, .price, .faq, .preview"
  );
  if ("IntersectionObserver" in window) {
    targets.forEach(function (el) { el.classList.add("reveal"); });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-in");
        io.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });
    targets.forEach(function (el) { io.observe(el); });
  }

  /* ── year ─────────────────────────────────────────────── */
  var y = document.querySelector("[data-year]");
  if (y) y.textContent = new Date().getFullYear();
})();
