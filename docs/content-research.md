# Content Research — Nepali Government Services (Demo App)

**Research date:** 8 October 2026 (Ashoj 22, 2083 BS)
**Scope:** Four services (जन्म दर्ता, घर कर, नागरिकता, विवाह दर्ता) + office hours + public holidays for Oct–Dec 2026 (Ashoj–Poush 2083 BS).

**Verification policy:** Every fact below was checked against the cited sources. Anything not confirmed by a source is marked `⚠️ UNVERIFIED` and must not be presented as fact in the app. Known source conflicts are flagged inline with a "Conflict" note.

---

## 1. जन्म दर्ता (Janma Darta) — Birth Registration

### Overview

- Registered at the **ward office** (गाउँपालिका/नगरपालिका ward) as registrar; the **Department of National ID and Civil Registration (DoNIDCR)** runs the national system and an online pre-registration portal.
- Online application: **https://public.donidcr.gov.np/**
- **Free window:** registration within **35 days** of birth is free; after 35 days a late fee applies.
- Processing is commonly **same-day** at the ward counter when documents are complete (per official FAQ and ward practice).

### Documents Required

| Document | Notes |
|---|---|
| Parents' citizenship certificates (copies) | Father's and mother's citizenship — official FAQ Q13 |
| Informant's citizenship certificate | The person reporting the birth must show their own citizenship |
| Hospital birth report | For hospital births; for home birth, **khop (खोप/vaccination) card** accepted instead |
| Police report | Only required **if the father is unknown** (official FAQ Q13) |
| Parents' marriage certificate | **NOT mandatory** — explicitly confirmed in official FAQ Q14 |
| Online pre-registration slip | From public.donidcr.gov.np (optional but speeds up the counter) |

### Fees & Processing

| Item | Detail | Confidence |
|---|---|---|
| Registration within 35 days | Free | ✅ Verified (DoNIDCR FAQ) |
| Late registration fee | Reported as **~Rs 200** in some guides; other guides say **Rs 50–100** | ⚠️ UNVERIFIED — Conflict between sources; do not show a precise figure without checking the specific ward/municipality |
| Processing time | Often same-day when documents complete | ✅ Verified (DoNIDCR FAQ) |

### Key Points for the App

- Marriage certificate of parents is *not* a prerequisite — common misconception, explicitly debunked by the official FAQ.
- Home births: khop card substitutes for hospital report.
- Late fee amount varies by source → show "late fee applies (amount set locally)" rather than a number.

---

## Sources — जन्म दर्ता (Birth Registration)

- DoNIDCR official FAQ (Q13 documents, Q14 marriage certificate not mandatory, 35-day rule): https://donidcr.gov.np/pages/about-frequently-asked-questions--registration-5/
- DoNIDCR online application portal: https://public.donidcr.gov.np/
- 35-day deadline & ward steps (secondary): https://nepaldocsguide.blog/blog/register-birth-nepal-35-day-deadline

---

## 2. घर कर (Ghar Kar) — House / Property Tax

### Overview

- Officially **integrated property tax** (सम्पत्ति कर) on land + buildings, levied by municipalities/rural municipalities under the **Local Government Operation Act, 2017**; in force since **Shrawan 1, 2075** (merged former house tax + land tax).
- **Rates:** slab-based, generally **0.05% – 0.5%** of assessed property value; each local government fixes slabs in its annual budget.

Example slabs (as published by GFCS Nepal):

| Local government | Slabs |
|---|---|
| Kathmandu Metropolitan City | 0.05% up to Rs 5M · 0.15% Rs 5–10M · 0.25% Rs 10–20M · 0.35% above Rs 20M |
| Lalitpur Metropolitan City | 0.05% up to Rs 2M · 0.10% Rs 2–5M · 0.15% Rs 5–10M · 0.20% above Rs 10M |
| Pokhara Metropolitan City | 0.10% up to Rs 5M · 0.15% Rs 5–10M · 0.20% Rs 10–20M · 0.25% above Rs 20M |

### Documents Required

| Document | Notes |
|---|---|
| Citizenship certificate (owner) | Identity of the taxpayer |
| Land ownership certificate — लालपुरजा (Lalpurja) | Proof of ownership |
| Building permit | For properties with structures |
| Previous year's tax payment receipt | For assessment continuity |
| Property valuation report | If a valuation has been done |
| Property sketch map / photos | Sometimes requested by the local government |

