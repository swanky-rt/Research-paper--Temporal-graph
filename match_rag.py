from __future__ import annotations

import json, os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
import openai
from flask import Flask, request, jsonify


# ────────────────────────────────────────────────────────────────────
# 0.  Secrets
# ────────────────────────────────────────────────────────────────────
# load_dotenv()
# if "OPENAI_API_KEY" not in os.environ:
#     os.environ["OPENAI_API_KEY"] = "key"
# openai.api_key = os.environ["OPENAI_API_KEY"]

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("OPENAI_API_KEY not found in environment. Set it in a .env file or shell.")

openai.api_key = api_key

# ────────────────────────────────────────────────────────────────────
# 1.  Load / persist the questionnaire (same as before)
# ────────────────────────────────────────────────────────────────────
QUESTIONS_PATH = Path("questions.json")
if not QUESTIONS_PATH.exists():     # first run – dump the hard-coded list
    QUESTIONS_PATH.write_text(json.dumps([
    {
      "q_id": "q1",
      "text": "My everyday communication style is…",
      "options": [
        { "opt_id": "q1a", "label": "Short & direct" },
        { "opt_id": "q1b", "label": "Warm & expressive" },
        { "opt_id": "q1c", "label": "Thoughtful & measured" },
        { "opt_id": "q1d", "label": "Humorous / meme-heavy" },
        { "opt_id": "q1e", "label": "Depends on the person" }
      ]
    },
    {
      "q_id": "q2",
      "text": "How do you recharge your social battery?",
      "options": [
        { "opt_id": "q2a", "label": "Big parties give me energy" },
        { "opt_id": "q2b", "label": "Small hangouts are perfect" },
        { "opt_id": "q2c", "label": "Solo time is essential" },
        { "opt_id": "q2d", "label": "Balanced mix of everything" },
        { "opt_id": "q2e", "label": "It changes week-to-week" }
      ]
    },
    {
      "q_id": "q3",
      "text": "Planning style for trips or projects:",
      "options": [
        { "opt_id": "q3a", "label": "Detailed checklist & timeline" },
        { "opt_id": "q3b", "label": "Loose outline, improvise later" },
        { "opt_id": "q3c", "label": "Spontaneous—decide on the day" },
        { "opt_id": "q3d", "label": "Last-minute crunch works best" },
        { "opt_id": "q3e", "label": "Collaborative planning with others" }
      ]
    },
    {
      "q_id": "q4",
      "text": "When conflict appears, I usually…",
      "options": [
        { "opt_id": "q4a", "label": "Address it calmly right away" },
        { "opt_id": "q4b", "label": "Take time, then talk it out" },
        { "opt_id": "q4c", "label": "Find a compromise quickly" },
        { "opt_id": "q4d", "label": "Prefer to let it blow over" },
        { "opt_id": "q4e", "label": "Avoid confrontation altogether" }
      ]
    },
    {
      "q_id": "q5",
      "text": "Which life priorities resonate most with you?",
      "options": [
        { "opt_id": "q5a", "label": "Career growth" },
        { "opt_id": "q5b", "label": "Creative expression" },
        { "opt_id": "q5c", "label": "Community & service" },
        { "opt_id": "q5d", "label": "Travel & new experiences" },
        { "opt_id": "q5e", "label": "Health & wellbeing" }
      ]
    },
    {
      "q_id": "q6",
      "text": "Your ideal weekend looks like…",
      "options": [
        { "opt_id": "q6a", "label": "Outdoor adventure" },
        { "opt_id": "q6b", "label": "Café-hopping & city strolls" },
        { "opt_id": "q6c", "label": "Game / movie marathon at home" },
        { "opt_id": "q6d", "label": "Learning a new skill or hobby" },
        { "opt_id": "q6e", "label": "Volunteering / community event" }
      ]
    },
    {
      "q_id": "q7",
      "text": "Fitness routine that actually sticks:",
      "options": [
        { "opt_id": "q7a", "label": "Daily gym / running plan" },
        { "opt_id": "q7b", "label": "Team or club sports" },
        { "opt_id": "q7c", "label": "Yoga / Pilates / meditation" },
        { "opt_id": "q7d", "label": "Dance or movement classes" },
        { "opt_id": "q7e", "label": "Not big on regular workouts" }
      ]
    },
    {
      "q_id": "q8",
      "text": "Topics you never tire of discussing:",
      "options": [
        { "opt_id": "q8a", "label": "Science & technology" },
        { "opt_id": "q8b", "label": "Arts & culture" },
        { "opt_id": "q8c", "label": "Global issues & politics" },
        { "opt_id": "q8d", "label": "Personal growth & psychology" },
        { "opt_id": "q8e", "label": "Sports & fitness" }
      ]
    },
    {
      "q_id": "q9",
      "text": "Money to me is mainly for…",
      "options": [
        { "opt_id": "q9a", "label": "Saving & security" },
        { "opt_id": "q9b", "label": "Investing & wealth building" },
        { "opt_id": "q9c", "label": "Experiences & memories" },
        { "opt_id": "q9d", "label": "Giving back / philanthropy" },
        { "opt_id": "q9e", "label": "Living comfortably day-to-day" }
      ]
    },
    {
      "q_id": "q10",
      "text": "Family life perspective:",
      "options": [
        { "opt_id": "q10a", "label": "Want kids in the near future" },
        { "opt_id": "q10b", "label": "Kids someday, not soon" },
        { "opt_id": "q10c", "label": "Happier without children" },
        { "opt_id": "q10d", "label": "Open to whatever unfolds" },
        { "opt_id": "q10e", "label": "Prefer not to say yet" }
      ]
    },
    {
      "q_id": "q11",
      "text": "Choose the values you hold dearest:",
      "options": [
        { "opt_id": "q11a", "label": "Honesty & integrity" },
        { "opt_id": "q11b", "label": "Kindness & empathy" },
        { "opt_id": "q11c", "label": "Ambition & drive" },
        { "opt_id": "q11d", "label": "Adventure & spontaneity" },
        { "opt_id": "q11e", "label": "Stability & reliability" }
      ]
    },
    {
      "q_id": "q12",
      "text": "Right now, I’m looking for…",
      "options": [
        { "opt_id": "q12a", "label": "Long-term commitment" },
        { "opt_id": "q12b", "label": "Open to long-term but casual start" },
        { "opt_id": "q12c", "label": "Short-term fun / dating" },
        { "opt_id": "q12d", "label": "Friendship that could evolve" },
        { "opt_id": "q12e", "label": "Not sure yet" }
      ]
    }
  ], indent=2))
