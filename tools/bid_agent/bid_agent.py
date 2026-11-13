"""
BID COORDINATION AGENT
======================
Usage:
  python bid_agent.py "C:\\Jobs\\Sample-Elementary"
  python bid_agent.py "C:\\Jobs\\Sample-Elementary" --project "Sample Elementary School HVAC Replacement"
  python bid_agent.py <job folder> --profile company_profile.json --model claude-opus-5-5

Reads all files in the folder, sends their text to the Anthropic API,
and saves 10 bid deliverables as a text file inside the job folder.

Company details (name, location, PM contact, market focus) come from a
company profile JSON file. See company_profile.example.json.

The API key is read from the ANTHROPIC_API_KEY environment variable only.

Requires:
  pip install --upgrade anthropic PyPDF2 python-docx openpyxl
"""

import sys
import os
import json
import argparse
import datetime
import anthropic

# -- Optional deps (graceful fallback if not installed) ----------------------
try:
    import PyPDF2
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

try:
    from docx import Document as DocxDocument
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    import openpyxl
    HAS_XLSX = True
except ImportError:
    HAS_XLSX = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MODEL = "claude-opus-5-5"
DEFAULT_MAX_TOKENS = 64000
DEFAULT_EFFORT = "high"

# -- Company Profile -----------------------------------------------------------

def default_profile_path():
    """company_profile.json beside the script if present, else the example file."""
    env_path = os.environ.get("BID_AGENT_PROFILE")
    if env_path:
        return env_path
    own = os.path.join(SCRIPT_DIR, "company_profile.json")
    if os.path.isfile(own):
        return own
    return os.path.join(SCRIPT_DIR, "company_profile.example.json")


def load_profile(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"ERROR: Could not read company profile {path}: {e}")
        sys.exit(1)

    def text(key, fallback):
        value = data.get(key)
        return str(value).strip() if value not in (None, "") else fallback

    def items(key, fallback):
        value = data.get(key)
        if isinstance(value, list) and value:
            return [str(v) for v in value]
        if isinstance(value, str) and value.strip():
            return [value.strip()]
        return fallback

    return {
        "legal_name": text("company_legal_name", "[Company Legal Name]"),
        "dba": text("company_dba", text("company_legal_name", "[Company DBA]")),
        "company_type": text("company_type", "commercial MEP subcontractor"),
        "location": text("location", "[Company City, State]"),
        "self_perform": items("self_perform", ["HVAC"]),
        "subcontracted": items("subcontracted", ["electrical"]),
        "market_focus": text("market_focus", "commercial projects"),
        "bonding_capacity": text("bonding_capacity", ""),
        "pm_software": text("pm_software", ""),
        "pm_name": text("pm_name", "[PM Name]"),
        "pm_title": text("pm_title", "Project Manager"),
        "pm_phone": text("pm_phone", "[PM Phone]"),
        "pm_email": text("pm_email", "[PM Email]"),
    }


def join_words(words):
    if len(words) <= 1:
        return "".join(words)
    return ", ".join(words[:-1]) + " and " + words[-1]


def pm_contact_line(p):
    return f"{p['pm_name']} | {p['pm_phone']} | {p['pm_email']}"


# -- System Prompt -------------------------------------------------------------