### Payment Channels

| Channel | Options |
|---|---|
| Offline | Ward office / municipal revenue counter (most common) |
| Online | eSewa, ConnectIPS, Fonepay, Khalti; KMC e-service portal and municipal apps |

### Deadlines, Discounts & Penalties

| Item | Detail | Source basis |
|---|---|---|
| Annual deadline | **Varies by municipality**; generally aligned with the fiscal year ending **Ashadh end (mid-July)** | GFCS Nepal |
| Early-payment discount | e.g. Kathmandu Metropolitan City: **10% discount if paid by Ashoj end (mid-October)** | GFCS Nepal, attorney Nepal |
| Normal rate window | Until **Chaitra end (mid-April)** | GFCS Nepal |
| Penalty | **10% penalty after Chaitra end**; late-payment interest commonly **~15% p.a.** | GFCS Nepal, attorney Nepal |

> ⚠️ UNVERIFIED — The claim that house tax has "an annual deadline typically within **Magh**" could **not** be confirmed. No source reviewed sets a Magh deadline; sources say the deadline is set by each municipality, typically around **fiscal-year end (Ashadh/mid-July)**, with discount windows (Ashoj end) and penalty onset (Chaitra end). Do not state a Magh deadline in the app.

### Key Points for the App

- Tax is local: rates/deadlines differ per municipality — always name the municipality.
- Payment can be done online (wallets/banking) or at the ward/municipal counter.
- Best demo UX: "Pay before Ashoj end → 10% discount (KMC example); after Chaitra end → +10% penalty."

---

## Sources — घर कर (House / Property Tax)

- Attorney Nepal — Property Tax in Nepal (rates, integrated tax since Shrawan 1 2075, documents, online payment, discount/penalty): https://attorneynepal.com/publications/property-tax-in-nepal
- GFCS Nepal — Property Tax in Nepal (slabs, deadlines, KMC example, penalties): https://gfcsnepal.com/property-tax-in-nepal/
- Lalitpur Metropolitan City (official): https://lmc.gov.np/en/
- Kathmandu Metropolitan City — Department of Revenue: https://kathmandu.gov.np/en/departments/revenue

---

## 3. नागरिकता (Nagrikta) — Citizenship Certificate

### Overview

- Issued by the **District Administration Office (DAO / जिल्ला प्रशासन कार्यालय)** of the applicant's permanent-address district, after a **ward recommendation (सिफारिश)**.
- Commonest type: **citizenship by descent (उत्तराधिकारको आधारमा)** — both parents Nepali.

### Documents Required (citizenship by descent)

| Document | Notes |
|---|---|
| Application form | Filled at DAO |
| Father's citizenship certificate (copy) | Official DAO Bhaktapur list: बुवाको नागरिकता प्रमाणपत्र |
| Mother's citizenship certificate (copy) | आमाको नागरिकता प्रमाणपत्र |
| Birth registration certificate | जन्म दर्ता प्रमाणपत्र |
| Educational certificate | SEE / school character certificate (guides) |
| Ward recommendation (सिफारिश) | From the ward office |
| Passport-size photographs | Count varies by DAO |
| Identification by relative/witness | Applicant identified by a relative or witness at the DAO (notarynepal) |

Other types: by **birth**, **marriage** (foreign spouse), **naturalized**, **honorary**, **NRN**.

### Fees & Processing

| Item | Detail | Confidence |
|---|---|---|
| Government fee | DAO Lamjung official FAQ: **"No fees are required to obtain Nepali citizenship certificates"**; guides (notarynepal, prashasanpro) cite a **NPR 10 revenue stamp / application fee** | ✅ Both verified — present as "no statutory fee / NPR 10 revenue stamp only" with the DAO source preferred |
| Processing time | Guides: **same day (1–3 hrs)** to **1–2 working days** | ✅ Verified (2 concordant guides); DAO camps can process in bulk |
| Submission | In person at the DAO of permanent address | ✅ Verified |

### Key Points for the App

