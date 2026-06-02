# ⚖️ HK Court Travel Document Generator
## 香港區域法院子女旅行申請文件自動生成

**Live App:** https://hk-court-template-production.up.railway.app

Generate Hong Kong District Court child travel application documents in seconds.

### What it generates

| Case Type | Documents |
|---|---|
| **Option A** — Mother agrees | 誓詞 + 承諾書 + 同意書 + 附錄一 |
| **Option B** — Mother does NOT agree | 誓詞 + 承諾書 + 附錄一 + 申請通知書 + 服達誓詞 |
| **School Trip** (English) | Affirmation + Consent + Undertaking |

### How to use
1. Open the live app link above
2. Fill in the travel details (destination, dates, children)
3. Preview all documents and run AI proofread check
4. Download as individual `.docx` files or ZIP

### Use for your own case
Click **⚙️ Case Settings** at the top to update the case number, party names, and children's names for your own matrimonial case.

### Local development
```bash
pip install -r requirements.txt
streamlit run app.py
```

---
婚姻訴訟 2022 年 9664 號 — FCMC 9664/2022
