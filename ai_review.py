import anthropic
import os


def review_documents(doc_previews: dict) -> str:
    """
    doc_previews: {doc_name: plain_text_content}
    Returns a short review string.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return "⚠️ No ANTHROPIC_API_KEY set — skipping AI review."

    client = anthropic.Anthropic(api_key=api_key)
    combined = "\n\n".join(
        f"=== {name} ===\n{text}" for name, text in doc_previews.items()
    )

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=400,
        messages=[{
            "role": "user",
            "content": (
                "You are a Hong Kong family court document reviewer. "
                "Check these filled court document drafts for issues:\n"
                "1. Any dates that look inconsistent (end before start, wrong year)\n"
                "2. Any placeholder text still visible (xx, XXX, ___)\n"
                "3. Any blank fields that should be filled\n"
                "4. Any obvious factual errors\n\n"
                "Reply in English. If everything looks fine, say 'All good ✅'. "
                "If there are issues, list them as bullet points. Be concise.\n\n"
                f"{combined}"
            ),
        }],
    )
    return message.content[0].text