questions_json: list[dict] = json.loads(QUESTIONS_PATH.read_text())

# flat lookup: opt_id → label
opt_lookup = {
    opt["opt_id"]: opt["label"]
    for q in questions_json
    for opt in q["options"]
}

# helper: map q_id -> question text
qtext = {q["q_id"]: q["text"] for q in questions_json}

# ────────────────────────────────────────────────────────────────────
# 2.  Prompt-builder helpers
# ────────────────────────────────────────────────────────────────────
def render_preferences(selected_opts: List[str]) -> str:
    """
    Pretty string: q1c: Thoughtful & measured; q3b: Loose outline...
    """
    parts = []
    for oid in selected_opts:
        label = opt_lookup.get(oid, "UNKNOWN")
        parts.append(f"{oid}: {label}")
    return "; ".join(parts)


SYSTEM_PROMPT = (
    "You are a dating expert named Matchmaker AI. Your personality is friendly, witty, and empathetic. "
    "Generate exactly FIVE personalised follow-up questions in JSON array form. "
    "Each element must look like {\"q_id\": \"f1\", \"text\": \"…\"}. "
    "DO NOT return any keys other than q_id and text. No extra keys, no markdown, no prose outside the JSON."
    "Focus on core personality traits, values and interests. The answers to these questions would be later used for matching with other users and checking compatiblity between them based on jaccard score"
    "Use the context to stay relevant.")
def generate_personalised_questions(
    user_id: str,
    selected_opts: List[str],
    bio: str,
) -> list[dict]:
    """
    Calls the chat model once – no vector search – and parses JSON.
    """
    user_pref_text = render_preferences(selected_opts)

    # We also give the model the full questionnaire dictionary so it
    # understands what each option ID refers to.
    questionnaire_stub = json.dumps(questions_json, ensure_ascii=False)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"User ID: {user_id}\n"
                f"Bio: {bio}\n"
                f"Selected MCQs (id → label): {user_pref_text}\n\n"
                f"Full questionnaire JSON (for reference):\n{questionnaire_stub}"
            ),
        },
    ]

    resp = openai.chat.completions.create(
        model="gpt-4o-mini",   # or any chat-capable model you prefer
        messages=messages,
        max_tokens=400,
        temperature=0.7,
    )

    raw = resp.choices[0].message.content.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(
            "Model response was not pure JSON. "
            "Received:\n" + raw
        )



