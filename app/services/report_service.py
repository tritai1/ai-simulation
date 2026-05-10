from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

from app.core.llm import model
from app.orchestration.session_memory import get_memory_context, get_session


OUTPUT_ROOT = Path("gucci_env") / "outputs"


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _gen(prompt: str) -> str:
    resp = model.generate_content(prompt)
    return getattr(resp, "text", None) or str(resp)


def export_module_pack(session_id: str, module: int) -> Dict[str, str]:
    """
    One-click "portfolio pack" export.
    Saves artifacts to disk and returns a dict of {name: path}.
    """
    session = get_session(session_id)
    memory = get_memory_context(session_id, max_turns=50)
    transcript = "\n".join([f'{m["role"]}: {m["content"]}' for m in session.messages[-80:]])

    out_dir = OUTPUT_ROOT / session_id / f"module_{module}"

    if module == 1:
        problem = _gen(
            f"""You are helping produce Module 1 deliverables for a Gucci Group leadership simulation.

Use the conversation context below. Output a 1-page problem statement (max ~350 words) balancing brand autonomy with group needs (mobility, leadership pipeline).

Context (memory + transcript):
{memory}

Transcript:
{transcript}
"""
        )

        csv_matrix = _gen(
            """Create a competency matrix CSV for a Gucci Group leadership model.
Requirements:
- 4 themes: Vision, Entrepreneurship, Passion, Trust
- 3 levels: Level 1 (Emerging), Level 2 (Proficient), Level 3 (Enterprise)
- For each theme x level, provide 2–3 behavior indicators (short phrases).
Output ONLY CSV with header: theme,level,behavior_indicators
Behavior indicators in one cell separated by ' | '.
"""
        )

        ceo_pack = _gen(
            """Draft a 10-slide CEO pack outline for Module 1.
Output as markdown with slide titles and 3–5 bullets each.
Slides must include: context & problem, principles (autonomy vs group), group DNA, competency model overview, level behaviors, use cases, rollout preview, asks/decisions.
"""
        )
        social_posts = _gen(
            """Create 3 short employer-readable social posts (LinkedIn style) about Module 1 progress.
Each post: headline + 3 bullets + neutral closing line.
Output as markdown.
"""
        )
        exec_update = _gen(
            """Create a concise executive update for Module 1 with:
- objective
- what was delivered
- risks
- decisions needed
Output as markdown.
"""
        )

        files = {
            "problem_statement.md": str(out_dir / "problem_statement.md"),
            "competency_matrix.csv": str(out_dir / "competency_matrix.csv"),
            "ceo_pack.md": str(out_dir / "ceo_pack.md"),
            "social_posts.md": str(out_dir / "social_posts.md"),
            "exec_update.md": str(out_dir / "exec_update.md"),
        }
        _write_text(Path(files["problem_statement.md"]), problem.strip())
        _write_text(Path(files["competency_matrix.csv"]), csv_matrix.strip())
        _write_text(Path(files["ceo_pack.md"]), ceo_pack.strip())
        _write_text(Path(files["social_posts.md"]), social_posts.strip())
        _write_text(Path(files["exec_update.md"]), exec_update.strip())
        return files

    if module == 2:
        program_spec = _gen(
            """Create a 360° + coaching program spec (about 5 pages worth of content, but concise).
Must include:
- instrument blueprint (rater groups, scale, items per theme, anonymity rules, language coverage)
- participant + rater journey (comms, deadlines, consent, data privacy)
- coaching program (coach profile, session cadence, goals-to-habits plan)
- vendor plan (build vs buy, benchmarking comparators like CCL, data security)
Output as markdown with clear headings.
"""
        )
        comms = _gen(
            """Create comms templates for the 360° program.
Include: invite email to participant, invite email to raters, reminder, confidentiality/data privacy note, and manager briefing note.
Output as markdown.
"""
        )
        questionnaire = _gen(
            """Create a sample 360° questionnaire section.
Include 4 themes (Vision, Entrepreneurship, Passion, Trust) with 3–4 items each.
Use a 1–5 scale and include 2 open-ended questions.
Output as markdown.
"""
        )
        social_posts = _gen(
            """Create 3 short employer-readable social posts (LinkedIn style) about Module 2 progress.
Focus on 360 design, coaching approach, and ethical implementation.
Output as markdown.
"""
        )
        exec_update = _gen(
            """Create a concise executive update for Module 2 with:
- status
- decisions made (build vs buy, privacy model)
- upcoming milestones
Output as markdown.
"""
        )
        files = {
            "program_spec.md": str(out_dir / "program_spec.md"),
            "comms_templates.md": str(out_dir / "comms_templates.md"),
            "questionnaire_sample.md": str(out_dir / "questionnaire_sample.md"),
            "social_posts.md": str(out_dir / "social_posts.md"),
            "exec_update.md": str(out_dir / "exec_update.md"),
        }
        _write_text(Path(files["program_spec.md"]), program_spec.strip())
        _write_text(Path(files["comms_templates.md"]), comms.strip())
        _write_text(Path(files["questionnaire_sample.md"]), questionnaire.strip())
        _write_text(Path(files["social_posts.md"]), social_posts.strip())
        _write_text(Path(files["exec_update.md"]), exec_update.strip())
        return files

    if module == 3:
        rollout = _gen(
            """Create a rollout playbook for cascading the leadership model across brands/regions.
Must include:
- train-the-trainer plan (phases, audiences, workshop outline)
- checklist + RACI
- regional trainer profile
Output as markdown.
"""
        )
        kpis = _gen(
            """Create a KPI table for adoption + impact measurement.
Include leading + lagging KPIs, definitions, data source, cadence, and owner.
Output as markdown table.
"""
        )
        exec_insights = _gen(
            """Create a sample executive insights one-pager.
Include: adoption snapshot, key themes from 360° insights (aggregated), risks, next actions.
Output as markdown.
"""
        )
        social_posts = _gen(
            """Create 3 short employer-readable social posts (LinkedIn style) about Module 3 rollout.
Focus on training adoption, KPI movement, and change-story.
Output as markdown.
"""
        )
        exec_update = _gen(
            """Create a concise executive update for Module 3 with:
- adoption snapshot
- KPI trend
- risks + mitigations
- asks for next quarter
Output as markdown.
"""
        )
        files = {
            "rollout_playbook.md": str(out_dir / "rollout_playbook.md"),
            "kpi_table.md": str(out_dir / "kpi_table.md"),
            "exec_insights_page.md": str(out_dir / "exec_insights_page.md"),
            "social_posts.md": str(out_dir / "social_posts.md"),
            "exec_update.md": str(out_dir / "exec_update.md"),
        }
        _write_text(Path(files["rollout_playbook.md"]), rollout.strip())
        _write_text(Path(files["kpi_table.md"]), kpis.strip())
        _write_text(Path(files["exec_insights_page.md"]), exec_insights.strip())
        _write_text(Path(files["social_posts.md"]), social_posts.strip())
        _write_text(Path(files["exec_update.md"]), exec_update.strip())
        return files

    raise ValueError("module must be 1, 2, or 3")

