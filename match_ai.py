import itertools, numpy as np

Json_Quiz = {
  "questionnaire_id": "core_match_v2",
  "title": "Core-Match Starter Quiz",
  "type": "MULTICHOICE",
  "allow_multiple_selection": True,
  "questions": [
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
  ]
}

# ------------------------------------------------------------------
# 1)  QUIZ SCHEMA
# ------------------------------------------------------------------
QUESTION_OPTS = {
    "q1":  ["q1a","q1b","q1c","q1d","q1e"],
    "q2":  ["q2a","q2b","q2c","q2d","q2e"],
    "q3":  ["q3a","q3b","q3c","q3d","q3e"],
    "q4":  ["q4a","q4b","q4c","q4d","q4e"],
    "q5":  ["q5a","q5b","q5c","q5d","q5e"],
    "q6":  ["q6a","q6b","q6c","q6d","q6e"],
    "q7":  ["q7a","q7b","q7c","q7d","q7e"],
    "q8":  ["q8a","q8b","q8c","q8d","q8e"],
    "q9":  ["q9a","q9b","q9c","q9d","q9e"],
    "q10": ["q10a","q10b","q10c","q10d","q10e"],
    "q11": ["q11a","q11b","q11c","q11d","q11e"],
    "q12": ["q12a","q12b","q12c","q12d","q12e"]
}

QUESTION_WEIGHT = {
    "q1": 1.2, "q2": 2.3, "q3": 1.9, "q4": 2.5,
    "q5": 1.6, "q6": 1.2, "q7": 1.1, "q8": 1.3,
    "q9": 1.1, "q10": 2.0, "q11": 3.2, "q12": 3.0
}

# ------------------------------------------------------------------
# 2)  SEMANTIC GROUPING  (only where it matters)
# ------------------------------------------------------------------
CATEGORY_GROUPS = {
    "q10": {                         # Family / kids
        "wants_kids" : {"q10a", "q10b"},
        "no_kids"    : {"q10c"},
        "flexible"   : {"q10d", "q10e"}
    },
    "q12": {                         # Relationship goal
        "serious"  : {"q12a", "q12b"},
        "casual"   : {"q12c", "q12d"},
        "unsure"   : {"q12e"}
    },
    "q2": {                          # Social energy
        "extro"     : {"q2a"},
        "intro"     : {"q2c"},
        "balanced"  : {"q2b", "q2d", "q2e"}
    },
    "q4": {                          # Conflict style
        "direct"    : {"q4a", "q4c"},
        "reflect"   : {"q4b"},
        "avoid"     : {"q4d", "q4e"}
    }
    # Leave all other questions un-grouped for finer distinction
}

# ------------------------------------------------------------------
# 3)  BUILD CATEGORY-LEVEL VECTORS
# ------------------------------------------------------------------
vector_bits        = []   # names like "q2:extro" or raw opt_id
vector_weights     = []   # one element per bit
vector_parent_q    = []   # which question produced this bit

for q_id, opts in QUESTION_OPTS.items():
    if q_id in CATEGORY_GROUPS:
        for cat, group in CATEGORY_GROUPS[q_id].items():
            vector_bits.append(f"{q_id}:{cat}")
            vector_weights.append(QUESTION_WEIGHT[q_id])
            vector_parent_q.append(q_id)
    else:
        for opt in opts:
            vector_bits.append(opt)
            vector_weights.append(QUESTION_WEIGHT[q_id])
            vector_parent_q.append(q_id)

IDX = {bit: i for i, bit in enumerate(vector_bits)}
W   = np.array(vector_weights, dtype=float)

# Core / life masks use the PARENT QUESTION label
CORE_Q = {"q2", "q4", "q11", "q12"}
mask_core = np.array([pq in CORE_Q for pq in vector_parent_q])
mask_life = ~mask_core

# Deal-breakers operate on whole questions
DEAL_Q = {"q10", "q12"}

# ------------------------------------------------------------------
# 4)  USER VECTORISATION
# ------------------------------------------------------------------
def answers_to_vector(picks):
    v = np.zeros(len(vector_bits), dtype=int)

    # Pass 1: set grouped categories
    grouped_seen = {}
    for q_id, group in CATEGORY_GROUPS.items():
        shared = set(picks) & set().union(*group.values())
        for cat, members in group.items():
            if shared & members:
                v[IDX[f"{q_id}:{cat}"]] = 1
                grouped_seen.update({m: True for m in members})

    # Pass 2: set remaining un-grouped options
    for opt in picks:
        if opt not in grouped_seen:        # skip ones already mapped to a category
            v[IDX[opt]] = 1
    return v

# ------------------------------------------------------------------
# 5)  KERNELS & CALIBRATION
# ------------------------------------------------------------------
def weighted_jaccard(u, v, mask):
    inter = np.sum(W * mask * np.minimum(u, v))
    union = np.sum(W * mask * np.maximum(u, v))
    return 0.0 if union == 0 else inter / union

def dealbreaker_fail(picks_u, picks_v):
    for q in DEAL_Q:
        cats_u = {cat for cat, members in CATEGORY_GROUPS.get(q, {}).items()
                         if members & set(picks_u)} or {opt for opt in picks_u if opt in QUESTION_OPTS[q]}
        cats_v = {cat for cat, members in CATEGORY_GROUPS.get(q, {}).items()
                         if members & set(picks_v)} or {opt for opt in picks_v if opt in QUESTION_OPTS[q]}
        if not (cats_u & cats_v):          # no overlap in that question
            return True
    return False

def calibrated_score(j_core, j_life, k=5, base=0.4):
    raw = 0.6*j_core + 0.4*j_life
    if raw == 0:
        return 0.0
    L     = 1/(1+np.exp(-k*(raw-base)))
    L_max = 1/(1+np.exp(-k*(1-base)))      # so self-match = 100
    return round(10 + 90 * (L/L_max), 2)

# ------------------------------------------------------------------
# 6)  TOP-LEVEL API
# ------------------------------------------------------------------
def compatibility(picks_u, picks_v):
    if dealbreaker_fail(picks_u, picks_v):
        return 0.0
    u_vec, v_vec = answers_to_vector(picks_u), answers_to_vector(picks_v)
    j_core = weighted_jaccard(u_vec, v_vec, mask_core)
    j_life = weighted_jaccard(u_vec, v_vec, mask_life)
    return calibrated_score(j_core, j_life)

def compatibility_matrix(user_answers: dict):
    names = list(user_answers)
    out   = {u:{} for u in names}
    for i,u in enumerate(names):
        for j,v in enumerate(names):
            out[u][v] = compatibility(user_answers[u], user_answers[v]) if j>=i else out[v][u]
    return out

# ------------------------------------------------------------------
# 7)  DEMO
# ------------------------------------------------------------------
if __name__ == "__main__":
    sample_users = {
        "Alex":   ["q1c","q1d","q2b","q3b","q4c","q5b","q6b","q7b","q8b",
                   "q9c","q10b","q11a","q11c","q12a"],
        "Brooke": ["q1a","q2a","q3a","q4b","q5a","q6a","q7a","q8a","q9a",
                   "q10a","q11a","q11d","q12a"],
        "Charlie":["q1e","q2d","q3e","q4e","q5d","q6e","q7e","q8e","q9e",
                   "q10d","q11c","q11e","q12b"]
    }

    from pprint import pprint
    pprint(compatibility_matrix(sample_users))
