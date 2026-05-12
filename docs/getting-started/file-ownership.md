# Understanding File Ownership

After running `simp init`, SimpCode creates several files and directories to maintain its intelligence layer. Understanding which files you can safely edit and which should be left to the system is crucial for maintaining the integrity of the Semantic Wiki.

---

## User-Editable Files

These files are designed to be modified by you to guide SimpCode's behavior.

### `SPEC.md`
- **Owner**: User
- **Purpose**: The authoritative project specification and target-state requirements.
- **Safe to Edit?**: **YES.** Keep this current when the product direction, architecture, or constraints change.

### `SIMP.md`
- **Owner**: Shared (Primarily User)
- **Purpose**: The high-level project manifest and project overview.
- **Safe to Edit?**: **YES.** Use it to summarize the repository structure, major modules, and important notes for SimpCode.

### `src/simpcode/core/prompts/`
- **Owner**: SimpCode
- **Purpose**: Internal reasoning prompts used by the framework itself.
- **Safe to Edit?**: **Only if you are modifying SimpCode itself.** These are not project-onboarding files.

---

## SimpCode-Managed Files

These files are the "internal brain" of the system. Manual edits can cause synchronization errors or hallucinations.

### `.simp/wiki/` (Directory)
- **Owner**: SimpCode
- **Purpose**: Contains the semantic Wiki nodes (knowledge base).
- **Safe to Edit?**: **NO.** These files are managed by the engine. If you manually edit a wiki node, the hashes will mismatch and SimpCode will consider the knowledge stale or corrupted.
- **How to update**: If the information here is wrong, run `simp sync` or make the corresponding code changes and let SimpCode refresh the Wiki.

### `.simp/index.json`
- **Owner**: SimpCode
- **Purpose**: The master index that maps file hashes to wiki entries.
- **Safe to Edit?**: **NO.** Deleting or corrupting this file will require a full `simp init --force` to recover.

---

## ⚖️ Summary Table

| File/Path | Managed By | User Safe? | Action on Conflict |
| :--- | :--- | :--- | :--- |
| `SPEC.md` | User | Yes | Edit to change the target-state requirements. |
| `SIMP.md` | User/AI | Yes | Edit to clarify the project overview. |
| `src/simpcode/core/prompts/` | SimpCode | No for project users | Internal framework prompts, not onboarding files. |
| `.simp/wiki/` | SimpCode | No | Run `simp sync` to fix. |
| `.simp/index.json`| SimpCode | No | Run `simp init` to fix. |

---

## Best Practice: The "Rule of Thumb"
If a file is inside the `.simp/` hidden directory, **do not touch it.** 
If it is a `.md` file in your repository root (`SIMP.md`, `SPEC.md`), it is **yours to control**. If it lives under `.simp/`, it is managed by SimpCode.
