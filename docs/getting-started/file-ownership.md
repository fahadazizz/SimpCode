# Understanding File Ownership

After running `simp init`, SimpCode creates several files and directories to maintain its intelligence layer. Understanding which files you can safely edit and which should be left to the system is crucial for maintaining the integrity of the Semantic Wiki.

---

## User-Editable Files

These files are designed to be modified by you to guide SimpCode's behavior.

### `AGENT.md`
- **Owner**: User
- **Purpose**: This is your "Rules of Engagement." 
- **Wait, can SimpCode edit this?**: SimpCode will never modify this file unless you explicitly run a command like `simp do "Update AGENT.md with rule X"`. 
- **Safe to Edit?**: **YES.** You should keep this file updated with your project's coding standards, naming conventions, and architectural preferences.

### `SIMP.md`
- **Owner**: Shared (Primarily User)
- **Purpose**: The high-level Project Manifest.
- **Safe to Edit?**: **YES.** While SimpCode generates this during `init`, you can manually refine the "Project Goal" or "Tech Stack" sections to provide better context for the AI.

---

## SimpCode-Managed Files

These files are the "internal brain" of the system. Manual edits can cause synchronization errors or hallucinations.

### `.simp/wiki/` (Directory)
- **Owner**: SimpCode
- **Purpose**: Contains the Semantic Wiki nodes (knowledge base).
- **Safe to Edit?**: **NO.** These files are managed by the engine. If you manually edit a wiki node, the cryptographic hashes will mismatch, and SimpCode will consider its knowledge "corrupted."
- **How to update**: If the information here is wrong, run `simp sync` or perform the manual code changes and SimpCode will update the wiki automatically.

### `.simp/index.json`
- **Owner**: SimpCode
- **Purpose**: The master index that maps file hashes to wiki entries.
- **Safe to Edit?**: **NO.** Deleting or corrupting this file will require a full `simp init --force` to recover.

---

## ⚖️ Summary Table

| File/Path | Managed By | User Safe? | Action on Conflict |
| :--- | :--- | :--- | :--- |
| `AGENT.md` | User | Yes | Edit freely to change AI behavior. |
| `SIMP.md` | User/AI | Yes | Edit to clarify project purpose. |
| `.simp/wiki/` | SimpCode | No | Run `simp sync` to fix. |
| `.simp/index.json`| SimpCode | No | Run `simp init` to fix. |

---

## Best Practice: The "Rule of Thumb"
If a file is inside the `.simp/` hidden directory, **do not touch it.** 
If it is a `.md` file in your repository root (`SIMP.md`, `AGENT.md`), it is **yours to control.**
