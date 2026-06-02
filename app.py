import streamlit as st
import datetime
import io
import zipfile
from generator import (
    CASE,
    generate_zh_affirmation_a, generate_zh_undertaking,
    generate_zh_consent, generate_zh_annex,
    generate_zh_affirmation_b, generate_zh_notice_b,
    generate_zh_service_affirmation,
    generate_en_affirmation, generate_en_consent, generate_en_undertaking,
    children_zh,
)
from ai_review import review_documents

st.set_page_config(
    page_title="HK Court Travel Document Generator",
    page_icon="⚖️",
    layout="wide",
)

if "step" not in st.session_state:
    st.session_state["step"] = 1
if "form_data" not in st.session_state:
    st.session_state["form_data"] = {}
if "docs" not in st.session_state:
    st.session_state["docs"] = {}


def go_to(step):
    st.session_state["step"] = step


def ordinal(n):
    if 11 <= n <= 13:
        return f"{n}th"
    return f"{n}{['th','st','nd','rd','th'][min(n % 10, 4)]}"


# ── STEP 1 ────────────────────────────────────────────────────────────────────
def step1():
    st.title("⚖️ HK Court Travel Document Generator")
    st.caption("區域法院 婚姻訴訟  2022  年  9664  號 — 方銘 v 李慧儀")

    with st.expander("⚙️ Case Settings — edit here for your own case", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            case_year = st.text_input("Case Year 案件年份", CASE["year"])
            case_number = st.text_input("Case Number 案件編號", CASE["number"])
            petitioner_zh = st.text_input("Petitioner 呈請人（中文）", CASE["petitioner_zh"])
            petitioner_en = st.text_input("Petitioner 呈請人（英文）", CASE["petitioner_en"])
            respondent_zh = st.text_input("Respondent 答辯人（中文）", CASE["respondent_zh"])
            respondent_en = st.text_input("Respondent 答辯人（英文）", CASE["respondent_en"])
            respondent_hkid = st.text_input("Respondent HKID 答辯人身份證", CASE["respondent_hkid"])
        with c2:
            child1_zh = st.text_input("Child 1（中文）", CASE["child1_zh"])
            child1_en = st.text_input("Child 1（English）", CASE["child1_en"])
            child2_zh = st.text_input("Child 2（中文）", CASE["child2_zh"])
            child2_en = st.text_input("Child 2（English）", CASE["child2_en"])
            custody_date_zh = st.text_input("Custody Order Date（中文）", CASE["custody_order_date_zh"])
            custody_date_en = st.text_input("Custody Order Date（English）", CASE["custody_order_date_en"])
            pet_addr_zh = st.text_input("Petitioner Address（中文）", CASE["petitioner_address_zh"])
            pet_addr_en = st.text_input("Petitioner Address（English）", CASE["petitioner_address_en"])

    st.divider()

    case_type = st.radio(
        "📋 Case Type 文件類型",
        [
            "Option A — 母親同意 (Mother Agrees)",
            "Option B — 母親不同意 (Mother Does NOT Agree)",
            "School Trip — 學校旅行 (English)",
        ],
        horizontal=True,
    )

    st.divider()
    st.subheader("👧👦 Children 子女")

    if "School Trip" in case_type:
        child_pick = st.radio(
            "Which child? 哪位子女？",
            [f"{child1_en} ({child1_zh})", f"{child2_en} ({child2_zh})"],
        )
        both_children = False
        child_key = "child1" if child1_en in child_pick else "child2"
    else:
        both_children = st.checkbox("Both children 兩位子女", value=True)
        child_key = "both"
        if not both_children:
            child_pick2 = st.radio(
                "Which child? 哪位子女？",
                [f"{child1_zh} ({child1_en})", f"{child2_zh} ({child2_en})"],
            )
            child_key = "child1" if child1_zh in child_pick2 else "child2"

    st.divider()
    st.subheader("✈️ Travel Details 旅行資料")

    if "School Trip" in case_type:
        school_name = st.text_input("School Name 學校名稱", "Harrow International School Hong Kong")
        destination_en = st.text_input("Destination 目的地 (English)", "Xi'an, China")
        c1, c2 = st.columns(2)
        with c1:
            trip_start = st.date_input("Departure Date 出發日期", datetime.date.today())
        with c2:
            trip_end = st.date_input("Return Date 回港日期", datetime.date.today() + datetime.timedelta(days=4))
        affirm_date = st.date_input("Signing Date 簽署日期", datetime.date.today())
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        trip_start_en = f"{day_names[trip_start.weekday()]}, {trip_start.day} {trip_start.strftime('%B %Y')}"
        trip_end_en = f"{day_names[trip_end.weekday()]}, {trip_end.day} {trip_end.strftime('%B %Y')}"
        affirm_date_en = f"{ordinal(affirm_date.day)} day of {affirm_date.strftime('%B %Y')}"
    else:
        destination_zh = st.text_input("Destination 目的地（中文，例如：日本）", "日本")
        c1, c2 = st.columns(2)
        with c1:
            travel_start = st.date_input("Departure Date 出發日期", datetime.date.today())
        with c2:
            travel_end = st.date_input("Return Date 回港日期", datetime.date.today() + datetime.timedelta(days=5))
        sign_date = st.date_input("Signing Date 簽署日期", datetime.date.today())

        def zh_date(d):
            return f"{d.year}年{d.month}月{d.day}日"

        start_date_zh = zh_date(travel_start)
        end_date_zh = zh_date(travel_end)
        sign_date_zh = zh_date(sign_date)

    if "Option B" in case_type:
        st.divider()
        st.subheader("🏛️ Court Hearing Details 聆訊資料 (Option B)")
        c1, c2, c3 = st.columns(3)
        with c1:
            hearing_date = st.date_input("Hearing Date 聆訊日期", datetime.date.today() + datetime.timedelta(days=14))
        with c2:
            hearing_time = st.selectbox("Time 時間", [
                "上午9時", "上午9時30分", "上午10時", "上午10時30分",
                "上午11時", "下午2時", "下午2時30分", "下午3時",
            ])
        with c3:
            hearing_floor = st.text_input("Floor 樓層", "6")
        c4, c5 = st.columns(2)
        with c4:
            hearing_room = st.text_input("Room 庭", "6")
        with c5:
            hearing_judge = st.text_input("Judge 法官 (leave blank if unknown)", "")

        st.subheader("📮 Mailing Details 郵寄資料 (Option B)")
        c1, c2 = st.columns(2)
        with c1:
            mail_date = st.date_input("Mailing Date 郵寄日期", datetime.date.today())
            post_office_zh = st.text_input("Post Office 郵政局", "旺角郵政局")
        with c2:
            respondent_addr_short = st.text_input("Respondent Address 答辯人地址（簡短）", "香港九龍某某道123號")
            email_date = st.date_input("Mother's Response Date 母親回覆日期", datetime.date.today() - datetime.timedelta(days=2))
            email_desc = st.text_input("Response Description 回覆描述", "回覆電郵表示原則上不反對")

    st.divider()

    if st.button("➡️ Preview Documents 預覽文件", type="primary", use_container_width=True):
        custom_case = dict(CASE)
        custom_case.update({
            "year": case_year, "number": case_number,
            "petitioner_zh": petitioner_zh, "petitioner_en": petitioner_en,
            "respondent_zh": respondent_zh, "respondent_en": respondent_en,
            "child1_zh": child1_zh, "child1_en": child1_en,
            "child2_zh": child2_zh, "child2_en": child2_en,
            "respondent_hkid": respondent_hkid,
            "custody_order_date_zh": custody_date_zh,
            "custody_order_date_en": custody_date_en,
            "petitioner_address_zh": pet_addr_zh,
            "petitioner_address_en": pet_addr_en,
        })

        fd = {
            "case": custom_case,
            "case_type": case_type,
            "both_children": both_children,
            "child": child_key,
        }

        if "School Trip" in case_type:
            child_en_str = (
                f"{custom_case['child1_en']} ({custom_case['child1_zh']})"
                if child_key == "child1"
                else f"{custom_case['child2_en']} ({custom_case['child2_zh']})"
            )
            fd.update({
                "child_en": child_en_str,
                "school_name": school_name,
                "destination_en": destination_en,
                "trip_start_en": trip_start_en,
                "trip_end_en": trip_end_en,
                "affirm_date_en": affirm_date_en,
            })
        else:
            fd.update({
                "destination_zh": destination_zh,
                "start_date_zh": start_date_zh,
                "end_date_zh": end_date_zh,
                "sign_date_zh": sign_date_zh,
                "sign_year": str(sign_date.year),
                "sign_month": str(sign_date.month),
                "sign_day": str(sign_date.day),
                "undertaking_date_zh": sign_date_zh,
                "consent_date_zh": f"{sign_date.year}年__月__日",
            })
            if "Option B" in case_type:
                fd.update({
                    "respondent_email_date_zh": zh_date(email_date),
                    "respondent_response_desc": email_desc,
                    "hearing_date_zh": zh_date(hearing_date),
                    "hearing_time": hearing_time,
                    "hearing_floor": hearing_floor,
                    "hearing_room": hearing_room,
                    "hearing_judge": hearing_judge,
                    "mail_date_zh": zh_date(mail_date),
                    "post_office_zh": post_office_zh,
                    "respondent_address_short_zh": respondent_addr_short,
                })

        st.session_state["form_data"] = fd
        go_to(2)
        st.rerun()


# ── STEP 2 ────────────────────────────────────────────────────────────────────
def step2():
    st.title("📋 Preview & Proofread 預覽及校對")
    st.caption("Review all filled content below before downloading. Use AI Check to flag issues.")

    fd = st.session_state["form_data"]
    case_type = fd["case_type"]
    case = fd["case"]

    docs = {}
    previews = {}

    kids = children_zh(fd)

    if "Option A" in case_type:
        docs["誓詞（Option A）.docx"] = generate_zh_affirmation_a(fd)
        docs["承諾書.docx"] = generate_zh_undertaking(fd)
        docs["同意書.docx"] = generate_zh_consent(fd)
        docs["附錄一.docx"] = generate_zh_annex(fd)

        previews["誓詞 (Option A)"] = (
            f"呈請人：{case['petitioner_zh']}，現居於 {case['petitioner_address_zh']}\n"
            f"子女：{kids}\n"
            f"目的地：{fd['destination_zh']}旅遊\n"
            f"出發：{fd['start_date_zh']}  回港：{fd['end_date_zh']}\n"
            f"簽署日期：{fd['sign_date_zh']}\n"
            f"管養令日期：{case['custody_order_date_zh']}\n"
            f"承諾書日期：{fd['undertaking_date_zh']}\n"
            f"同意書日期：{fd['consent_date_zh']}"
        )
        previews["承諾書"] = (
            f"呈請人：{case['petitioner_zh']}\n"
            f"子女：{kids}\n"
            f"目的地：{fd['destination_zh']}旅遊\n"
            f"出發：{fd['start_date_zh']}  回港：{fd['end_date_zh']}\n"
            f"簽署：{fd['sign_date_zh']}"
        )
        previews["同意書（答辯人簽署）"] = (
            f"答辯人：{case['respondent_zh']}\n"
            f"子女：{kids}\n"
            f"目的地：{fd['destination_zh']}旅遊\n"
            f"出發：{fd['start_date_zh']}  回港：{fd['end_date_zh']}"
        )
        previews["附錄一"] = (
            f"案件：{case['year']}年 第{case['number']}號\n"
            f"呈請人：{case['petitioner_zh']}\n"
            f"答辯人：{case['respondent_zh']}"
        )

    elif "Option B" in case_type:
        docs["誓詞（Option B）.docx"] = generate_zh_affirmation_b(fd)
        docs["承諾書.docx"] = generate_zh_undertaking(fd)
        docs["附錄一.docx"] = generate_zh_annex(fd)
        docs["申請帶子女離境許可通知書.docx"] = generate_zh_notice_b(fd)
        docs["服達誓詞.docx"] = generate_zh_service_affirmation(fd)

        previews["誓詞 (Option B)"] = (
            f"呈請人：{case['petitioner_zh']}\n"
            f"子女：{kids}\n"
            f"目的地：{fd['destination_zh']}旅遊\n"
            f"出發：{fd['start_date_zh']}  回港：{fd['end_date_zh']}\n"
            f"答辯人回覆：{fd['respondent_email_date_zh']} {fd['respondent_response_desc']}"
        )
        previews["通知書"] = (
            f"聆訊：{fd['hearing_date_zh']} {fd['hearing_time']}\n"
            f"地點：灣仔法院 {fd['hearing_floor']}樓 第{fd['hearing_room']}庭\n"
            f"子女：{kids}\n"
            f"目的地：{fd['destination_zh']}旅遊\n"
            f"答辯人 HKID：{case['respondent_hkid']}"
        )
        previews["服達誓詞"] = (
            f"郵寄日期：{fd['mail_date_zh']}\n"
            f"郵政局：{fd['post_office_zh']}\n"
            f"寄往：{fd['respondent_address_short_zh']}"
        )

    else:  # School Trip
        docs["Affirmation.docx"] = generate_en_affirmation(fd)
        docs["Consent.docx"] = generate_en_consent(fd)
        docs["Undertaking.docx"] = generate_en_undertaking(fd)
        previews["Affirmation"] = (
            f"Petitioner: {case['petitioner_en']}\n"
            f"Child: {fd['child_en']}\n"
            f"School: {fd['school_name']}\n"
            f"Destination: {fd['destination_en']}\n"
            f"Trip: {fd['trip_start_en']} → {fd['trip_end_en']}\n"
            f"Signed: {fd['affirm_date_en']}"
        )
        previews["Consent (Respondent signs)"] = (
            f"Respondent: {case['respondent_en']}\n"
            f"Child: {fd['child_en']}\n"
            f"Destination: {fd['destination_en']}\n"
            f"Trip: {fd['trip_start_en']} → {fd['trip_end_en']}"
        )
        previews["Undertaking (Petitioner signs)"] = (
            f"Petitioner: {case['petitioner_en']}\n"
            f"Child: {fd['child_en']}\n"
            f"Destination: {fd['destination_en']}\n"
            f"Trip: {fd['trip_start_en']} → {fd['trip_end_en']}\n"
            f"Organised by: {fd['school_name']}"
        )

    st.session_state["docs"] = docs

    # Side-by-side previews
    doc_names = list(previews.keys())
    for i in range(0, len(doc_names), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(doc_names):
                name = doc_names[i + j]
                with col:
                    st.subheader(f"📄 {name}")
                    st.code(previews[name], language=None)

    st.divider()
    st.subheader("🤖 AI Review 人工智能審查")
    if st.button("▶ Run AI Check", use_container_width=True):
        with st.spinner("Checking with Claude..."):
            result = review_documents(previews)
        if "All good" in result or "✅" in result:
            st.success(result)
        else:
            st.warning(result)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Edit 返回修改", use_container_width=True):
            go_to(1)
            st.rerun()
    with col2:
        if st.button("✅ Confirm & Download 確認下載", type="primary", use_container_width=True):
            go_to(3)
            st.rerun()


# ── STEP 3 ────────────────────────────────────────────────────────────────────
def step3():
    st.title("✅ Download Documents 下載文件")
    st.success("Documents ready! Click to download each file, or get all as ZIP.")

    docs = st.session_state["docs"]
    fd = st.session_state["form_data"]

    for filename, content in docs.items():
        st.download_button(
            label=f"⬇️  {filename}",
            data=content,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )

    st.divider()

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w") as zf:
        for filename, content in docs.items():
            zf.writestr(filename, content)
    zip_buf.seek(0)

    case_type_short = (
        "OptionA" if "Option A" in fd["case_type"]
        else ("OptionB" if "Option B" in fd["case_type"] else "SchoolTrip")
    )
    st.download_button(
        label="📦  Download All as ZIP 下載全部",
        data=zip_buf.read(),
        file_name=f"TravelDocs_{case_type_short}.zip",
        mime="application/zip",
        type="primary",
        use_container_width=True,
    )

    st.divider()
    if st.button("🔄 Start New Application 開始新申請", use_container_width=True):
        st.session_state["step"] = 1
        st.session_state["form_data"] = {}
        st.session_state["docs"] = {}
        st.rerun()


# ── Router ────────────────────────────────────────────────────────────────────
st.sidebar.markdown("## Steps 步驟")
step = st.session_state["step"]
st.sidebar.progress(step / 3)
st.sidebar.markdown(
    f"{'✅' if step > 1 else '▶'} 1. Fill Details 填寫資料\n\n"
    f"{'✅' if step > 2 else ('▶' if step == 2 else '○')} 2. Preview & Proofread 預覽校對\n\n"
    f"{'✅' if step > 3 else ('▶' if step == 3 else '○')} 3. Download 下載"
)

if step == 1:
    step1()
elif step == 2:
    step2()
else:
    step3()
