# -*- coding: utf-8 -*-
"""
الفرق بين مربعين — تطبيق تفاعلي شامل بـ Streamlit
- إعداد الطالبات: أية، رفيف، سارة، هزار
"""

import streamlit as st
import random
import math
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ==========================================================
# 1) إعدادات الصفحة والتصميم العامة
# ==========================================================
st.set_page_config(
    page_title="الفرق بين مربعين - تطبيق تفاعلي",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تخصيص الاتجاه من اليمين إلى اليسار (RTL) مع ألوان داكنة وجذابة
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .stApp {
        background-color: #0f172a;
        color: #e2e8f0;
    }
    .main-header {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 12px;
        border-right: 6px solid #38bdf8;
        margin-bottom: 20px;
        text-align: center;
    }
    .metric-box {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    .card-box {
        background-color: #1e293b;
        border: 1px solid #38bdf8;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)


# ==========================================================
# 2) منطق توليد الأسئلة (120 سؤالاً)
# ==========================================================

def term(coef, var, power):
    """تنسيق حد جبري مثل 9س^2"""
    c = "" if coef == 1 else str(coef)
    if not var:
        return str(coef)
    p = "" if power == 1 else f"^{power}"
    return f"{c}{var}{p}"


class Question:
    def __init__(self, expr, answer, category, level, steps, hint):
        self.expr = expr  # المقدار المطلوب تحليله
        self.answer = answer  # الحل الصحيح
        self.category = category  # التصنيف
        self.level = level  # المستوى 1..3
        self.steps = steps  # خطوات الحل
        self.hint = hint  # تلميح
        self.options = []  # خيارات الاختبار


VARS = ["س", "ص", "ع", "ل"]


@st.cache_data
def build_bank():
    """يبني 120 سؤالاً موزعة على أربعة تصنيفات"""
    bank = []
    rnd = random.Random(2026)  # بذرة ثابتة لتكرار نفس الأسئلة

    # ---------- (أ) تحليل مباشر: a²س² - b² ----------
    for i in range(35):
        a = rnd.choice([1, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12])
        b = rnd.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13])
        v = VARS[i % len(VARS)]
        left = term(a * a, v, 2)
        right = b * b
        expr = f"{left} - {right}"
        ans = f"({term(a, v, 1)} - {b})({term(a, v, 1)} + {b})"
        steps = [
            f"نتحقق أن الحدّين مربعان كاملان: {left} = ({term(a, v, 1)})²  و  {right} = ({b})².",
            "نطبّق القاعدة: أ² − ب² = (أ − ب)(أ + ب).",
            f"أ = {term(a, v, 1)}  ،  ب = {b}.",
            f"الناتج: {ans}.",
        ]
        hint = f"ما جذر {left}؟ وما جذر {right}؟ ثم ضع الجذرين في (أ−ب)(أ+ب)."
        bank.append(Question(expr, ans, "تحليل مباشر", 1, steps, hint))

    # ---------- (ب) إخراج العامل المشترك أولاً ----------
    for i in range(35):
        k = rnd.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 12])
        a = rnd.choice([1, 2, 3, 4, 5, 6])
        b = rnd.choice([1, 2, 3, 4, 5, 7, 8, 9])
        v = VARS[(i + 1) % len(VARS)]
        expr = f"{term(k * a * a, v, 2)} - {k * b * b}"
        inner = f"({term(a, v, 1)} - {b})({term(a, v, 1)} + {b})"
        ans = f"{k}{inner}"
        steps = [
            f"العامل المشترك الأكبر بين {k * a * a} و {k * b * b} هو {k}.",
            f"نُخرجه: {expr} = {k}({term(a * a, v, 2)} - {b * b}).",
            f"داخل القوس فرق بين مربعين: {term(a * a, v, 2)} = ({term(a, v, 1)})²  و  {b * b} = ({b})².",
            f"الناتج النهائي: {ans}.",
        ]
        hint = f"لا تحلّل قبل إخراج العامل المشترك {k}."
        bank.append(Question(expr, ans, "عامل مشترك (G.C.F)", 2, steps, hint))

    # ---------- (ج) حساب ذهني للأعداد: n² - m² ----------
    pairs = [(101, 99), (52, 48), (75, 25), (63, 37), (120, 80), (45, 35),
             (210, 190), (99, 1), (86, 14), (55, 45), (31, 29), (150, 50),
             (77, 23), (64, 36), (98, 2), (250, 150), (41, 39), (88, 12),
             (72, 28), (135, 65), (96, 4), (58, 42), (111, 89), (140, 60),
             (33, 27)]
    for (n, m) in pairs:
        expr = f"{n}² - {m}²"
        d, s = n - m, n + m
        ans = f"{d} × {s} = {d * s}"
        steps = [
            "نستخدم القاعدة بدل الحساب الطويل: أ² − ب² = (أ − ب)(أ + ب).",
            f"أ − ب = {n} − {m} = {d}.",
            f"أ + ب = {n} + {m} = {s}.",
            f"الناتج: {d} × {s} = {d * s}.",
        ]
        hint = f"اطرح العددين ثم اجمعهما، واضرب الناتجين ({d} و {s})."
        bank.append(Question(expr, ans, "حساب ذهني للأعداد", 2, steps, hint))

    # ---------- (د) أسس أعلى وكسور ----------
    high = [
        ("س^4 - 16", "(س - 2)(س + 2)(س² + 4)",
         ["س⁴ = (س²)²  و  16 = 4².",
          "أولاً: (س² − 4)(س² + 4).",
          "القوس الأول ما زال فرق بين مربعين: س² − 4 = (س − 2)(س + 2).",
          "الناتج التام: (س − 2)(س + 2)(س² + 4)."],
         "حلّل مرتين: الناتج الأول ليس تاماً بعد."),
        ("16س^4 - 81", "(2س - 3)(2س + 3)(4س² + 9)",
         ["16س⁴ = (4س²)²  و  81 = 9².",
          "(4س² − 9)(4س² + 9).",
          "4س² − 9 = (2س − 3)(2س + 3).",
          "الناتج: (2س − 3)(2س + 3)(4س² + 9)."],
         "بعد التحليل الأول، افحص كل قوس مجدداً."),
        ("س^6 - 64", "(س³ - 8)(س³ + 8)",
         ["س⁶ = (س³)²  و  64 = 8².",
          "الناتج: (س³ − 8)(س³ + 8)."],
         "اقسم الأس 6 على 2 لتحصل على س³."),
        ("س^2/9 - 25", "(س/3 - 5)(س/3 + 5)",
         ["س²/9 = (س/3)²  و  25 = 5².",
          "الناتج: (س/3 − 5)(س/3 + 5)."],
         "جذر المقام 9 هو 3، فالجذر هو س/3."),
        ("4س^2/25 - 1", "(2س/5 - 1)(2س/5 + 1)",
         ["4س²/25 = (2س/5)²  و  1 = 1².",
          "الناتج: (2س/5 − 1)(2س/5 + 1)."],
         "جذر البسط 4س² هو 2س وجذر المقام 25 هو 5."),
        ("س^2 - ص^2", "(س - ص)(س + ص)",
         ["الحدّان مربعان: (س)² و (ص)².",
          "الناتج: (س − ص)(س + ص)."],
         "الصورة الأساسية للقاعدة."),
        ("49س^2 - 36ص^2", "(7س - 6ص)(7س + 6ص)",
         ["49س² = (7س)²  و  36ص² = (6ص)².",
          "الناتج: (7س − 6ص)(7س + 6ص)."],
         "خذ جذر كل حد مع متغيّره."),
        ("س^8 - 1", "(س - 1)(س + 1)(س² + 1)(س^4 + 1)",
         ["س⁸ = (س⁴)²  و  1 = 1².",
          "(س⁴ − 1)(س⁴ + 1).",
          "س⁴ − 1 = (س² − 1)(س² + 1)، و س² − 1 = (س − 1)(س + 1).",
          "الناتج التام: (س − 1)(س + 1)(س² + 1)(س⁴ + 1)."],
         "كرّر التحليل ثلاث مرات حتى لا يبقى فرق بين مربعين."),
        ("100 - س^2", "(10 - س)(10 + س)",
         ["الترتيب مقلوب: العدد أولاً.",
          "100 = 10²  و  س² = (س)².",
          "الناتج: (10 − س)(10 + س)."],
         "لا يهم الترتيب، المهم أيّهما المطروح."),
        ("س^2 ص^2 - 121", "(سص - 11)(سص + 11)",
         ["س²ص² = (سص)²  و  121 = 11².",
          "الناتج: (سص − 11)(سص + 11)."],
         "اجمع المتغيّرين تحت جذر واحد: سص."),
        ("(س+1)^2 - 9", "(س - 2)(س + 4)",
         ["أ = (س + 1)  ،  ب = 3.",
          "(س + 1 − 3)(س + 1 + 3).",
          "نبسّط: (س − 2)(س + 4)."],
         "اعتبر القوس كلّه حدّاً واحداً (أ)."),
        ("س^4 - ص^4", "(س - ص)(س + ص)(س² + ص²)",
         ["س⁴ = (س²)²  و  ص⁴ = (ص²)².",
          "(س² − ص²)(س² + ص²).",
          "س² − ص² = (س − ص)(س + ص).",
          "الناتج: (س − ص)(س + ص)(س² + ص²)."],
         "القوس الأول يقبل تحليلاً إضافياً."),
        ("0.25س^2 - 0.09", "(0.5س - 0.3)(0.5س + 0.3)",
         ["0.25س² = (0.5س)²  و  0.09 = (0.3)².",
          "الناتج: (0.5س − 0.3)(0.5س + 0.3)."],
         "جذر 0.25 = 0.5 وجذر 0.09 = 0.3."),
        ("س^10 - 1", "(س^5 - 1)(س^5 + 1)",
         ["س¹⁰ = (س⁵)²  و  1 = 1².",
          "الناتج: (س⁵ − 1)(س⁵ + 1)."],
         "اقسم الأس على 2."),
        ("9/16 - س^2", "(3/4 - س)(3/4 + س)",
         ["9/16 = (3/4)²  و  س² = (س)².",
          "الناتج: (3/4 − س)(3/4 + س)."],
         "جذر الكسر = جذر البسط على جذر المقام."),
        ("81س^4 - 16ص^4", "(3س - 2ص)(3س + 2ص)(9س² + 4ص²)",
         ["81س⁴ = (9س²)²  و  16ص⁴ = (4ص²)².",
          "(9س² − 4ص²)(9س² + 4ص²).",
          "9س² − 4ص² = (3س − 2ص)(3س + 2ص).",
          "الناتج: (3س − 2ص)(3س + 2ص)(9س² + 4ص²)."],
         "حلّل، ثم افحص القوس الأول."),
        ("س^2 - 1/4", "(س - 1/2)(س + 1/2)",
         ["1/4 = (1/2)².",
          "الناتج: (س − 1/2)(س + 1/2)."],
         "جذر 1/4 هو 1/2."),
        ("2س^4 - 32", "2(س - 2)(س + 2)(س² + 4)",
         ["العامل المشترك 2: 2(س⁴ − 16).",
          "س⁴ − 16 = (س² − 4)(س² + 4).",
          "س² − 4 = (س − 2)(س + 2).",
          "الناتج: 2(س − 2)(س + 2)(س² + 4)."],
         "عامل مشترك أولاً، ثم تحليل مزدوج."),
        ("(2س)^2 - (3ص)^2", "(2س - 3ص)(2س + 3ص)",
         ["الحدّان مكتوبان أصلاً كمربعين.",
          "الناتج: (2س − 3ص)(2س + 3ص)."],
         "طبّق القاعدة مباشرة."),
        ("س^12 - ص^12", "(س^6 - ص^6)(س^6 + ص^6)",
         ["س¹² = (س⁶)²  و  ص¹² = (ص⁶)².",
          "الناتج: (س⁶ − ص⁶)(س⁶ + ص⁶)."],
         "نصّف الأسس."),
        ("144 - 25س^2", "(12 - 5س)(12 + 5س)",
         ["144 = 12²  و  25س² = (5س)².",
          "الناتج: (12 − 5س)(12 + 5س)."],
         "ابدأ بالعدد لأنه المطروح منه."),
        ("س^2/36 - ص^2/49", "(س/6 - ص/7)(س/6 + ص/7)",
         ["س²/36 = (س/6)²  و  ص²/49 = (ص/7)².",
          "الناتج: (س/6 − ص/7)(س/6 + ص/7)."],
         "خذ جذر البسط والمقام لكل كسر."),
        ("3س^2 - 75", "3(س - 5)(س + 5)",
         ["العامل المشترك 3: 3(س² − 25).",
          "س² − 25 = (س − 5)(س + 5).",
          "الناتج: 3(س − 5)(س + 5)."],
         "أخرج 3 أولاً."),
        ("س^2 - 0.01", "(س - 0.1)(س + 0.1)",
         ["0.01 = (0.1)².",
          "الناتج: (س − 0.1)(س + 0.1)."],
         "جذر 0.01 هو 0.1."),
        ("(س+ص)^2 - (س-ص)^2", "4سص",
         ["أ = (س+ص) ، ب = (س−ص).",
          "الفرق: [(س+ص) − (س−ص)][(س+ص) + (س−ص)].",
          "= (2ص)(2س).",
          "الناتج: 4سص."],
         "بسّط كل قوس بعد الطرح والجمع."),
    ]
    for expr, ans, steps, hint in high:
        bank.append(Question(expr, ans, "أسس أعلى وكسور", 3, steps, hint))

    # توليد خيارات لكل سؤال
    for q in bank:
        wrongs = set()
        if "(" in q.answer and ")" in q.answer:
            wrongs.add(q.answer.replace(" - ", " + ", 1))
            wrongs.add(q.answer.replace(" + ", " - ", 1))
        pool = [o.answer for o in bank if o.answer != q.answer]
        rnd.shuffle(pool)
        for cand in pool:
            if len(wrongs) >= 3:
                break
            if cand != q.answer:
                wrongs.add(cand)
        opts = [q.answer] + list(wrongs)[:3]
        rnd.shuffle(opts)
        q.options = opts

    return bank[:120]


