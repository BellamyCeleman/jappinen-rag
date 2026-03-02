import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

import pdfplumber

def format_as_markdown_table(table):
   if not table or not any(row for row in table):
      return ""
   
   clean_table = [[(cell or "").strip() for cell in row] for row in table]
   
   markdown_rows = []
   for i, row in enumerate(clean_table):
      markdown_rows.append("| " + " | ".join(row) + " |")
      if i == 0:
         markdown_rows.append("| " + " | ".join(["---"] * len(row)) + " |")
         
   return "\n".join(markdown_rows)

def page_to_text(page):
   tables = page.find_tables()
   tables_bbox = [table.bbox for table in tables]
   
   page_without_tables = page
   for bbox in tables_bbox:
      page_without_tables = page_without_tables.filter(
         lambda char, b=bbox: not (
               char["x0"] >= b[0] and char["x1"] <= b[2] and
               char["top"] >= b[1] and char["bottom"] <= b[3]
         )
      )

   plain_text = page_without_tables.extract_text() or ""
   
   markdown_tables = []
   for table_data in page.extract_tables():
      md_table = format_as_markdown_table(table_data)
      if md_table:
         markdown_tables.append(md_table)

   content = [f"## PAGE SECTION ##\n{plain_text}"]
   if markdown_tables:
      content.append("### DATA TABLES ###")
      content.extend(markdown_tables)
      
   return "\n\n".join(content)

def save_txt(list_paths):
   for path in list_paths:
      path = Path(path)

      if path.with_suffix(".txt").exists():
         continue

      with pdfplumber.open(path) as pdf:
         full_text = "\n\n".join(page_to_text(page) for page in pdf.pages)

      with open(path.with_suffix(".txt"), "w", encoding="utf-8") as file:
         file.write(full_text)



if __name__ == "__main__":
   list_paths = [
      "manuals/LAD-Front-Loading-Service-Manual-L11.pdf",
      "manuals/technical-manual-w11663204-revb.pdf"
   ]

   save_txt(list_paths)