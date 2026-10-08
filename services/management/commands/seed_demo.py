"""Seed the demo database with researched, source-backed content.

Facts sourced from docs/content-research.md (Oct 2026):
- Office hours: 9 AM–5 PM Mon–Fri (since Cabinet decision of 6 Apr 2026,
  Rajpatra ref 26253); Sat + Sun weekly holidays; lunch typically 1:30–2:00 PM;
  winter hours 9 AM–4 PM from 2 Nov 2026.
- Holidays: Nepal Rajpatra 2083 notice (ref 26242), Oct–Dec 2026 window.
- Unverified fees/deadlines are intentionally kept vague ("set locally").
"""

from datetime import date, time

from django.core.management.base import BaseCommand

from services.models import ChecklistItem, Holiday, Service, SiteInfo, Step, WorkingDay


class Command(BaseCommand):
    help = "Load the four demo services, working days, holidays and site info."

    def handle(self, *args, **options):
        self.clear()
        self.working_days()
        self.holidays()
        self.site_info()
        self.services()
        self.stdout.write(self.style.SUCCESS("Seed complete ✓"))

    def clear(self):
        for model in (ChecklistItem, Step, WorkingDay, Holiday, SiteInfo, Service):
            model.objects.all().delete()

    # ---------------------------------------------------------------- days
    def working_days(self):
        # day: 0=Sunday .. 6=Saturday  (Nepali convention)
        for day, note_en, note_ne in [
            (0, "", ""),
            (1, "", ""),
            (2, "", ""),
            (3, "", ""),
            (4, "", ""),
            (5, "", ""),
            (6, "", ""),
        ]:
            WorkingDay.objects.create(
                day=day,
                open_time=None if day == 6 else time(9, 0),
                close_time=None if day == 6 else time(17, 0),
                note_en=note_en,
                note_ne=note_ne,
            )

    # ------------------------------------------------------------- holidays
    def holidays(self):
        rows = [
            # (date, name_en, name_ne, note_en, note_ne)
            (date(2026, 10, 11), "Ghatasthapana", "घटस्थापना", "Start of Dashain", "दशैं सुरु"),
            (date(2026, 10, 17), "Dashain festival", "दशैं बिदा", "Holiday block 17–23 Oct", "१७–२३ अक्टोबरसम्म बिदा"),
            (date(2026, 10, 21), "Vijaya Dashami — Tika", "विजया दशमी — टीका", "Main Tika day", "मुख्य टीका दिन"),
            (date(2026, 11, 8), "Tihar festival", "तिहार बिदा", "Holiday block 8–12 Nov", "८–१२ नोभेम्बरसम्म बिदा"),
            (date(2026, 11, 11), "Bhai Tika", "भाइ टीका", "End of Tihar", "तिहारको अन्त्य"),
            (date(2026, 11, 15), "Chhath Parva", "छठ पर्व", "—", "—"),
            (date(2026, 12, 24), "Yomari Punhi", "योमरी पुन्ही", "—", "—"),
            (date(2026, 12, 25), "Christmas Day", "क्रिसमस डे", "—", "—"),
            (date(2026, 12, 30), "Tamu Lhosar", "तमु ल्होसार", "Gurung New Year", "गुरुङ नयाँ वर्ष"),
        ]
        for r in rows:
            Holiday.objects.create(
                date=r[0],
                name_en=r[1],
                name_ne=r[2],
                note_en=r[3].replace("—", "") if r[3] != "—" else "",
                note_ne=r[4].replace("—", "") if r[4] != "—" else "",
            )

    # ----------------------------------------------------------- site info
    def site_info(self):
        SiteInfo.objects.create(
            key="hours",
            icon="🕘",
            label_en="Standard office hours",
            label_ne="मानक कार्यालय समय",
            value_en="9 AM–5 PM, Mon–Fri · Sat & Sun weekly holidays",
            value_ne="बिहान ९ – बेलुका ५, सोम–शुक्र · शनि र आइत साप्ताहिक बिदा",
            order=1,
        )
        SiteInfo.objects.create(
            key="winter",
            icon="❄️",
            label_en="Winter hours",
            label_ne="जाडो समय",
            value_en="From 2 Nov 2026: 9 AM–4 PM (Mon–Fri)",
            value_ne="२०८३ कात्तिक १६ देखि: बिहान ९ – बेलुका ४ (सोम–शुक्र)",
            order=2,
        )
        SiteInfo.objects.create(
            key="lunch",
            icon="🍽️",
            label_en="Lunch break",
            label_ne="खाजा विश्राम",
            value_en="Typically 1:30–2:00 PM (30 min)",
            value_ne="सामान्यतया १:३०–२:०० (३० मिनेट)",
            order=3,
        )

    # ------------------------------------------------------------- services
    def services(self):
        birth = Service.objects.create(
            slug="birth-certificate",
            icon="👶",
            name_en="Birth certificate",
            name_ne="जन्म दर्ता प्रमाणपत्र",
            tagline_en="Register a new birth or get a certificate copy",
            tagline_ne="नयाँ जन्म दर्ता वा प्रमाणपत्रको प्रति लिनुहोस्",
            overview_en=(
                "Birth registration happens at your ward office (the ward is the "
                "registrar). Registering within 35 days of birth is free; after 35 "
                "days a late fee applies."
            ),
            overview_ne=(
                "जन्म दर्ता तपाईंको वडा कार्यालयमा हुन्छ (वडा नै दर्ताकर्ता हो)। "
                "जन्म भएको ३५ दिनभित्र दर्ता निःशुल्क छ; ३५ दिनपछि ढिलो शुल्क लाग्छ।"
            ),
            office_en="Your ward office (वडा कार्यालय)",
            office_ne="तपाईंको वडा कार्यालय",
            fee_en="Free within 35 days. Late fee after that (set locally)",
            fee_ne="३५ दिनभित्र निःशुल्क। त्यसपछि ढिलो शुल्क (स्थानीय रूपमा तोकिन्छ)",
            timeline_en="Often same day when documents are complete",
            timeline_ne="कागजात पूरा भएमा प्रायः सोही दिन",
            deadline_en="Register within 35 days of birth to stay free",
            deadline_ne="जन्म भएको ३५ दिनभित्र दर्ता गर्नुहोस् — निःशुल्क",
            tips_en=(
                "Parents' marriage certificate is NOT required — a common misconception "
                "explicitly cleared by the official FAQ.\n"
                "For home births, bring the khop (खोप / vaccination) card instead of a "
                "hospital report.\n"
                "A police report is only needed if the father is unknown."
            ),
            tips_ne=(
                "अभिभावकको विवाह दर्ता प्रमाणपत्र आवश्यक छैन — आधिकारिक FAQ ले "
                "स्पष्ट पारेको सामान्य गलतधारणा हो।\nघरमै जन्मिएको भए अस्पताल रिपोर्टको "
                "सट्टा खोप (khop) कार्ड ल्याउनुहोस्।\nबुवा अज्ञात भए मात्र प्रहरी "
                "रिपोर्ट चाहिन्छ।"
            ),
            order=1,
        )
        self.birth_checklist(birth)
        self.birth_steps(birth)

        tax = Service.objects.create(
            slug="house-tax",
            icon="🏠",
            name_en="House & property tax",
            name_ne="घर कर (सम्पत्ति कर)",
            tagline_en="Pay your annual property tax on time",
            tagline_ne="वार्षिक सम्पत्ति कर समयमा तिर्नुहोस्",
            overview_en=(
                "The integrated property tax on land and buildings is levied by your "
                "municipality or rural municipality under the Local Government "
                "Operation Act, 2017. Rates are slab-based and set by each local "
                "government in its annual budget."
            ),
            overview_ne=(
                "जग्गा र भवनमा लाग्ने एकीकृत सम्पत्ति कर (घर कर) स्थानीय सरकार "
                "सञ्चालन ऐन, २०७४ अनुसार तपाईंको नगरपालिका/गाउँपालिकाले लिन्छ। दर "
                "स्ल्याब-आधारित हुन्छ र प्रत्येक स्थानीय सरकारले वार्षिक बजेटमा तोक्छ।"
            ),
            office_en="Your ward office or municipal revenue counter",
            office_ne="तपाईंको वडा कार्यालय वा नगरपालिकाको राजस्व काउन्टर",
            fee_en="Slab-based, typically 0.05%–0.5% of assessed value",
            fee_ne="स्ल्याब-आधारित, सामान्यतया मूल्याङ्कनको ०.०५%–०.५%",
            timeline_en="Same day at the counter, or instantly online",
            timeline_ne="काउन्टरमा सोही दिन, वा अनलाइन तुरुन्तै",
            deadline_en="Usually fiscal-year end (mid-July) — varies by municipality",
            deadline_ne="सामान्यतया आर्थिक वर्षको अन्त्य (मध्य-साउन) — नगरपालिका अनुसार फरक",
            tips_en=(
                "Kathmandu example: 10% discount if paid by Ashoj-end (mid-October), "
                "normal rate until Chaitra-end, then ~10% penalty.\n"
                "Rates and deadlines differ by municipality — check yours.\n"
                "Pay at the counter or online (eSewa, Khalti, Fonepay, ConnectIPS)."
            ),
            tips_ne=(
                "काठमाडौंको उदाहरण: असोज मसान्त (मध्य-अक्टोबर) सम्म तिरे १०% छुट, "
                "चैत मसान्तसम्म सामान्य दर, त्यसपछि करिब १०% जरिवाना।\nदर र म्याद "
                "नगरपालिका अनुसार फरक हुन्छ — आफ्नो पालिका हेर्नुहोस्।\nकाउन्टर वा "
                "अनलाइन (eSewa, Khalti, Fonepay, ConnectIPS) मा तिर्न सकिन्छ।"
            ),
            order=2,
        )
        self.tax_checklist(tax)
        self.tax_steps(tax)

        cit = Service.objects.create(
            slug="citizenship",
            icon="🪪",
            name_en="Citizenship certificate",
            name_ne="नागरिकता प्रमाणपत्र",
            tagline_en="Apply for citizenship by descent",
            tagline_ne="उत्तराधिकारको आधारमा नागरिकताका लागि आवेदन",
            overview_en=(
                "Citizenship by descent is issued by the District Administration "
                "Office (DAO) of your permanent-address district, after a ward "
                "recommendation (सिफारिश). Both parents must be Nepali citizens."
            ),
            overview_ne=(
                "उत्तराधिकारको आधारमा नागरिकता दर्ता स्थायी ठेगाना भएको जिल्लाको "
                "जिल्ला प्रशासन कार्यालय (DAO) ले वडाको सिफारिशपछि जारी गर्छ। दुवै "
                "अभिभावक नेपाली नागरिक हुनुपर्छ।"
            ),
            office_en="District Administration Office (जिल्ला प्रशासन कार्यालय) of your permanent address",
            office_ne="स्थायी ठेगानाको जिल्ला प्रशासन कार्यालय (DAO)",
            fee_en="No statutory fee — NPR 10 revenue stamp only",
            fee_ne="कुनै कानुनी शुल्क छैन — केवल रु. १० रेभिन्यु स्टाम्प",
            timeline_en="Same day (1–3 hrs) to 1–2 working days",
            timeline_ne="सोही दिन (१–३ घण्टा) देखि १–२ कार्यदिवस",
            deadline_en="",
            deadline_ne="",
            tips_en=(
                "The ward only gives the recommendation — the DAO issues the "
                "certificate itself.\n"
                "Amendments (name, spelling, mother's name) and duplicates go through "
                "the same DAO."
            ),
            tips_ne=(
                "वडाले मात्र सिफारिश दिन्छ — प्रमाणपत्र DAO ले नै जारी गर्छ।\n"
                "नाम/हिज्जे/आमाको नाम सच्याउने र डुप्लिकेट पनि सोही DAO बाटै हुन्छ।"
            ),
            order=3,
        )
        self.citizenship_checklist(cit)
        self.citizenship_steps(cit)

        mar = Service.objects.create(
            slug="marriage-registration",
            icon="💍",
            name_en="Marriage registration",
            name_ne="विवाह दर्ता",
            tagline_en="Register your marriage at the ward or court",
            tagline_ne="वडा वा अदालतमा विवाह दर्ता गर्नुहोस्",
            overview_en=(
                "Two routes: ward-office registration (the normal, low-cost route) or "
                "court marriage. In both cases both spouses must appear and register "
                "themselves as informants."
            ),
            overview_ne=(
                "दुई मार्ग: वडा कार्यालय दर्ता (सामान्य र सस्तो) वा अदालती विवाह। "
                "दुवै अवस्थामा दुवै पति-पत्नी आफैं उपस्थित भई दर्ता गराउनुपर्छ।"
            ),
            office_en="Your ward office, or the District Court (जिल्ला अदालत)",
            office_ne="तपाईंको वडा कार्यालय, वा जिल्ला अदालत",
            fee_en="Court marriage: NPR 500 filing fee. Ward route: no official fee published",
            fee_ne="अदालती विवाह: रु. ५०० दर्ता शुल्क। वडा मार्ग: आधिकारिक शुल्क प्रकाशित छैन",
            timeline_en="Ward: usually same day. Court: 1–3 working days (Nepali citizens)",
            timeline_ne="वडा: प्रायः सोही दिन। अदालत: १–३ कार्यदिवस (नेपाली नागरिक)",
            deadline_en="Register within 35 days of the marriage to avoid late fee",
            deadline_ne="ढिलो शुल्कबाट बच्न विवाह भएको ३५ दिनभित्र दर्ता गर्नुहोस्",
            tips_en=(
                "Both spouses MUST appear in person — one spouse cannot register alone "
                "(official FAQ).\n"
                "Both spouses must be at least 20 years old.\n"
                "Spouse abroad → power of attorney required. Spouse refuses → court "
                "order required."
            ),
            tips_ne=(
                "दुवै पति-पत्नी आफैं उपस्थित हुनैपर्छ — एक्लै दर्ता गराउन सकिँदैन "
                "(आधिकारिक FAQ)।\nदुवैको उमेर कम्तीमा २० वर्ष हुनुपर्छ।\nपति/पत्नी "
                "विदेशमा भए → अधिकृत वकिलनामा चाहिन्छ। दर्ता गर्न अस्वीकार गरे → "
                "अदालतको आदेश चाहिन्छ।"
            ),
            order=4,
        )
        self.marriage_checklist(mar)
        self.marriage_steps(mar)

    # --------------------------------------------------- checklists + steps
    def add_check(self, svc, group_en, group_ne, label_en, label_ne,
                  *notes, required=True, order=0):
        note_en = ""
        note_ne = ""
        for n in notes:
            if isinstance(n, int):  # bare order int squeezed into the note slots
                order = n
            elif not note_en:
                note_en = n
            elif not note_ne:
                note_ne = n
        ChecklistItem.objects.create(
            service=svc,
            group_en=group_en,
            group_ne=group_ne,
            label_en=label_en,
            label_ne=label_ne,
            note_en=note_en,
            note_ne=note_ne,
            required=required,
            order=order,
        )

    def add_step(self, svc, title_en, title_ne, detail_en="", detail_ne="", order=0):
        Step.objects.create(
            service=svc, title_en=title_en, title_ne=title_ne,
            detail_en=detail_en, detail_ne=detail_ne, order=order,
        )

    def birth_checklist(self, s):
        c = self.add_check
        c(s, "Your documents", "तपाईंका कागजातहरू",
          "Parents' citizenship certificates", "अभिभावकको नागरिकता प्रमाणपत्र",
          "Father's and mother's, copies fine", "बुवा र आमाको, प्रतिलिपि पुग्छ", 1)
        c(s, "Your documents", "तपाईंका कागजातहरू",
          "Your own citizenship certificate", "तपाईंकै नागरिकता प्रमाणपत्र",
          "You report the birth as informant", "तपाईं informant का रूपमा दर्ता गराउनुहुन्छ", 2)
        c(s, "Birth evidence", "जन्म प्रमाण",
          "Hospital birth report", "अस्पतालको जन्म रिपोर्ट",
          "For hospital births", "अस्पतालमा जन्मिएको भए", 3)
        c(s, "Birth evidence", "जन्म प्रमाण",
          "Khop (खोप) vaccination card", "खोप (khop) कार्ड",
          "For home births instead of the hospital report", "घरमै जन्मिएको भए अस्पताल रिपोर्टको सट्टा",
          required=False, order=4)
        c(s, "Birth evidence", "जन्म प्रमाण",
          "Police report", "प्रहरी रिपोर्ट",
          "Only if the father is unknown", "बुवा अज्ञात भए मात्र", required=False, order=5)
        c(s, "Useful extras", "काम लाग्ने कागजात",
          "Online pre-registration slip", "अनलाइन प्रि-दर्ता स्लिप",
          "From public.donidcr.gov.np — optional but faster", "public.donidcr.gov.np बाट — ऐच्छिक तर छिटो",
          required=False, order=6)
        c(s, "Useful extras", "काम लाग्ने कागजात",
          "Parents' marriage certificate", "अभिभावकको विवाह दर्ता प्रमाणपत्र",
          "Not required (official FAQ)", "आवश्यक छैन (आधिकारिक FAQ)",
          required=False, order=7)

    def birth_steps(self, s):
        a = self.add_step
        a(s, "Pre-register online (optional)", "अनलाइन प्रि-दर्ता गर्नुहोस् (ऐच्छिक)",
          "Fill the form at public.donidcr.gov.np to save time at the counter.",
          "public.donidcr.gov.np मा फारम भर्नुहोस् — काउन्टरमा समय बच्छ।", 1)
        a(s, "Gather your documents", "कागजात जुटाउनुहोस्",
          "See the checklist — parents' citizenship and birth evidence are the key items.",
          "सूची हेर्नुहोस् — अभिभावकको नागरिकता र जन्म प्रमाण मुख्य कागजात हुन्।", 2)
        a(s, "Go to your ward office", "वडा कार्यालय जानुहोस्",
          "Open Mon–Fri 9 AM–5 PM. Bring everything in the checklist.",
          "सोम–शुक्र बिहान ९–बेलुका ५ खुल्छ। सूचीका सबै कागजात लैजानुहोस्।", 3)
        a(s, "Submit at the counter", "काउन्टरमा बुझाउनुहोस्",
          "The ward officer checks the documents and enters the registration.",
          "कर्मचारीले कागजात जाँचेर दर्ता गराउँछ।", 4)
        a(s, "Collect your certificate", "प्रमाणपत्र लिनुहोस्",
          "Often issued the same day when everything is complete.",
          "सबै पूरा भए प्रायः सोही दिन नै पाइन्छ।", 5)

    def tax_checklist(self, s):
        c = self.add_check
        c(s, "Your documents", "तपाईंका कागजातहरू",
          "Citizenship certificate (owner)", "नागरिकता प्रमाणपत्र (मालिकको)", 1)
        c(s, "Your documents", "तपाईंका कागजातहरू",
          "Land ownership certificate — Lalpurja", "जग्गा धनीपुर्जा — लालपुरजा", 2)
        c(s, "Your documents", "तपाईंका कागजातहरू",
          "Building permit", "भवन निर्माण अनुमति",
          "For properties with structures", "भवन भएको सम्पत्तिका लागि", required=False, order=3)
        c(s, "Your documents", "तपाईंका कागजातहरू",
          "Previous year's tax receipt", "अघिल्लो वर्षको कर भुक्तानी रसिद",
          "Helps with assessment continuity", "मूल्याङ्कन निरन्तरताका लागि", required=False, order=4)
        c(s, "Your documents", "तपाईंका कागजातहरू",
          "Property sketch / photos", "सम्पत्तिको नक्सा / फोटो",
          "Sometimes requested by the local government", "कहिलेकाहीं पालिकाले माग्छ", required=False, order=5)
        c(s, "Payment", "भुक्तानी",
          "Payment method", "भुक्तानी विधि",
          "Cash at counter, or wallet app for online payment", "काउन्टरमा नगद, वा अनलाइनका लागि वालेट", order=6)

    def tax_steps(self, s):
        a = self.add_step
        a(s, "Get your tax assessed", "कर मूल्याङ्कन गराउनुहोस्",
          "The revenue counter calculates your slab-based tax from the property value.",
          "राजस्व काउन्टरले सम्पत्ति मूल्यबाट स्ल्याब-आधारित कर गणना गर्छ।", 1)
        a(s, "Bring your documents", "कागजात लैजानुहोस्",
          "Lalpurja + citizenship are the essentials.",
          "लालपुरजा र नागरिकता मुख्य कागजात हुन्।", 2)
        a(s, "Pay by the deadline", "म्यादभित्र तिर्नुहोस्",
          "Check your municipality for the deadline and any early-payment discount.",
          "आफ्नो पालिकाको म्याद र छुट अवधि जाँच्नुहोस्।", 3)
        a(s, "Keep the receipt", "रसिद राख्नुहोस्",
          "You will need last year's receipt for next year's assessment.",
          "अर्को वर्षको मूल्याङ्कनका लागि रसिद राख्नुहोस्।", 4)

    def citizenship_checklist(self, s):
        c = self.add_check
        c(s, "Your documents", "तपाईंका कागजातहरू",
          "Application form", "आवेदन फारम",
          "Filled at the DAO", "DAO मा भर्नुपर्छ", 1)
        c(s, "Your documents", "तपाईंका कागजातहरू",
          "Father's citizenship certificate", "बुवाको नागरिकता प्रमाणपत्र",
          "Copy, per DAO list", "प्रतिलिपि, DAO सूची अनुसार", 2)
        c(s, "Your documents", "तपाईंका कागजातहरू",
          "Mother's citizenship certificate", "आमाको नागरिकता प्रमाणपत्र",
          "Copy, per DAO list", "प्रतिलिपि, DAO सूची अनुसार", 3)
        c(s, "Your documents", "तपाईंका कागजातहरू",
          "Birth registration certificate", "जन्म दर्ता प्रमाणपत्र", 4)
        c(s, "Your documents", "तपाईंका कागजातहरू",
          "Educational certificate", "शैक्षिक प्रमाणपत्र",
          "SEE / school character certificate", "एसईई / चरित्र प्रमाणपत्र", required=False, order=5)
        c(s, "Your documents", "तपाईंका कागजातहरू",
          "Passport-size photographs", "पासपोर्ट साइजका फोटो",
          "Count varies by DAO", "संख्या DAO अनुसार फरक", order=6)
        c(s, "Your documents", "तपाईंका कागजातहरू",
          "Ward recommendation (सिफारिश)", "वडाको सिफारिश", 7)
        c(s, "At the DAO", "DAO मा",
          "Identification by a relative/witness", "आफन्त/साक्षीको चिनारी",
          "You are identified at the DAO", "DAO मा चिनारी गराउनुपर्छ", 8)
        c(s, "At the DAO", "DAO मा",
          "NPR 10 revenue stamp", "रु. १० रेभिन्यु स्टाम्प", 9)

    def citizenship_steps(self, s):
        a = self.add_step
        a(s, "Get the ward recommendation", "वडाको सिफारिश लिनुहोस्",
          "Your ward office issues the सिफारिश for the DAO.",
          "वडा कार्यालयले DAO का लागि सिफारिश दिन्छ।", 1)
        a(s, "Go to the DAO", "जिल्ला प्रशासन कार्यालय जानुहोस्",
          "Of your permanent-address district, Mon–Fri 9 AM–5 PM.",
          "स्थायी ठेगानाको जिल्ला, सोम–शुक्र बिहान ९–बेलुका ५।", 2)
        a(s, "Be identified", "चिनारी गराउनुहोस्",
          "A relative or witness identifies you before the officer.",
          "आफन्त वा साक्षीले कर्मचारीसमक्ष चिनारी दिन्छ।", 3)
        a(s, "Collect your certificate", "प्रमाणपत्र लिनुहोस्",
          "Often same day (1–3 hrs) or within 1–2 working days.",
          "प्रायः सोही दिन (१–३ घण्टा) वा १–२ कार्यदिवसभित्र।", 4)

    def marriage_checklist(self, s):
        c = self.add_check
        c(s, "Both spouses", "दुवै पति-पत्नी",
          "Citizenship certificates — both spouses", "नागरिकता प्रमाणपत्र — दुवैको",
          "Original + copy", "मूल + प्रतिलिपि", 1)
        c(s, "Both spouses", "दुवै पति-पत्नी",
          "Passport-size photos — 2 each", "पासपोर्ट साइजका फोटो — २/२ वटा",
          "Per official FAQ", "आधिकारिक FAQ अनुसार", 2)
        c(s, "Both spouses", "दुवै पति-पत्नी",
          "Both spouses appear in person", "दुवै आफैं उपस्थित हुनुपर्छ",
          "One spouse cannot register alone", "एक्लै दर्ता गराउन सकिँदैन", 3)
        c(s, "Both spouses", "दुवै पति-पत्नी",
          "Age proof — 20+ years", "उमेर प्रमाण — २०+ वर्ष",
          "Both spouses must be at least 20", "दुवैको उमेर कम्तीमा २० हुनुपर्छ", 4)
        c(s, "Special cases", "विशेष अवस्था",
          "Power of attorney", "अधिकृत वकिलनामा",
          "If one spouse is abroad", "एक जना विदेशमा भए", required=False, order=5)
        c(s, "Special cases", "विशेष अवस्था",
          "Court order", "अदालतको आदेश",
          "If one spouse refuses to register", "एक जनाले दर्ता गर्न अस्वीकार गरे", required=False, order=6)
        c(s, "Court marriage only", "अदालती विवाह मात्र",
          "Application form + witnesses", "आवेदन फारम + साक्षी",
          "As per the court's practice", "अदालतको अभ्यास अनुसार", required=False, order=7)

    def marriage_steps(self, s):
        a = self.add_step
        a(s, "Choose your route", "मार्ग रोज्नुहोस्",
          "Ward office (normal route) or District Court (court marriage).",
          "वडा कार्यालय (सामान्य) वा जिल्ला अदालत (अदालती विवाह)।", 1)
        a(s, "Gather documents", "कागजात जुटाउनुहोस्",
          "Both spouses' citizenship, photos, age proof.",
          "दुवैको नागरिकता, फोटो, उमेर प्रमाण।", 2)
        a(s, "Go together", "सँगै जानुहोस्",
          "Both spouses must appear in person to register as informants.",
          "दुवै पति-पत्नी आफैं उपस्थित भई informant का रूपमा दर्ता गराउनुपर्छ।", 3)
        a(s, "Collect the certificate", "प्रमाणपत्र लिनुहोस्",
          "Ward: often same day. Court: 1–3 working days.",
          "वडा: प्रायः सोही दिन। अदालत: १–३ कार्यदिवस।", 4)