bank = build_bank()

# ==========================================================
# 3) تهيئة حالة الجلسة (Session State)
# ==========================================================
if "total_points" not in st.session_state:
    st.session_state.total_points = 0
if "solved" not in st.session_state:
    st.session_state.solved = 0
if "correct_total" not in st.session_state:
    st.session_state.correct_total = 0
if "practice_q" not in st.session_state:
    st.session_state.practice_q = random.choice(bank)
if "practice_tries" not in st.session_state:
    st.session_state.practice_tries = 0

# ==========================================================
# 4) القائمة الجانبية والرأس
# ==========================================================
st.sidebar.title("📌 إعداد الطالبات")
st.sidebar.info("""
- **أية**
- **رفيف**
- **سارة**
- **هزار**
""")

st.sidebar.markdown("---")
st.sidebar.subheader("📊 إحصائيات الإنجاز")
st.sidebar.metric("إجمالي النقاط", st.session_state.total_points)
st.sidebar.metric("الأسئلة المحلولة", st.session_state.solved)
acc = round(st.session_state.correct_total / st.session_state.solved * 100) if st.session_state.solved > 0 else 100
st.sidebar.metric("نسبة الدقة", f"{acc}%")

if st.sidebar.button("🔄 إعادة ضبط النتيجة"):
    st.session_state.total_points = 0
    st.session_state.solved = 0
    st.session_state.correct_total = 0
    st.rerun()

