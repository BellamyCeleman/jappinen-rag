import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

import pdfplumber

def page_to_text(page):
   tables_bbox = [table.bbox for table in page.find_tables()]
   page_without_tables = page

   for bbox in tables_bbox:
      page_without_tables = page_without_tables.filter(
         lambda char, bbox=bbox: not (
            char["x0"] >= bbox[0] and char["x1"] <= bbox[2] and
            char["top"] >= bbox[1] and char["bottom"] <= bbox[3]
         )
      )

   plain_text = page_without_tables.extract_text()
   
   table_text = []
   for table in page.extract_tables():
      rows = ['|'.join(char or "" for char in row) for row in table]
      table_text.append("\n".join(rows))

   return plain_text + "\n\n" + "\n\n".join(table_text)

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