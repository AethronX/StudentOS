/* ============================================================
   Student OS Pro — site configuration
   This is the ONLY file you need to edit to go live.
   ============================================================ */

window.STUDENTOS_CONFIG = {

  /* 1 ── STRIPE CHECKOUT ────────────────────────────────────
     Create a Payment Link in your Stripe Dashboard:
       Stripe → Payment links → + New → pick your product → Create link
     Then paste the link here. It looks like:
       https://buy.stripe.com/00g5kQ1a2b3c4d5e6f
     Until you set this, the buy button shows a friendly notice
     instead of sending anyone to a broken page.                */
  stripePaymentLink: "",

  /* 2 ── PRICE DISPLAY ──────────────────────────────────────
     Shown on the page only. Your real charge is whatever the
     Stripe Payment Link above is set to — keep them in sync.   */
  price:    "$29",
  priceWas: "$49",     // set to "" to hide the crossed-out price

  /* 3 ── NOTION TEMPLATE LINK ───────────────────────────────
     The duplicate-ready public link buyers receive. Deliver it
     via Stripe's post-payment confirmation page or receipt.
     Kept here for reference.                                   */
  notionTemplateUrl: "",

  /* 4 ── CONTACT / SOCIAL ───────────────────────────────────  */
  instagram: "",       // e.g. "https://instagram.com/yourhandle"
  supportEmail: "",    // e.g. "you@example.com"

  /* 5 ── DEFAULT LANGUAGE ───────────────────────────────────
     "en" or "ar". Visitors can switch, and their choice sticks. */
  defaultLang: "en",
};
