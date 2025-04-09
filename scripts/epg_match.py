import sys
import json
import re
import os
from functools import lru_cache
from rapidfuzz import fuzz, process
from sentence_transformers import util
from sentence_transformers import SentenceTransformer as st

SENTENCE_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_PATH = os.path.join("/app", "models", "all-MiniLM-L6-v2")

BEST_FUZZY_THRESHOLD = 85
LOWER_FUZZY_THRESHOLD = 40
EMBED_SIM_THRESHOLD = 0.65

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def normalize_preferred_region(raw):
    raw = raw.lower().strip()
    if not raw:
        return ""
    if raw.startswith("."):
        return raw[:3]  # e.g. '.us'
    return "." + raw[:2]

@lru_cache(maxsize=None)
def remove_region_suffix(name):
    name_lower = name.lower().strip()
    match = re.search(r'(\.[a-z]{2})$', name_lower)
    if match:
        region = match.group(1)  # e.g. ".us"
        base_name = name_lower[:-len(region)].strip()
        return base_name, region
    else:
        return name_lower, None

def process_data(input_data):
    raw_preferred = input_data.get("region_code", "")
    preferred_region = normalize_preferred_region(raw_preferred)  # e.g. ".us"
    print(f"Preferred Region is: {preferred_region}")

    # If not present locally, download:
    os.makedirs(MODEL_PATH, exist_ok=True)
    if not os.path.exists(os.path.join(MODEL_PATH, "config.json")):
        eprint(f"Local model not found in {MODEL_PATH}; downloading from {SENTENCE_MODEL_NAME}...")
        st_model = st(SENTENCE_MODEL_NAME, cache_folder=MODEL_PATH)
    else:
        eprint(f"Loading local model from {MODEL_PATH}")
        st_model = st(MODEL_PATH)

    channels = input_data["channels"]
    epg_data = input_data["epg_data"]

    # Precompute normalized base names for EPG (using norm_name field)
    for row in epg_data:
        epg_base, epg_region = remove_region_suffix(row["norm_name"])
        row["norm_base"] = epg_base
        row["region_suffix"] = epg_region  # e.g. ".us" if matches

    # Batch-encode all epg base names for embedding comparisons
    epg_embeddings = None
    if any(row["norm_base"] for row in epg_data):
        epg_embeddings = st_model.encode(
            [row["norm_base"] for row in epg_data],
            convert_to_tensor=True
        )

    channels_to_update = []
    matched_channels = []

    for chan in channels:
        # Try a direct match using tvg_id if available.
        if chan["tvg_id"]:
            direct_match = next((epg for epg in epg_data if epg["tvg_id"] == chan["tvg_id"]), None)
            if direct_match:
                chan["epg_data_id"] = direct_match["id"]
                chan["candidate_matches"] = [{
                    "epg_id": direct_match["id"],
                    "tvg_id": direct_match["tvg_id"],
                    "total_score": BEST_FUZZY_THRESHOLD + 1,
                    "note": "direct match"
                }]
                eprint(f"Channel {chan['id']} '{chan['name']}' => Direct match found by tvg_id={chan['tvg_id']}")
                channels_to_update.append(chan)
                matched_channels.append((chan["id"], chan["name"], direct_match["tvg_id"]))
                continue

        fallback_name = chan["name"]
        chan_base, chan_region = remove_region_suffix(chan.get("norm_chan", chan["name"]))
        if not chan_base:
            eprint(f"Channel {chan['id']} '{chan['name']}' => empty after normalization, skipping")
            continue

        candidate_matches = []
        for row_idx, row in enumerate(epg_data):
            epg_base = row["norm_base"]
            if not epg_base:
                continue
            base_score = fuzz.ratio(chan_base, epg_base)
            bonus = 0
            if chan_region and row["region_suffix"]:
                bonus += 15 if chan_region == row["region_suffix"] else -5
            if preferred_region and row["region_suffix"]:
                bonus += 10 if row["region_suffix"] == preferred_region else -5
            total_score = base_score + bonus

            candidate_matches.append({
                "epg_row": row,
                "fuzzy_score": base_score,
                "bonus": bonus,
                "total_score": total_score,
                "row_idx": row_idx,
            })
        chan["candidate_matches"] = candidate_matches

        if not candidate_matches:
            eprint(f"Channel {chan['id']} '{fallback_name}' => no candidates found")
            continue

        # ---- FORCE preferred region candidate selection ----
        # First look for candidates whose EPG tvg_id ends with the preferred region.
        if preferred_region:
            forced_candidates = [
                c for c in candidate_matches
                if c["epg_row"]["tvg_id"].lower().endswith(preferred_region)
            ]
            if forced_candidates:
                best_candidate = max(forced_candidates, key=lambda x: x["total_score"])
            else:
                best_candidate = max(candidate_matches, key=lambda x: x["total_score"])
        else:
            best_candidate = max(candidate_matches, key=lambda x: x["total_score"])
        # --------------------------------------------------------

        eprint(f"Channel {chan['id']} '{fallback_name}' => best candidate = {best_candidate['epg_row']['tvg_id']}, "
               f"score={best_candidate['total_score']:.1f}")

        if best_candidate["total_score"] >= BEST_FUZZY_THRESHOLD:
            best_epg = best_candidate["epg_row"]
            chan["epg_data_id"] = best_epg["id"]
            channels_to_update.append(chan)
            matched_channels.append((chan["id"], fallback_name, best_epg["tvg_id"]))
            eprint(f"Channel {chan['id']} '{fallback_name}' => Matched tvg_id={best_epg['tvg_id']} "
                   f"(total_score={best_candidate['total_score']:.1f})")
        else:
            # Optional embedding similarity check
            if best_candidate["total_score"] >= LOWER_FUZZY_THRESHOLD and epg_embeddings is not None:
                chan_embedding = st_model.encode(chan_base, convert_to_tensor=True)
                sim_scores = util.cos_sim(chan_embedding, epg_embeddings)[0]
                sim_score = float(sim_scores[best_candidate["row_idx"]])
                eprint(f"Channel {chan['id']} '{fallback_name}' => Top candidate fuzzy={best_candidate['total_score']:.1f}, "
                       f"cos-sim={sim_score:.2f}")
                if sim_score >= EMBED_SIM_THRESHOLD:
                    best_epg = best_candidate["epg_row"]
                    chan["epg_data_id"] = best_epg["id"]
                    channels_to_update.append(chan)
                    matched_channels.append((chan["id"], fallback_name, best_epg["tvg_id"]))
                    eprint(f"Channel {chan['id']} '{fallback_name}' => Matched EPG tvg_id={best_epg['tvg_id']} "
                           f"(fuzzy={best_candidate['fuzzy_score']}, total_score={best_candidate['total_score']:.1f}, "
                           f"cos-sim={sim_score:.2f})")
                else:
                    eprint(f"Channel {chan['id']} '{fallback_name}' => Embedding similarity {sim_score:.2f} below threshold, skipping")
            else:
                eprint(f"Channel {chan['id']} '{fallback_name}' => Best candidate score {best_candidate['total_score']:.1f} below threshold, skipping")

    return {
        "channels_to_update": channels_to_update,
        "matched_channels": matched_channels,
    }


def main():
    input_file_path = sys.argv[1]
    with open(input_file_path, 'r') as f:
        input_data = json.load(f)
    
    # Process data with the ML model (or your logic)
    result = process_data(input_data)

    # Output result to stdout
    print(json.dumps(result))

if __name__ == "__main__":
    main()