SYSTEM_PROMPT_TEMPLATE = """SYSTEM PROMPT - BID COORDINATION AGENT

You are a senior bid coordination assistant for {legal_name}
("{dba}"), a {company_type} based in {location}.
Your operator is {pm_name}, {pm_title}.

{dba} self-performs {self_perform}. {subcontracted_sentence}
Primary market: {market_focus}.
{company_extras}
WHEN GIVEN A PROJECT FOLDER, you will automatically read every file in it -
blueprints, specifications (all divisions), addendums, bid forms, RFI logs,
and any vendor quotes - then produce ALL of the following deliverables
without being asked for each one individually.

===================================================
DEFINITION OF DONE - ALL DELIVERABLES REQUIRED
===================================================

1. SCOPE OF WORK (Internal Document)
   - Project header: bid or solicitation number, GC partner, contract start,
     phase substantial completion (SC) dates, liquidated damages (LDs),
     work hours, summer window if applicable
   - Base Bid: detailed scope by trade/system (Div 22 Plumbing, Div 23 HVAC,
     Div 26 Electrical, Sheet Metal, Insulation, Controls/BAS, Water Treatment,
     Crane/Rigging)
   - Each Alternate: separate section with removals, installations, piping,
     electrical, controls, warranties
   - Scope exclusions: what is NOT {dba} scope (GC scope items)
   - Coordination interface points with GC
   - Write it in plain language like you are briefing a foreman, not quoting
     the spec. Include quantities, sizes, brands (basis of design), and counts.

2. VENDOR RFQ LIST (Grouped by Rep/Category)
   Group all spec'd equipment and subcontracted scope into the following
   categories - add others if the project requires them:
   - Air distribution / fan rep - exhaust fans, VFDs, air devices
   - Specialty equipment rep - specialty and custom equipment
   - Packaged and applied HVAC equipment rep(s) - RTUs, chillers, WSHPs,
     applied equipment (one line per manufacturer or rep)
   - Pump and hydronic specialties rep - pumps, hydronic specialties
   - Plumbing Sub - all fixtures, sanitary, domestic water, gas piping
   - Electrical Sub - full Div 26 scope, quoted as: Base Bid + each Alternate
     + Unit Prices separately
   - Controls/BAS Sub - approved systems only per spec; full DDC scope,
     FCU retrofit counts, utility metering
   - Welding Sub - hydronic welded joints, structural steel, AWS certs required
   - Insulation Sub - HVAC piping, plumbing piping, duct insulation per spec
   - Crane/Rigging - lift plan with equipment weights, crane tonnage required,
     hours estimated
   - Sheet Metal/Ductwork - transitions, diffusers, fire/smoke dampers,
     duct leakage testing
   - Concrete Sub - equipment pads, piers, specs (PSI, rebar, air entrainment)
   - Water Treatment - initial treatment + annual service program
   - Painting/Coatings - gas piping yellow epoxy, pipe markers, equipment ID
   - Fire Protection / Kitchen Hood - NFPA 96 if kitchen scope present
   - TAB - air and water side quantities for reference/backup pricing only
     (the owner often selects the TAB firm on school district projects)
   For each line item: equipment tag, model/basis of design, quantity,
   voltage/phase, and the spec section that governs it.

3. SUBMITTAL LOG
   Every spec section requiring a submittal, with:
   - Spec section number and title
   - Submittal type (shop drawings, product data, samples, calculations)
   - Responsible party ({dba} self-perform, Electrical Sub, Controls Sub, etc.)
   - Projected submission date (working back from Phase 1 SC)
   - Review period (use the spec; if silent, assume 15 days, longer when
     several parties review)
   - Status column (blank at bid stage)
   Flag the critical path submittal.

4. MILESTONE SCHEDULE (Preliminary)
   Key dates working back from Substantial Completion:
   - NTP / Contract Start
   - Summer window open/close (if K-12)
   - Equipment order dates (flag items with >60-day lead time)
   - Submittal submission and approval windows
   - Pre-installation conferences (roofing, BAS, metal panels)
   - Rough-in complete dates by phase
   - Startup/testing start (per spec lead time before SC)
   - TAB period
   - Commissioning / CxA functional testing
   - Closeout conference (per spec lead time before SC)
   - Punch list (per spec duration)
   - Phase 1 SC and Phase 2 SC

5. EQUIPMENT SCHEDULE / KEY NUMBERS TABLE
   All mechanical equipment on the project:
   - Equipment tag, description, quantity
   - Model number / basis of design
   - Tonnage, CFM, GPM, HP, voltage, MOCP as applicable
   - Weight (lbs) - flag anything requiring crane
   - Crane assignment (crane size class needed for the pick)
   - Warranty terms
   - Vendor / rep source
   Existing equipment to remain vs. demo - clearly separated.

6. RFI LOG (Pre-Bid Flags)
   Any item that is: ambiguous, contradictory between documents, missing
   from the drawings, scope-split unclear between GC and {dba}, or
   requires clarification before pricing.
   Format: RFI number, spec/drawing reference, question, impacted scope item.

7. RISK FLAG LIST
   Items that could affect cost, schedule, or safety:
   - Long lead equipment (>60 days)
   - Occupied building / school-year work restrictions
   - ACM / hazmat present
   - Scope splits with GC that need tight coordination
   - Unit prices that could add cost if triggered
   - Crane staging conflicts (bus loop, pick radius, school access)
   - Liquidated damages exposure
   - Alternates that create scope dependency

8. GC / MECHANICAL COORDINATION NOTES
   Every interface point between {dba} scope and GC scope:
   - Concrete pads (GC pours, {dba} provides anchor bolt templates)
   - Structural steel (GC installs before {dba} sets equipment)
   - Equipment curbs (GC/roofing provides, {dba} sets equipment)
   - Electrical coordination (sub to {dba}, but GC coordinates conduit routing)
   - Crane access and staging ({dba} contracts, GC clears path)
   - Restroom/kitchen sequencing (GC finishes, {dba} rough-in, GC closes)

9. CONTRACT MILESTONE CHECKLIST
   Every spec-required action item with its deadline:
   - Site-specific safety plan
   - Background screening / badges (all workers before site access)
   - CPM schedule
   - Submittals (per log)
   - Pre-installation conferences
   - Closeout conference
   - O&M manual submission
   - As-built drawing submission
   - Training (hours required per system)
   - Warranty start confirmation
   - Spare parts delivery
   - Any state gas piping filings required by the spec or the local authority
     (if gas piping)
   - Certified payroll / Davis-Bacon (if prevailing wage applies)

10. SUBCONTRACTOR RFQ SUMMARY
    One-page formatted RFQ sheet per sub category with:
    - Scope description
    - Key spec sections
    - Quantities
    - Quote format required (Base Bid / each Alternate / Unit Prices separately)
    - Contact: {pm_contact}

===================================================
FORMAT AND STYLE RULES - ALWAYS APPLY
===================================================
- No em dashes or en dashes anywhere. Use hyphens or rewrite the sentence.
- Write in plain language. No spec jargon unless quoting a required term.
- Flag ambiguities inline with [RFI NEEDED] rather than silently skipping them.
- If a quantity is estimated or unclear, note it with [EST] or [VERIFY].
- Separate base bid from each alternate clearly.
- When equipment is Owner-Furnished / Contractor-Installed (OFCI), flag it.
- Note salvage rights items (some owners keep salvage on demolished equipment;
  check the spec).
- Note Davis-Bacon / prevailing wage applicability if public school project.
- Output each deliverable as a clearly labeled section.
- Do not summarize. Give every extractable detail.
  The PM will hand individual sections to subs for pricing.

===================================================
WHEN TO ASK VS. WHEN TO PROCEED
===================================================
- Begin immediately. Do not ask for permission to read files.
- If a deliverable cannot be completed due to missing information,
  produce what you can and flag what is missing with [MISSING - RFI].
- Do not ask the PM to confirm you should produce each deliverable.
  Produce all 10. The PM will say if a deliverable should be skipped."""