- Not a ward-level service — DAO is the issuing authority; ward only gives the recommendation.
- Fee is effectively zero to NPR 10 — never show a large fee.
- Amendments (name/spelling/mother's name) and duplicates go through the same DAO.

---

## Sources — नागरिकता (Citizenship)

- DAO Bhaktapur — Documents Required for New Citizenship (official list): https://daobhaktapur.moha.gov.np/en/post/documents-required-for-new-citizenship
- DAO Lamjung — Citizenship FAQ (official: no fee): https://daolamjung.moha.gov.np/en/post/citizenship-17
- Notary Nepal — Citizenship in Nepal 2026 (types, docs, process, NPR 10 stamp, 1–3 hrs): https://notarynepal.com/blog/citizenship-in-nepal
- Prashasan Pro — Citizenship Certificate (fee NPR 10, 1–2 days): https://prashasanpro.com/services/citizenship-certificate

---

## 4. विवाह दर्ता (Vivah Darta) — Marriage Registration

### Overview

Two routes:

1. **Ward office registration (गाउँपालिका/नगरपालिका ward):** both spouses register in person as informants — the normal, low-cost route.
2. **Court marriage (जिल्ला अदालत):** formal court process — used when ward route is unavailable, for foreigners, or by choice.

### Documents Required (DoNIDCR official FAQ, Q27–34)

| Document | Notes |
|---|---|
| Citizenship certificates — both spouses | Original + copy |
| Passport-size photos — both spouses | **2 auto-size photos each** (official FAQ) |
| Both spouses as informants | **Both must register/appear** — one cannot register alone (official FAQ) |
| Age proof | Both must be **20+ years** (official FAQ) |
| Power of Attorney (POA) | If one spouse is **abroad** |
| Court order | If one spouse **refuses** to register |
| Application form | Ward or court form as applicable |
| Witness details | Per ward/court practice |

### Fees & Processing

| Route | Fee | Processing | Confidence |
|---|---|---|---|
| Court marriage | **NPR 500** government/court filing fee | 1–3 working days (Nepali citizens); foreigners need 15-day residency → ~17–22 days | ✅ 3 concordant sources |
| Ward office registration | ⚠️ UNVERIFIED — no official fee figure confirmed; registration within 35 days is free of late fee, similar to birth registration | Usually same-day/quick at ward counter | Fee amount not verified — do not display a number |
| Late registration | 35-day free window, late fee after | per DoNIDCR FAQ | ✅ Verified |

### Key Points for the App

- Both spouses must physically register as informants — a common point of confusion.
- Age 20+ is the legal minimum (both).
- Court marriage's NPR 500 is a court filing fee only; total realistic cost with documents/notary is higher (lawaxion: NPR 1,000–10,500 total depending on applicant type).
- If a spouse is abroad → POA required; if a spouse refuses → court order required.

---

## Sources — विवाह दर्तа (Marriage Registration)

- DoNIDCR official FAQ (Q27–34: informants, age 20+, photos, POA, court order, 35-day rule): https://donidcr.gov.np/pages/about-frequently-asked-questions--registration-5/
- Court Marriage in Nepal (process, documents, cost): https://courtmarriageinnepal.com/
- Court marriage document checklist (NPR 500 filing fee): https://courtmarriageinnepal.com/blog/document-required-for-court-marriages-in-nepal
- Axion Partners — Court Marriage Process (NPR 500 fee, cost range): https://lawaxion.com/court-marriage-process-in-nepal/
- Law Neeti — Marriage Registration of Foreigner (NPR 500 fee): https://lawneeti.com/publications/marriage-registration-of-foreigner-in-nepal

---

## 5. सरकारी कार्यालय समय (Government Office Hours & Working Days)

### Current schedule (in force since 6 April 2026 / Chaitra 23, 2082)

| Item | Detail |
|---|---|
| Working hours | **9:00 AM – 5:00 PM, Monday – Friday** |
| Weekly holidays | **Saturday AND Sunday** (two-day weekend) |
| Effective from | Chaitra 23, 2082 (**6 April 2026**), Cabinet decision; published in Nepal Gazette (Rajpatra ref **26253**) by MoHA |
| Reason given | Petroleum/fuel conservation (global fuel-supply disruption) |
| Winter hours | **9:00 AM – 4:00 PM, Monday – Friday** during **Kartik 16 – Magh 15** ≈ **2 Nov 2026 – 29 Jan 2027** (seasonal pattern published on government portals) |
| Lunch break | **1:30 PM – 2:00 PM** (30 minutes; press reports say it was reduced from 1 hour to 30 minutes in the April 2026 change) |
| Passport dept. example | Department of Passports site: "MONDAY–FRIDAY (9 AM TO 5 PM)" |

### (a) Is the weekly holiday Saturday?

- **Yes — and now Sunday too.** Until April 2026 the weekly holiday was **Saturday only** (the 2083 holiday gazette, published 2 Mar 2026, lists public holidays "excluding Saturdays").
- Since **6 April 2026**, the weekly holidays are **Saturday + Sunday** for all government offices and educational institutions (Cabinet decision, gazette notice, multiple outlets).
- Historical color (ratopati): the Saturday holiday dates to Dev Shumsher; Bhim Shumsher institutionalized **Friday half-day + Saturday full holiday**.

### (b) Is there a Friday half-day?

**It WAS true until 5 April 2026 — it is NOT true anymore.**

| Period | Friday hours | Source |
|---|---|---|
| Until 5 Apr 2026 | **10:00 AM – 3:00 PM** (Friday half-day); Sun–Thu 10:00 AM – 5:00 PM; Saturday holiday | Pradhan & Associates alert of 10 Mar 2026 explicitly lists "Fridays: 10:00 AM to 3:00 PM"; MyRepublica (5 Apr 2026) also describes the prior schedule |
| Since 6 Apr 2026 | **9:00 AM – 5:00 PM** — Friday is a **full working day** | Cabinet decision; Radio Nepal ("gazette notice … weekly holidays Saturdays and Sundays"); Kathmandu Post; Khabarhub |

**Ambiguity note:** Many older websites, guides and even some government PDFs still show the Friday half-day. For the demo app, treat **current** behavior as full Friday 9–5 (Mon–Fri), and mention the old Friday half-day only as history. If the app must be "as-of-today correct": ✅ Friday = full day.

### (c) Lunch break norms

- **1:30 PM – 2:00 PM** — listed in Pradhan & Associates' office-hours block (10 Mar 2026) and reported again in the April 2026 change (30-minute break, down from 1 hour).
- Exact break timing can vary by office → app should say "typically 1:30–2:00 PM (30 min)". ⚠️ Minor: not every office publishes its break time.

### Seasonal winter change (relevant for the demo window)

- From **Kartik 16, 2083 = 2 Nov 2026** until **Magh 15, 2083 ≈ 29 Jan 2027**, offices close at **4:00 PM** instead of 5:00 PM (Mon–Fri). Pattern published in the footer of dop.gov.np: जाडो (कार्तिक १६ देखि माघ १५) सोम–शुक्र ०९:००–४:००; गर्मी (माघ १६ देखि कार्तिक १५) सोम–शुक्र ०९:००–५:००.
- So: **today (8 Oct 2026) → 9–5; from 2 Nov 2026 → 9–4.**

---

## Sources — Office Hours

- Pradhan & Associates — List of Public Holidays 2083 (includes "Government Office Hours and Break": Sun–Thu 10–5, **Fri 10–3**, winter 10–4 (Nov 2–Jan 29), **lunch 1:30–2:00 PM**): https://pradhanlaw.com/publications/list-of-public-holidays-2083-202627
- MyRepublica — Nepal moves to 9 AM–5 PM office hours with extended weekend (5 Apr 2026): https://myrepublica.nagariknetwork.com/news/govt-sets-new-office-hours-from-9-am-to-5-pm-29-97.html
- Kathmandu Post — Government announces two-day weekend amid fuel crisis (5 Apr 2026): https://kathmandupost.com/national/2026/04/05/government-announces-two-day-weekend-amid-fuel-crisis
- Radio Nepal — Government enforces new office hours from Monday (gazette notice, 6 Apr 2026): https://radionepalonline.com/en/2026/04/06/427683.html
- Khabarhub — New office timing begins: 9 am–5 pm workweek with two weekly holidays: https://english.khabarhub.com/2026/06/542831/
- NepalDocs — Government Office Time in Nepal (Rajpatra ref 26253, effective Chaitra 23): https://nepaldocs.com/government-office-time-in-nepal
- dop.gov.np footer — seasonal office hours (जाडो ०९:००–४:०० / गर्मी ०९:००–५:००, सोम–शुक्र): https://www.dop.gov.np/
- Department of Passports — official working hours (Mon–Fri 9 AM–5 PM): https://nepalpassport.gov.np/
- Ratopati — historical background on Saturday holiday & Friday half-day: https://english.ratopati.com/story/57398/the-decision-to-grant-two-days-off-a-week-had-previously-been-failed

---

## 6. सार्वजनिक बिदाहरू (Public Holidays) — Oct–Dec 2026 / Ashoj–Poush 2083 BS

### Official basis

- **Nepal Rajpatra, Khanda 75, Sankhya 67, Bhag 5**, published **2082-11-18 (2 March 2026)** by the Ministry of Home Affairs — "List of Public Holidays 2083" applicable 2083/01/01 (14 Apr 2026) – 2083/12/31 (13 Apr 2027). Gazette link (ref 26242): http://rajpatra.dop.gov.np/welcome/book/?ref=26242
- The notice contains **34 dated holidays excluding Saturdays** (Saturdays were the sole weekly holiday when it was published; since 6 Apr 2026 Sundays are weekly holidays too — see §5).
- Several religious holidays have **no fixed date in the gazette** (Eid, Guru Nanak Jayanti, Bhoto Jatra, etc.) — they are announced annually.

### Holidays, Oct–Dec 2026 window (dates from the gazette as mirrored by pradhanlaw + nepalhrm)

| Holiday (नेपाली) | English | BS date (2083) | AD date | Day | Notes |
|---|---|---|---|---|---|
| संविधान दिवस | Constitution Day | Ashoj 3 | **Sat, 19 Sep 2026** | Sat | Just before window; national holiday |
| घटस्थापना | Ghatasthapana (start of Dashain) | Ashoj 25 | **Sun, 11 Oct 2026** | Sun | Granted as a separate day, 6 days before the Dashain block |
| दशैं बिदा (७ दिन) | Dashain holiday block (7 days) | Ashoj 31 – Kartik 6 | **Sat, 17 Oct – Fri, 23 Oct 2026** | Sat–Fri | Phulpati through Dwadashi — *not* starting on Dashami |
| विजया दशमी / टीका | Vijaya Dashami (Tika) | **Kartik 4** | **Wed, 21 Oct 2026** | Wed | Middle of the Dashain block — the main Tika day |
| तिहार बिदा (५ दिन) | Tihar holiday block (5 days) | Kartik 22 – Kartik 26 | **Sun, 8 Nov – Thu, 12 Nov 2026** | Sun–Thu | Laxmi Puja through the day after Bhai Tika |
| भाइ टीका | Bhai Tika (end of Tihar) | Kartik 25 | **Wed, 11 Nov 2026** | Wed | Conflict: one social-media source said 10 Nov; gazette math (block ends Kartik 26 = day *after* Bhai Tika) + 4 sources confirm **11 Nov** |
| छठ पर्व | Chhath | Kartik 29 | **Sun, 15 Nov 2026** | Sun | Nationwide festival holiday |
| अन्तर्राष्ट्रिय अपाङ्गता दिवस | Intl. Day of Persons with Disabilities | Mangsir 17 | **Thu, 3 Dec 2026** | Thu | For employees with disabilities only |
| योमरी पुन्ही / धान्य पूर्णिमा / उधौलि पर्व | Yomari Punhi / Udhauli / Jyapu Diwas | Poush 9 | **Thu, 24 Dec 2026** | Thu | Nationwide |
| क्रिसमस डे | Christmas Day | Poush 10 | **Fri, 25 Dec 2026** | Fri | Nationwide |
| तमु ल्होसार | Tamu Lhosar (Gurung New Year) | Poush 15 | **Wed, 30 Dec 2026** | Wed | Nationwide; same day Dura Mhaipu Nakuma |

### Major national holidays outside the Oct–Dec window (same gazette)

| Holiday | BS (2083) | AD date | Day |
|---|---|---|---|
| नव वर्ष — Nepali New Year | Baishakh 1 | Tue, 14 Apr 2026 | Tue |
| बुद्ध जयन्ती / चण्डी पूर्णिमा / विश्व मजदुर दिवस | Baishakh 18 | Fri, 1 May 2026 | Fri |
| गणतन्त्र दिवस — Republic Day | Jestha 15 | Fri, 29 May 2026 | Fri |
| जनै पूर्णिमा / रक्षाबन्धन | Bhadra 12 | Fri, 28 Aug 2026 | Fri |
| श्रीकृष्ण जन्माष्टमी / गौरा पर्व | Bhadra 19 | Fri, 4 Sep 2026 | Fri |
| हरितालिका तीज (women only) | Bhadra 29 | Mon, 14 Sep 2026 | Mon |
| महाशिवरात्री | Falgun 22 | Sat, 6 Mar 2027 | Sat |
| फागु पूर्णिमा (होली) | Chaitra 7 (hills) / Chaitra 8 (Tarai) | Sun, 21 Mar 2027 (Tarai: Mon, 22 Mar) | — |

### Undated in the gazette (announce yearly)

- ⚠️ UNVERIFIED — **Eid ul-Fitr** (usually Mar/Apr/May), **Bakar Eid / Eid al-Adha** (usually Jun/Jul), **Mohammad Jayanti**, **Guru Nanak Jayanti** (usually Oct/Nov — *could* fall in the Oct–Dec 2026 window; no confirmed date), **Bhoto Jatra**, **Siruwa Pawani**. The gazette grants these as holidays but fixes no date ("To be determined"). Never display a specific date for these without a fresh official announcement.

### Key Points for the App

- Dashain = a **7-day block** (17–23 Oct), not a single day; Tika/Tuesday highlight = **Wed, 21 Oct 2026 (Kartik 4)**.
- Tihar = a **5-day block** (8–12 Nov); Bhai Tika = **Wed, 11 Nov 2026**.
- Holidays falling on Sat/Sun are absorbed into the weekend (since Apr 2026 the weekend is Sat+Sun).
- In Oct–Dec 2026 every major gazette holiday in the window falls Sun–Fri except Constitution Day (Sat, 19 Sep) — useful for a "days off" demo.

---

## Sources — Public Holidays

- MoHA — Government and Public Holidays (official): https://www.moha.gov.np/en/page/holidays
- Nepal Rajpatra text of the 2083 notice (ref 26242): http://rajpatra.dop.gov.np/welcome/book/?ref=26242
- Pradhan & Associates — List of Public Holidays, 2083 (2026/27) with AD dates (published 10 Mar 2026): https://pradhanlaw.com/publications/list-of-public-holidays-2083-202627
- NepalHRM — Public Holidays in Nepal 2083/84 (gazette-by-gazette with AD dates, blocks, clause refs): https://nepalhrm.com/tools/holiday-calendar/
- Nepali calendar (rat32) 2083 — festival-day AD dates (Dashami grid): https://nepalicalendar.rat32.com/2083/
- timeanddate.com — Bhai Tika / Dashain observances: https://www.timeanddate.com/holidays/nepal/bhai-tika-tihar

---

## All ⚠️ UNVERIFIED items (summary)

| # | Claim | Status |
|---|---|---|
| 1 | Birth registration **late fee = Rs 200** | ⚠️ Conflicting sources (~Rs 200 vs Rs 50–100) — amount is set locally; do not display a figure |
| 2 | House tax annual deadline **"typically within Magh"** | ⚠️ Not supported — sources say deadline varies by municipality, typically **Ashadh end (mid-July)**; discount by Ashoj end; penalty after Chaitra end |
| 3 | **Ward-office marriage registration fee** | ⚠️ No official figure verified (court marriage fee NPR 500 IS verified) — do not display a ward fee |
| 4 | **Eid / Guru Nanak Jayanti / Bhoto Jatra 2026 dates** | ⚠️ Undated in the gazette ("To be determined") — must be announced yearly |
| 5 | Exact **lunch break** at every office | ⚠️ 1:30–2:00 PM is the widely reported norm; individual offices may differ |
| 6 | Bhai Tika **11 Nov vs 10 Nov** | Minor source conflict resolved → **Wed, 11 Nov 2026** (gazette block math + 4 sources); one outlier said 10 Nov |
