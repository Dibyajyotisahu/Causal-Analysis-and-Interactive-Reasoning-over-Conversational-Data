import json
import os

RAW_PATH = "C:\\Users\\acer\\OneDrive\\Desktop\\iitbbsr\\data\\raw\\Conversational_Transcript_Dataset.json"
OUT_PATH = "C:\\Users\\acer\\OneDrive\\Desktop\\iitbbsr\\data\\proceed\\normalized_conversations.json"

os.makedirs("data/processed", exist_ok=True)


def normalize_dataset(raw_json):
    normalized_conversations = []

    transcripts = raw_json.get("transcripts", [])

    for transcript in transcripts:
        call_id = transcript.get("transcript_id")

        # You can refine outcome mapping later (escalation, complaint, etc.)
        outcome = transcript.get("intent", "unknown").lower()

        turns = []
        conversation = transcript.get("conversation", [])

        for idx, turn in enumerate(conversation, start=1):
            speaker_raw = turn.get("speaker", "").lower()

            # Normalize speaker
            if speaker_raw == "agent":
                speaker = "agent"
            elif speaker_raw == "customer":
                speaker = "customer"
            else:
                speaker = "unknown"

            text = turn.get("text", "").strip()

            if not text:
                continue

            turns.append(
                {
                    "turn_id": idx,
                    "speaker": speaker,
                    "text": text
                }
            )

        # Skip malformed entries
        if not call_id or not turns:
            continue

        normalized_conversations.append(
            {
                "call_id": call_id,
                "outcome": outcome,
                "turns": turns
            }
        )

    return normalized_conversations


def main():
    with open(RAW_PATH, "r", encoding="utf-8") as f:
        raw_json = json.load(f)

    normalized = normalize_dataset(raw_json)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(normalized, f, indent=2, ensure_ascii=False)

    print(f" Normalized {len(normalized)} conversations")
    print(f" Output saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