def build_system_prompt(p):
    extras = []
    if p["bonding_capacity"]:
        extras.append(f"Bonding capacity: {p['bonding_capacity']}.")
    if p["pm_software"]:
        extras.append(f"PM software: {p['pm_software']}.")
    company_extras = (" ".join(extras) + "\n") if extras else ""
    if p["subcontracted"]:
        sub_sentence = f"{join_words(p['subcontracted']).capitalize()} is subcontracted."
    else:
        sub_sentence = ""
    return SYSTEM_PROMPT_TEMPLATE.format(
        legal_name=p["legal_name"],
        dba=p["dba"],
        company_type=p["company_type"],
        location=p["location"],
        pm_name=p["pm_name"],
        pm_title=p["pm_title"],
        self_perform=join_words(p["self_perform"]),
        subcontracted_sentence=sub_sentence,
        market_focus=p["market_focus"],
        company_extras=company_extras,
        pm_contact=pm_contact_line(p),
    )


# -- File Readers --------------------------------------------------------------

def read_txt(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        return f"[ERROR reading {path}: {e}]"


def read_pdf(path):
    if not HAS_PDF:
        return f"[PDF SKIPPED - install PyPDF2: {path}]"
    try:
        text = []
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for i, page in enumerate(reader.pages):
                t = page.extract_text()
                if t:
                    text.append(f"--- PDF Page {i+1} ---\n{t}")
        return "\n".join(text) if text else f"[PDF appears to be scanned/image-only: {path}]"
    except Exception as e:
        return f"[ERROR reading PDF {path}: {e}]"


def read_docx(path):
    if not HAS_DOCX:
        return f"[DOCX SKIPPED - install python-docx: {path}]"
    try:
        doc = DocxDocument(path)
        paras = [p.text for p in doc.paragraphs if p.text.strip()]
        # Also grab tables
        table_text = []
        for table in doc.tables:
            for row in table.rows:
                row_data = [cell.text.strip() for cell in row.cells]
                table_text.append(" | ".join(row_data))
        return "\n".join(paras) + ("\n\nTABLES:\n" + "\n".join(table_text) if table_text else "")
    except Exception as e:
        return f"[ERROR reading DOCX {path}: {e}]"


def read_xlsx(path):
    if not HAS_XLSX:
        return f"[XLSX SKIPPED - install openpyxl: {path}]"
    try:
        wb = openpyxl.load_workbook(path, data_only=True)
        output = []
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            output.append(f"--- Sheet: {sheet_name} ---")
            for row in ws.iter_rows(values_only=True):
                row_data = [str(cell) if cell is not None else "" for cell in row]
                if any(cell.strip() for cell in row_data):
                    output.append(" | ".join(row_data))
        return "\n".join(output)
    except Exception as e:
        return f"[ERROR reading XLSX {path}: {e}]"


def read_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in (".txt", ".md", ".csv", ".rtf"):
        return read_txt(path)
    elif ext == ".pdf":
        return read_pdf(path)
    elif ext in (".docx", ".doc"):
        return read_docx(path)
    elif ext in (".xlsx", ".xls"):
        return read_xlsx(path)
    else:
        return None  # Skip unsupported types


# -- Folder Reader -------------------------------------------------------------

SKIP_DIRS = {"__pycache__", ".git", "node_modules", "BID_AGENT_OUTPUTS"}
SKIP_FILES = {
    "BID_AGENT_OUTPUT.txt", "bid_agent.py", "run_bid_agent.bat",
    "SETUP_FIRST_RUN.bat", "company_profile.json", "company_profile.example.json",
}
SKIP_PREFIXES = ("BID_AGENT_",)  # earlier agent outputs saved in the job folder
MAX_CHARS_PER_FILE = 80_000
MAX_TOTAL_CHARS = 180_000

def read_folder(folder_path):
    collected = []
    total_chars = 0

    for root, dirs, files in os.walk(folder_path):
        # Skip unwanted dirs
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for fname in sorted(files):
            if fname in SKIP_FILES or fname.startswith(SKIP_PREFIXES):
                continue

            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, folder_path)

            content = read_file(fpath)
            if content is None:
                continue  # Unsupported extension

            # Truncate if huge
            if len(content) > MAX_CHARS_PER_FILE:
                content = content[:MAX_CHARS_PER_FILE] + f"\n[TRUNCATED - file exceeded {MAX_CHARS_PER_FILE} chars]"

            block = f"\n{'='*60}\nFILE: {rel_path}\n{'='*60}\n{content}"
            collected.append(block)
            total_chars += len(block)

            if total_chars >= MAX_TOTAL_CHARS:
                collected.append(f"\n[TOTAL CONTENT LIMIT REACHED - {MAX_TOTAL_CHARS} chars. Some files omitted.]")
                break

        if total_chars >= MAX_TOTAL_CHARS:
            break

    return "\n".join(collected)


