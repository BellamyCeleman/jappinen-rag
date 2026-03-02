import chromadb
import openai
import os
from dotenv import load_dotenv
from pathlib import Path
from pdf_preprocessing import save_txt

load_dotenv("dev.env")

openai_key = os.getenv("OPENAI_API_KEY")

openai_client = openai.OpenAI(api_key=openai_key)
chroma_client = chromadb.PersistentClient(path="./chroma_db")

collection = chroma_client.get_or_create_collection("documents")

def get_overlapping_chunks(text, chunk_size=1000, overlap=200):
   chunks = []
   start = 0
   while start < len(text):
      end = start + chunk_size
      chunks.append(text[start:end])
      start += (chunk_size - overlap)
   return chunks

def add_chunks(text_list):
   if collection.count() != 0:
      return

   all_chunks, all_metadatas, all_ids = [], [], []
   global_idx = 0
   
   for path in text_list:
      text = path.read_text(encoding="utf-8")
      chunks = get_overlapping_chunks(text)
      
      for i, chunk_content in enumerate(chunks):
         if not chunk_content.strip():
               continue
         
         all_chunks.append(chunk_content)
         all_metadatas.append({
               "source": path.name.replace(".txt", ".pdf"), 
               "chunk_index": i + 1
         })
         all_ids.append(f"chunk_{global_idx}")
         global_idx += 1

   collection.add(documents=all_chunks, metadatas=all_metadatas, ids=all_ids)

def retrieve_context(question, n_results=3):
    results = collection.query(
        query_texts=[question],
        n_results=n_results
    )
    
    context_parts = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        source_info = f"[Source: {meta['source']}, Page: {meta.get('page', 'N/A')}]"
        context_parts.append(f"{source_info}\n{doc}")
        
    return "\n\n---\n\n".join(context_parts)

def ask_question(question):
   context = retrieve_context(question)

   system_message = """
   You are an expert technical assistant for field mechanics.
   You answer questions about product maintenance and technical issues based strictly on the provided documentation.

   Guidelines:
   - Answer clearly and concisely, prioritizing practical actionable information
   - If the answer involves steps, present them in order
   - If the documentation does not contain enough information to answer, say so explicitly — do not guess or make up information
   - If relevant, mention which part of the documentation your answer is based on
   - Use simple, professional language suitable for field mechanics"""

   user_message = f"""
   Documentation context:
   {context}

   Mechanic's question: {question}

   Answer based on the documentation above."""

   response = openai_client.chat.completions.create(
      model="gpt-4o-mini",
              messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
   )
   return response.choices[0].message.content
   
if __name__ == "__main__":
   list_paths = [
      "manuals/LAD-Front-Loading-Service-Manual-L11.pdf",
      "manuals/technical-manual-w11663204-revb.pdf"
   ]
   missing = [p for p in list_paths if not Path(p).exists()]
   if missing:
      print("Missing manual files:")
      for p in missing:
         print(f"  {p}")
      print("Place the PDF files in the manuals/ directory and try again.")
      exit(1)

   save_txt(list_paths)
   
   list_paths = [Path(path).with_suffix(".txt") for path in list_paths]

   add_chunks(list_paths)

   while True:
      question = input("\nAsk a question (or 'quit' to exit): ")
      if question.lower() == "quit":
         break
      answer = ask_question(question)
      print(f"\nAnswer: {answer}")