app = Flask(__name__)

@app.route("/generate_questions", methods=["POST"])
def api_generate():
    """
    POST JSON:
    {
      "user_id": "42",
      "opts": ["q1a","q2b", ...],
      "bio":  "string"
    }
    → 200 JSON: { "questions": [ {...}, {...}, ... ] }
    """
    data = request.get_json(force=True)
    try:
        user_id = str(data["user_id"])
        opts    = list(data["opts"])
        bio     = str(data["bio"])
    except (KeyError, TypeError):
        return jsonify({"error": "Expect JSON with user_id, opts, bio"}), 400

    try:
        questions = generate_personalised_questions(user_id, opts, bio)
        return jsonify({"questions": questions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────
# 4.  Dev entry-point
# ─────────────────────────────
if __name__ == "__main__":
    # FLASK_RUN_PORT=5000 flask run   ← or just:
    app.run(host="0.0.0.0", port=5001, debug=True)

# ────────────────────────────────────────────────────────────────────
# 3.  CLI test
# ────────────────────────────────────────────────────────────────────
# if __name__ == "__main__":
#     SAMPLE_OPTS = [
# "q1a","q2a","q3a","q4b","q5a","q6a","q7a","q8a","q9a",
#                    "q10a","q11a","q11d","q12a"
#     ]
#     SAMPLE_BIO = (
#         "I am a student currently pursuing my masters in robotics. Looking for a partner"
#     )
#     out = generate_personalised_questions("user-42", SAMPLE_OPTS, SAMPLE_BIO)
#     print(json.dumps(out, indent=2, ensure_ascii=False))


# ────────────────────────────────────────────────────────────────────
# 5.  Future work: FAISS + RAG
# ────────────────────────────────────────────────────────────────────



# # ────────────────────────────────────────────────────────────────────
# ONLY FOR PREMIUM FEATURE IMPLEMENTATION with SUBSCRIPTION MODEL to Enhance matches based on EMOTIONAL INTELLIGENCE
# # ────────────────────────────────────────────────────────────────────







# load_dotenv()                       # expects OPENAI_API_KEY in .env
# openai.api_key = os.environ["OPENAI_API_KEY"]
# # ---------- 1. Persist / load the questionnaire -------------------
# QUESTIONS_PATH = Path("questions.json")
# if not QUESTIONS_PATH.exists():     # first run – dump the hard-coded list
#     QUESTIONS_PATH.write_text(json.dumps([
#     {
#       "q_id": "q1",
#       "text": "My everyday communication style is…",
#       "options": [
#         { "opt_id": "q1a", "label": "Short & direct" },
#         { "opt_id": "q1b", "label": "Warm & expressive" },
#         { "opt_id": "q1c", "label": "Thoughtful & measured" },
#         { "opt_id": "q1d", "label": "Humorous / meme-heavy" },
#         { "opt_id": "q1e", "label": "Depends on the person" }
#       ]
#     },
#     {
#       "q_id": "q2",
#       "text": "How do you recharge your social battery?",
#       "options": [
#         { "opt_id": "q2a", "label": "Big parties give me energy" },
#         { "opt_id": "q2b", "label": "Small hangouts are perfect" },
#         { "opt_id": "q2c", "label": "Solo time is essential" },
#         { "opt_id": "q2d", "label": "Balanced mix of everything" },
#         { "opt_id": "q2e", "label": "It changes week-to-week" }
#       ]
#     },
#     {
#       "q_id": "q3",
#       "text": "Planning style for trips or projects:",
#       "options": [
#         { "opt_id": "q3a", "label": "Detailed checklist & timeline" },
#         { "opt_id": "q3b", "label": "Loose outline, improvise later" },
#         { "opt_id": "q3c", "label": "Spontaneous—decide on the day" },
#         { "opt_id": "q3d", "label": "Last-minute crunch works best" },
#         { "opt_id": "q3e", "label": "Collaborative planning with others" }
#       ]
#     },
#     {
#       "q_id": "q4",
#       "text": "When conflict appears, I usually…",
#       "options": [
#         { "opt_id": "q4a", "label": "Address it calmly right away" },
#         { "opt_id": "q4b", "label": "Take time, then talk it out" },
#         { "opt_id": "q4c", "label": "Find a compromise quickly" },
#         { "opt_id": "q4d", "label": "Prefer to let it blow over" },
#         { "opt_id": "q4e", "label": "Avoid confrontation altogether" }
#       ]
#     },
#     {
#       "q_id": "q5",
#       "text": "Which life priorities resonate most with you?",
#       "options": [
#         { "opt_id": "q5a", "label": "Career growth" },
#         { "opt_id": "q5b", "label": "Creative expression" },
#         { "opt_id": "q5c", "label": "Community & service" },
#         { "opt_id": "q5d", "label": "Travel & new experiences" },
#         { "opt_id": "q5e", "label": "Health & wellbeing" }
#       ]
#     },
#     {
#       "q_id": "q6",
#       "text": "Your ideal weekend looks like…",
#       "options": [
#         { "opt_id": "q6a", "label": "Outdoor adventure" },
#         { "opt_id": "q6b", "label": "Café-hopping & city strolls" },
#         { "opt_id": "q6c", "label": "Game / movie marathon at home" },
#         { "opt_id": "q6d", "label": "Learning a new skill or hobby" },
#         { "opt_id": "q6e", "label": "Volunteering / community event" }
#       ]
#     },
#     {
#       "q_id": "q7",
#       "text": "Fitness routine that actually sticks:",
#       "options": [
#         { "opt_id": "q7a", "label": "Daily gym / running plan" },
#         { "opt_id": "q7b", "label": "Team or club sports" },
#         { "opt_id": "q7c", "label": "Yoga / Pilates / meditation" },
#         { "opt_id": "q7d", "label": "Dance or movement classes" },
#         { "opt_id": "q7e", "label": "Not big on regular workouts" }
#       ]
#     },
#     {
#       "q_id": "q8",
#       "text": "Topics you never tire of discussing:",
#       "options": [
#         { "opt_id": "q8a", "label": "Science & technology" },
#         { "opt_id": "q8b", "label": "Arts & culture" },
#         { "opt_id": "q8c", "label": "Global issues & politics" },
#         { "opt_id": "q8d", "label": "Personal growth & psychology" },
#         { "opt_id": "q8e", "label": "Sports & fitness" }
#       ]
#     },
#     {
#       "q_id": "q9",
#       "text": "Money to me is mainly for…",
#       "options": [
#         { "opt_id": "q9a", "label": "Saving & security" },
#         { "opt_id": "q9b", "label": "Investing & wealth building" },
#         { "opt_id": "q9c", "label": "Experiences & memories" },
#         { "opt_id": "q9d", "label": "Giving back / philanthropy" },
#         { "opt_id": "q9e", "label": "Living comfortably day-to-day" }
#       ]
#     },
#     {
#       "q_id": "q10",
#       "text": "Family life perspective:",
#       "options": [
#         { "opt_id": "q10a", "label": "Want kids in the near future" },
#         { "opt_id": "q10b", "label": "Kids someday, not soon" },
#         { "opt_id": "q10c", "label": "Happier without children" },
#         { "opt_id": "q10d", "label": "Open to whatever unfolds" },
#         { "opt_id": "q10e", "label": "Prefer not to say yet" }
#       ]
#     },
#     {
#       "q_id": "q11",
#       "text": "Choose the values you hold dearest:",
#       "options": [
#         { "opt_id": "q11a", "label": "Honesty & integrity" },
#         { "opt_id": "q11b", "label": "Kindness & empathy" },
#         { "opt_id": "q11c", "label": "Ambition & drive" },
#         { "opt_id": "q11d", "label": "Adventure & spontaneity" },
#         { "opt_id": "q11e", "label": "Stability & reliability" }
#       ]
#     },
#     {
#       "q_id": "q12",
#       "text": "Right now, I’m looking for…",
#       "options": [
#         { "opt_id": "q12a", "label": "Long-term commitment" },
#         { "opt_id": "q12b", "label": "Open to long-term but casual start" },
#         { "opt_id": "q12c", "label": "Short-term fun / dating" },
#         { "opt_id": "q12d", "label": "Friendship that could evolve" },
#         { "opt_id": "q12e", "label": "Not sure yet" }
#       ]
#     }
#   ], indent=2))

# questions_json = json.loads(QUESTIONS_PATH.read_text())

# # ---------- 2. Build / cache embeddings with FAISS ---------------
# EMB_CACHE = Path("questions.faiss")
# DIM       = 1536                    # dimension for text-embedding-3-small

# def build_faiss():
#     docs, meta = [], []
#     for q in questions_json:
#         q_text = q["text"]
#         docs.append(q_text)
#         meta.append({"q_id": q["q_id"], "content": q_text})
#         for opt in q["options"]:
#             o_text = f"{q_text} -> {opt['label']}"
#             docs.append(o_text)
#             meta.append({"q_id": q["q_id"], "opt_id": opt["opt_id"], "content": o_text})

#     # Batch-embed ↓
#     embs = []
#     for i in range(0, len(docs), 100):
#         chunk = docs[i : i + 100]
#         resp  = openai.embeddings.create(model="text-embedding-3-small", input=chunk)
#         embs.extend([e.embedding for e in resp.data])

#     embs = np.array(embs, dtype="float32")
#     index = faiss.IndexFlatIP(DIM)
#     index.add(embs)
#     faiss.write_index(index, str(EMB_CACHE))
#     Path("questions.meta.json").write_text(json.dumps(meta))
#     print("FAISS store built!")

# if not EMB_CACHE.exists():
#     build_faiss()

# index = faiss.read_index(str(EMB_CACHE))
# meta  = json.loads(Path("questions.meta.json").read_text())

# # ---------- 3. Helper: human-readable summary of user answers -----
# opt_lookup = {opt["opt_id"]: opt["label"]
#               for q in questions_json for opt in q["options"]}

# def render_preferences(selected_opts: List[str]) -> str:
#     parts = []
#     for oid in selected_opts:
#         label = opt_lookup.get(oid, "?")
#         parts.append(f"{oid}: {label}")
#     return "; ".join(parts)

# # ---------- 4. Retrieval step ------------------------------------
# def retrieve_context(selected_opts: List[str], top_k: int = 10) -> str:
#     """
#     Embed the rendered preference text and pull top-k closest facts
#     from the FAISS store. Returns newline-separated snippets.
#     """
#     query = render_preferences(selected_opts)
#     q_emb = np.array(
#         openai.embeddings.create(
#             model="text-embedding-3-small", input=query
#         ).data[0].embedding,
#         dtype="float32",
#     )
#     D, I = index.search(q_emb[None, :], top_k)
#     snippets = [meta[i]["content"] for i in I[0]]
#     return "\n".join(snippets)

# # ---------- 5. Main generation call ------------------------------
# SYSTEM = (
#     "You are Matchmaker AI, a witty, friendly, empathetic dating expert. "
#     "Generate exactly FIVE personalised follow-up questions in JSON array form. "
#     "Each element must look like {\"q_id\": \"f1\", \"text\": \"…\"}. "
#     "DO NOT return any keys other than q_id and text. "
#     "Focus on core personality traits and interests. "
#     "Use the context to stay relevant."
# )

# def generate_personalised_questions(
#     user_id: str,
#     selected_opts: List[str],
#     bio: str,
# ) -> List[dict]:
#     context = retrieve_context(selected_opts)
#     user_pref_text = render_preferences(selected_opts)

#     messages = [
#         {"role": "system",    "content": SYSTEM},
#         {"role": "user",      "content": f"User ID: {user_id}\nBio: {bio}"
#                                          f"\nSelected MCQs: {user_pref_text}"
#                                          f"\n\nRelevant facts:\n{context}"},
#     ]

#     resp = openai.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=messages,
#         max_tokens=400,
#         temperature=0.7,
#     )

#     # The assistant should reply with raw JSON text → parse
#     try:
#         return json.loads(resp.choices[0].message.content)
#     except json.JSONDecodeError as e:
#         raise ValueError("Model did not return valid JSON") from e

# # ---------- 6. CLI test ------------------------------------------
# if __name__ == "__main__":
#     SAMPLE_OPTS = [
#         "q1c","q1d","q2b","q3b","q4c","q5b","q6b","q7b","q8b",
#         "q9c","q10b","q11a","q11c","q12a"
#     ]
#     SAMPLE_BIO = "I am an outgoing student currently pursuing my masters in robotics"
#     out = generate_personalised_questions("user-42", SAMPLE_OPTS, SAMPLE_BIO)
#     print(json.dumps(out, indent=2))