# -- API Call ------------------------------------------------------------------

def run_agent(folder_path, profile, project_name=None, model=DEFAULT_MODEL,
              max_tokens=DEFAULT_MAX_TOKENS, effort=DEFAULT_EFFORT):
    print("\nBID COORDINATION AGENT")
    print("======================")
    print(f"Company: {profile['dba']}")
    print(f"Folder : {folder_path}")
    if project_name:
        print(f"Project: {project_name}")
    print()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY is not set. Set it as an environment variable")
        print("(see SETUP_FIRST_RUN.bat or README.md) and run again.")
        sys.exit(1)

    # Read all files
    print("Reading files...")
    file_content = read_folder(folder_path)

    if not file_content.strip():
        print("ERROR: No readable files found in folder.")
        sys.exit(1)

    char_count = len(file_content)
    print(f"Read {char_count:,} characters from folder.")

    # Build user message
    header = f"PROJECT FOLDER: {project_name or os.path.basename(folder_path)}\n"
    header += f"FOLDER PATH: {folder_path}\n"
    header += f"RUN DATE: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    header += "All files extracted from the job folder are below. "
    header += "Produce all 10 deliverables.\n"
    user_message = header + file_content

    # Call API (streamed, so a long run does not hit an HTTP timeout)
    print(f"Sending to the Anthropic API, model {model} (a full run can take several minutes)...")
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

    request = dict(
        model=model,
        max_tokens=max_tokens,
        system=build_system_prompt(profile),
        messages=[{"role": "user", "content": user_message}],
    )
    if effort:
        request["output_config"] = {"effort": effort}

    try:
        with client.messages.stream(**request) as stream:
            response = stream.get_final_message()
    except anthropic.APIError as e:
        print(f"API Error: {e}")
        sys.exit(1)

    if response.stop_reason == "refusal":
        print("The model declined this request (stop_reason: refusal). No output saved.")
        sys.exit(1)

    output_text = "".join(
        block.text for block in response.content if getattr(block, "type", "") == "text"
    )
    if response.stop_reason == "max_tokens":
        output_text += "\n\n[OUTPUT CUT OFF - max_tokens reached. Re-run with a higher --max-tokens.]"
        print("WARNING: output hit the max_tokens limit and is incomplete.")

    # Save output
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    project_slug = (project_name or os.path.basename(folder_path)).replace(" ", "_").replace("/", "-")[:40]
    out_filename = f"BID_AGENT_{project_slug}_{timestamp}.txt"
    out_path = os.path.join(folder_path, out_filename)

    divider = "=" * 70
    full_output = f"""{divider}
BID COORDINATION AGENT - OUTPUT
{divider}
Company : {profile['dba']}
Project : {project_name or os.path.basename(folder_path)}
Folder  : {folder_path}
Run Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
Model   : {model}
{divider}

{output_text}

{divider}
END OF OUTPUT
Generated by the {profile['dba']} Bid Agent
{pm_contact_line(profile)}
{divider}
"""

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full_output)

    print("\nDONE.")
    print(f"Output saved to: {out_path}")
    print("Open that file and each deliverable will be labeled 1-10.")
    return out_path


