from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

load_dotenv()

client = OpenAI()

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_rag",
    embedding=embedding_model
)


def process_query(query: str):
    print("Searching chunks", query)
    search_results = vector_db.similarity_search(query=query, k=6)

    def format_context(docs):
        lines = []

        for i, d in enumerate(docs, start=1):
            page = (
                d.metadata.get("page")
                or d.metadata.get("page_number")
                or "unknown"
            )

            source = d.metadata.get("source", "")

            header = f"[Snippet {i} | p. {page}"
            if source:
                header += f" | {source}"
            header += "]"

            lines.append(f"{header}\n{d.page_content}")

        return "\n\n".join(lines)


    retrieved_context = format_context(search_results)

    prompt = f"""
    User question:
    {query}

    Retrieved Context:
    {retrieved_context}
    """

    SYSTEM_PROMPT = f"""
    ## Role
    You are “PDF-RAG Assistant”, a retrieval-grounded assistant.

    ## Grounding rules (critical) 
    - Answer using ONLY the provided Retrieved Context.
    - If the answer is not clearly contained in the Retrieved Context, say:
      “I don’t have enough information in the provided document to answer that.”
    - Do not invent facts, APIs, code, or page numbers.

    ## Use of context
    - The Retrieved Context will be provided as a list of snippets, each with:
      - page_content
      - page_number (or metadata.page)
    - Prefer the most relevant snippets; ignore irrelevant ones.

    ## Citations
    - After each factual claim, cite the supporting page number(s) like: (p. 12) or (p. 12–13).
    - If multiple snippets support a claim, cite multiple pages: (p. 4, p. 7).
    - If you cannot cite it, don’t claim it.

    ## Output style
    - Be concise and direct.
    - If the user asks for code, provide code only if the context supports it; otherwise say you can’t find it in the document.
    - When helpful, include a short “Where this comes from” section listing the pages referenced.

    ## If the user asks outside the PDF
    - Refuse briefly and remind them you can only answer from the indexed PDF content.
    """

    response = client.responses.create(
        model="gpt-5",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )

    return response.output_text

# if __name__ == "__main__":
#     while True:
#         user_query = input("Ask me something: ")
#         print(process_query(user_query))