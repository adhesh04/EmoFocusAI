# rag_service.py
# The full RAG pipeline: question → guardrail → retrieve → LLM → guardrail → answer

import logging
from typing import Optional
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough, RunnableParallel
from langchain.schema.output_parser import StrOutputParser
from langchain.schema import Document

from .vector_store import get_retriever
from .guardrails import check_input, check_output, apply_warning

logger = logging.getLogger(__name__)

# SYSTEM_PROMPT = """You are the EmoFocus AI Focus Advisor — a knowledgeable, evidence-based assistant
# specialized in focus, attention, cognitive performance, and productivity science.

# STRICT RULES:
# 1. Answer ONLY using the context provided below. Do not invent facts.
# 2. If the context doesn't cover the question, say: "I don't have specific research on that,
#    but here is what I know from related areas..." — then give a helpful, grounded answer.
# 3. Always cite sources using [Source: filename].
# 4. Never recommend prescription medications, illegal substances, or unproven supplements.
# 5. Be warm, practical, and specific — give the user something actionable.
# 6. Keep answers between 150-250 words unless more detail is genuinely needed.
# 7. If the user describes a harmful or dangerous practice, clearly advise against it
#    and explain why, citing the science.

# CONTEXT FROM KNOWLEDGE BASE:
# {context}

# User question: {question}

# Answer:"""
SYSTEM_PROMPT = """You are the EmoFocus AI Focus Advisor — a knowledgeable, 
evidence-based assistant specialized in focus, attention, cognitive performance, 
and productivity science.

You have two sources of knowledge:
1. RETRIEVED CONTEXT below — specific research chunks from our knowledge base
2. YOUR OWN KNOWLEDGE — your general training on neuroscience, psychology, 
   and productivity research

INSTRUCTIONS:
- If the retrieved context is relevant to the question, use it and cite it 
  with [Source: filename]
- If the retrieved context is NOT relevant or insufficient, answer from your 
  own knowledge — you are a knowledgeable focus science expert
- Always give practical, actionable advice
- Never recommend prescription drugs or illegal substances
- Keep answers between 150-300 words
- Be warm and conversational, not clinical

RETRIEVED CONTEXT (use if relevant):
{context}

User question: {question}

Answer:"""


def format_docs(docs: list) -> str:
    parts = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        parts.append(f"[Source: {source}]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def extract_sources(docs: list) -> list:
    return list(set(doc.metadata.get("source", "unknown") for doc in docs))


def ask(question: str, chat_history: Optional[list] = None) -> dict:
    """
    Main entry point. Full pipeline:
    1. Input guardrail check
    2. Retrieve relevant chunks from ChromaDB
    3. LLM generates answer
    4. Output guardrail check
    5. Append any warnings
    6. Return answer + sources + metadata
    """

    # ── Step 1: Input guardrail
    input_check = check_input(question)
    if not input_check.allowed:
        return {
            "answer": input_check.message,
            "sources": [],
            "blocked": True,
            "block_category": input_check.category,
            "retrieved_chunks": 0,
            "error": None
        }

    try:
        # ── Step 2: Retrieve relevant chunks
        retriever = get_retriever(k=5)
        retrieved_docs = retriever.get_relevant_documents(question)
        context_text = format_docs(retrieved_docs)
        sources = extract_sources(retrieved_docs)

        # ── Step 3: Add conversation context if multi-turn
        final_question = question
        if chat_history and len(chat_history) > 0:
            recent = chat_history[-4:]
            history_text = "\n".join(
                f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
                for m in recent
            )
            final_question = f"Previous exchange:\n{history_text}\n\nCurrent question: {question}"

        # ── Step 4: Build and run LLM chain
        llm = Ollama(model="llama3.2:1b", temperature=0.3, num_ctx=2048)
        # llm = Ollama(model="llama3", temperature=0.3, num_ctx=4096)
        prompt = PromptTemplate(
            template=SYSTEM_PROMPT,
            input_variables=["context", "question"]
        )
        chain = (
            RunnableParallel(
                context=lambda _: context_text,
                question=RunnablePassthrough()
            )
            | prompt
            | llm
            | StrOutputParser()
        )

        logger.info(f"Running RAG for: {question[:80]}...")
        answer = chain.invoke(final_question)

        # ── Step 5: Output guardrail
        output_check = check_output(answer)
        if not output_check.allowed:
            return {
                "answer": output_check.message,
                "sources": [],
                "blocked": True,
                "block_category": output_check.category,
                "retrieved_chunks": len(retrieved_docs),
                "error": None
            }

        # ── Step 6: Append any safety warnings
        final_answer = apply_warning(answer, input_check.warning)

        return {
            "answer": final_answer,
            "sources": sources,
            "blocked": False,
            "block_category": None,
            "retrieved_chunks": len(retrieved_docs),
            "error": None
        }

    except Exception as e:
        import traceback
        logger.error(f"RAG error: {e}")
        logger.error(traceback.format_exc())
        return {
            "answer": "I couldn't process your question right now. Please make sure Ollama is running with the llama3 model (`ollama run llama3`).",
            "sources": [],
            "blocked": False,
            "block_category": None,
            "retrieved_chunks": 0,
            "error": str(e)
        }