# -- Entry Point ---------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bid Coordination Agent")
    parser.add_argument(
        "folder",
        help='Path to the job folder (e.g. "C:\\Jobs\\Sample-Elementary")',
    )
    parser.add_argument(
        "--project",
        default=None,
        help='Project name (e.g. "Sample Elementary School HVAC Replacement")',
    )
    parser.add_argument(
        "--profile",
        default=None,
        help="Company profile JSON (default: BID_AGENT_PROFILE env var, else "
             "company_profile.json beside this script, else company_profile.example.json)",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("BID_AGENT_MODEL", DEFAULT_MODEL),
        help=f"Model id (default: BID_AGENT_MODEL env var or {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=DEFAULT_MAX_TOKENS,
        help=f"Output token cap (default: {DEFAULT_MAX_TOKENS})",
    )
    parser.add_argument(
        "--effort",
        default=DEFAULT_EFFORT,
        choices=["low", "medium", "high", "xhigh", "max", "none"],
        help=f"Effort level sent to the API, or 'none' to omit it (default: {DEFAULT_EFFORT})",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.folder):
        print(f"ERROR: Folder not found: {args.folder}")
        sys.exit(1)

    profile = load_profile(args.profile or default_profile_path())
    run_agent(
        args.folder,
        profile,
        project_name=args.project,
        model=args.model,
        max_tokens=args.max_tokens,
        effort=None if args.effort == "none" else args.effort,
    )