st.markdown("""
<div class="main-header">
    <h1>📐 تطبيق الفرق بين مربعين التفاعلي</h1>
    <p>بطاقات الشرح، بنك الأسئلة الشامل، الاختبارات، التدريب الموجه والمحاكاة الهندسية</p>
</div>
""", unsafe_allow_html=True)

# ==========================================================
# 5) تبويبات التطبيق
# ==========================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📖 بطاقات الشرح",
    "📚 بنك الأسئلة (120)",
    "📝 الاختبار الشامل",
    "🎯 التدريب الموجّه",
    "🎨 المحاكاة الهندسية"
])

# ----------------------------------------------------------
# تبويب 1: بطاقات الشرح
# ----------------------------------------------------------
with tab1:
    st.subheader("💡 بطاقات التأسيس والتحليل")
    st.write("اختر التصنيف لعرض البطاقات، واضغط على السؤال لرؤية خطوات الحل التفصيلية.")

    category_filter = st.radio(
        "تصنيف البطاقات:",
        ["الكل", "عامل مشترك (G.C.F)", "تحليل مباشر", "حساب ذهني للأعداد", "أسس أعلى وكسور"],
        horizontal=True
    )

    filtered_cards = [q for q in bank if category_filter == "الكل" or q.category == category_filter][:12]

    cols = st.columns(3)
    for idx, q in enumerate(filtered_cards):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="card-box">
                <small style="color:#fbbf24;">{q.category}</small>
                <h3 style="color:#38bdf8; text-align:center;">{q.expr}</h3>
            </div>
            """, unsafe_allow_html=True)
            with st.expander("عرض خطوات الحل ↺"):
                for s_idx, step in enumerate(q.steps, 1):
                    st.write(f"**{s_idx}.** {step}")

# ----------------------------------------------------------
# تبويب 2: بنك الأسئلة (120)
# ----------------------------------------------------------
with tab2:
    st.subheader("📚 بنك أسئلة المنهاج الكامل (120 سؤالاً)")

    b_cat = st.selectbox(
        "فلترة حسب التصنيف:",
        ["الكل", "عامل مشترك (G.C.F)", "تحليل مباشر", "حساب ذهني للأعداد", "أسس أعلى وكسور"]
    )

    filtered_bank = [q for q in bank if b_cat == "الكل" or q.category == b_cat]

    df_data = []
    for i, q in enumerate(filtered_bank, 1):
        df_data.append({
            "#": i,
            "المقدار": q.expr,
            "التصنيف": q.category,
            "المستوى": f"المستوى {q.level}",
            "الحل النهائي": q.answer
        })

    st.dataframe(pd.DataFrame(df_data), use_container_width=True)

    st.markdown("---")
    st.write("🔍 **عرض التفاصيل لسؤال معين:**")
    selected_idx = st.number_input("أدخل رقم السؤال لعرض التلميح وخطوات الحل:", min_value=1,
                                   max_value=len(filtered_bank), step=1)
    if selected_idx:
        q = filtered_bank[selected_idx - 1]
        st.info(f"**المقدار:** {q.expr}\n\n💡 **التلميح:** {q.hint}")
        st.success("**خطوات الحل:**\n" + "\n".join([f"{n + 1}. {s}" for n, s in enumerate(q.steps)]))

# ----------------------------------------------------------
# تبويب 3: الاختبار الشامل
# ----------------------------------------------------------
with tab3:
    st.subheader("📝 اختبار الانطلاقة والتمكن الشامل")

    if "exam_state" not in st.session_state:
        st.session_state.exam_state = "home"

    if st.session_state.exam_state == "home":
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### ⚡ تحدي سريع")
            st.write("10 أسئلة لمراجعة سريعة")
            if st.button("ابدأ 10 أسئلة"):
                st.session_state.exam_qs = random.sample(bank, min(10, len(bank)))
                st.session_state.exam_answers = {}
                st.session_state.exam_t0 = time.time()
                st.session_state.exam_state = "running"
                st.rerun()

        with col2:
            st.markdown("### 🎯 مستوى قياسي")
            st.write("30 سؤالاً لتغطية الشامل للمهارات")
            if st.button("ابدأ 30 سؤالاً"):
                st.session_state.exam_qs = random.sample(bank, min(30, len(bank)))
                st.session_state.exam_answers = {}
                st.session_state.exam_t0 = time.time()
                st.session_state.exam_state = "running"
                st.rerun()

        with col3:
            st.markdown("### 🏆 التحدي الشامل")
            st.write("120 سؤالاً بالكامل")
            if st.button("ابدأ التحدي الكامل"):
                st.session_state.exam_qs = bank.copy()
                st.session_state.exam_answers = {}
                st.session_state.exam_t0 = time.time()
                st.session_state.exam_state = "running"
                st.rerun()

    elif st.session_state.exam_state == "running":
        qs = st.session_state.exam_qs
        st.warning(f"⏰ الاختبار جارٍ | عدد الأسئلة: {len(qs)}")

        with st.form("exam_form"):
            for idx, q in enumerate(qs, 1):
                st.markdown(f"**سؤال {idx} من {len(qs)}:** حلّل تحليلاً تاماً: `{q.expr}`")
                user_ans = st.radio(
                    f"اختر الإجابة للسؤال {idx}:",
                    q.options,
                    key=f"ex_q_{idx}",
                    index=None
                )
                st.session_state.exam_answers[idx - 1] = user_ans
                st.markdown("---")

            submitted = st.form_submit_button("تسليم الاختبار 🏁")
            if submitted:
                st.session_state.exam_time = int(time.time() - st.session_state.exam_t0)
                st.session_state.exam_state = "finished"
                st.rerun()

    elif st.session_state.exam_state == "finished":
        qs = st.session_state.exam_qs
        ans = st.session_state.exam_answers
        right = sum(1 for i, q in enumerate(qs) if ans.get(i) == q.answer)
        wrong = len(qs) - right
        pct = round(right / len(qs) * 100)
        pts = sum(q.level * 10 for i, q in enumerate(qs) if ans.get(i) == q.answer)

        # تحديث النقاط العابرة
        st.session_state.total_points += pts
        st.session_state.solved += len(qs)
        st.session_state.correct_total += right

        st.balloons()
        st.header("🎉 نتيجة الاختبار")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("النتيجة", f"{pct}%")
        c2.metric("إجابات صحيحة", right)
        c3.metric("إجابات خاطئة", wrong)
        c4.metric("النقاط المكتسبة", pts)

        if pct >= 90:
            st.success("ممتاز! إتقان تام 🎉")
        elif pct >= 70:
            st.info("جيد جداً، واصلي 💪")
        else:
            st.error("تحتاجين لمراجعة البطاقات 📘")

        if st.button("العودة لشاشة الاختبارات"):
            st.session_state.exam_state = "home"
            st.rerun()

# ----------------------------------------------------------
# تبويب 4: التدريب الموجه
# ----------------------------------------------------------
with tab4:
    st.subheader("🎯 التدريب الموجّه والمباشر")
    st.write("حلّ المسألة، وإذا احتجت مساعدة اضغط على زر التلميح.")

    q = st.session_state.practice_q

    st.markdown(f"""
    <div style="background-color:#1e293b; padding:20px; border-radius:10px; text-align:center;">
        <span style="color:#fbbf24;">{q.category} | المستوى {q.level}</span>
        <h2 style="color:#38bdf8;">{q.expr}</h2>
    </div>
    """, unsafe_allow_html=True)


    def norm(s):
        return s.replace(" ", "").replace("×", "*").replace("−", "-").replace("*", "").lower()


    user_input = st.text_input("اكتب التحليل التام هنا:", key="practice_input")

    col_b1, col_b2, col_b3, col_b4 = st.columns(4)

    with col_b1:
        if st.button("تحقق من الإجابة ✔"):
            st.session_state.practice_tries += 1
            if norm(user_input) == norm(q.answer) or norm(user_input) in norm(q.answer):
                pts = max(q.level * 10 - (st.session_state.practice_tries - 1) * 3, 3)
                st.success(f"إجابة صحيحة ممتاز! (+{pts} نقطة)")
                st.session_state.total_points += pts
                st.session_state.solved += 1
                st.session_state.correct_total += 1
            else:
                st.error(f"غير صحيح، حاولي مرة أخرى. (المحاولة {st.session_state.practice_tries})")
                if st.session_state.practice_tries >= 3:
                    st.warning(f"الحل الصحيح هو: {q.answer}")

    with col_b2:
        if st.button("عرض تلميح 💡"):
            st.info(f"💡 تلميح: {q.hint}")

    with col_b3:
        if st.button("خطوات الحل 📖"):
            st.write("**خطوات الحل التفصيلية:**")
            for n, step in enumerate(q.steps, 1):
                st.write(f"{n}. {step}")

    with col_b4:
        if st.button("سؤال جديد 🔄"):
            st.session_state.practice_q = random.choice(bank)
            st.session_state.practice_tries = 0
            st.rerun()

# ----------------------------------------------------------
# تبويب 5: المحاكاة الهندسية
# ----------------------------------------------------------
with tab5:
    st.subheader("🎨 المحاكاة الهندسية للفرق بين مربعين")
    st.write("شاهد هندسياً كيف يتحول اقتطاع المربع $b^2$ من $a^2$ إلى مستطيل أبعاده $(a-b)(a+b)$.")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        a_val = st.slider("طول ضلع المربع الكبير (a):", min_value=3, max_value=15, value=8)
    with col_s2:
        b_val = st.slider("طول ضلع المربع المقتطع (b):", min_value=1, max_value=a_val - 1, value=min(3, a_val - 1))

    # رسم الأشكال الهندسية باستخدام Matplotlib
    fig, ax = plt.subplots(figsize=(6, 6))

    # المربع الكلي a^2
    rect_a = patches.Rectangle((0, 0), a_val, a_val, linewidth=2, edgecolor='#38bdf8', facecolor='#1e293b',
                               label=f'المربع الكلي أ² ({a_val}×{a_val}={a_val * a_val})')
    ax.add_patch(rect_a)

    # المربع المقتطع b^2
    rect_b = patches.Rectangle((a_val - b_val, a_val - b_val), b_val, b_val, linewidth=2, edgecolor='#ef4444',
                               facecolor='#7f1d1d', label=f'المربع المقتطع ب² ({b_val}×{b_val}={b_val * b_val})')
    ax.add_patch(rect_b)

    # المنطقة المتبقية 1
    rect_r1 = patches.Rectangle((0, 0), a_val - b_val, a_val, linewidth=1.5, edgecolor='#22c55e', facecolor='#15803d',
                                alpha=0.5)
    ax.add_patch(rect_r1)

    # المنطقة المتبقية 2
    rect_r2 = patches.Rectangle((a_val - b_val, 0), b_val, a_val - b_val, linewidth=1.5, edgecolor='#fbbf24',
                                facecolor='#b45309', alpha=0.5)
    ax.add_patch(rect_r2)

    ax.set_xlim(-1, a_val + 2)
    ax.set_ylim(-1, a_val + 2)
    ax.set_aspect('equal')
    ax.axis('off')

    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')

    st.pyplot(fig)

    st.markdown(f"""
    <div style="background-color:#1e293b; padding:15px; border-radius:10px; text-align:center;">
        <h3>المساحة المتبقية = $a^2 - b^2$ = {a_val ** 2} - {b_val ** 2} = <span style="color:#38bdf8;">{a_val ** 2 - b_val ** 2}</span></h3>
        <h3>أبعاد المستطيل الناتج = $(a-b)(a+b)$ = ({a_val - b_val}) × ({a_val + b_val}) = <span style="color:#22c55e;">{(a_val - b_val) * (a_val + b_val)}</span></h3>
    </div>
    """, unsafe_allow_html=True)