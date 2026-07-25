"""H4: extract text from downloaded source PDFs (literature verification)."""
import sys, fitz

src = sys.argv[1]
out = sys.argv[2]
doc = fitz.open(src)
with open(out, "w", encoding="utf-8") as f:
    for i, page in enumerate(doc):
        f.write("\n===== PAGE %d =====\n" % (i + 1))
        f.write(page.get_text("text"))
print("pages:", doc.page_count, "->", out)
