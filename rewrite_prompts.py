import glob
from pathlib import Path

def rewrite_prompt(content, filename):
    # This is a basic rule-based formatting upgrade to add best-practice tags.
    # A true rewrite would use an LLM, but we'll apply standard clear sections.
    # Doing a structural enhancement here:
    
    parts = content.split('\n\n')
    if not parts:
        return content

    title = parts[0].strip()
    rest = '\n\n'.join(parts[1:])
    
    new_content = f"""{title}

<role>
You are an expert AI agent in the SimpCode system, operating in the role of {filename.replace('.md', '').replace('_', ' ').title()}.
</role>

<instructions>
{rest}
</instructions>

<constraints>
- Strictly follow the output schema provided in the user prompt.
- Do not hallucinate or guess. Rely ONLY on the provided context.
- Be concise, professional, and deterministic. No conversational filler ("Here is the plan...").
- Adhere to the principles of SimpCode SDD: "Think Before You Act," "Context is King," and "Wiki-First".
</constraints>
"""
    return new_content

for p in glob.glob("src/simpcode/core/prompts/*.md"):
    if "base_principles.md" in p: continue
    path = Path(p)
    content = path.read_text()
    if "<role>" not in content:
        path.write_text(rewrite_prompt(content, path.name))
        print(f"Rewrote {path.name}")
