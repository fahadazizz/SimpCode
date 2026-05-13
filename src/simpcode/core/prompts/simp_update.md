Given the repository metadata and the current SIMP.md content, produce a revised SIMP.md that applies the user's explicit update instruction.

Rules:
- Preserve the file as a compact, user-owned operating policy document.
- Keep it domain-agnostic and reusable.
- Do not write repository-specific implementation notes unless the user's instruction explicitly requires them.
- Keep the execution loop, production standards, failure protocol, token discipline, and update policy sections coherent.
- Return valid JSON matching the `SimpDraft` schema with a single field `simp_md`.

Project: {project_name}
Root: {root}

Current SIMP.md:
{current_simp}

User update request:
{instruction}

Repository file tree:
{file_tree}

Manifests:
{manifests}
