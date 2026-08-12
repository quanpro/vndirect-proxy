# -*- coding: utf-8 -*-
"""Build the RACI and register workbook as .xlsx."""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

import content as C

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "Marico_MPS_MRP_RACI_and_Registers_v1.0.xlsx")

NAVY, BLUE, LIGHT, LIGHTER = C.NAVY, C.BLUE, C.LIGHT, C.LIGHTER
SLATE, GREY, AMBER, RED, GREEN = C.SLATE, C.GREY, C.AMBER, C.RED, C.GREEN

HDR_FILL = PatternFill("solid", fgColor=NAVY)
HDR_FONT = Font(name="Arial", size=9.5, bold=True, color="FFFFFF")
BODY_FONT = Font(name="Arial", size=9.5, color=SLATE)
BOLD_FONT = Font(name="Arial", size=9.5, bold=True, color=SLATE)
ZEBRA = PatternFill("solid", fgColor=LIGHTER)
THIN = Side(style="thin", color="D2DCE8")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
TOP_WRAP = Alignment(vertical="top", wrap_text=True)
CENTER = Alignment(vertical="center", horizontal="center", wrap_text=True)

wb = Workbook()
wb.remove(wb.active)


def sheet(name, headers, rows, widths, tab_color=BLUE, freeze="A2",
          centre_cols=(), height=None, title=None, note=None):
    ws = wb.create_sheet(name[:31])
    ws.sheet_properties.tabColor = tab_color
    r0 = 1
    if title:
        ws.cell(1, 1, title).font = Font(name="Arial", size=13, bold=True, color=NAVY)
        if note:
            ws.cell(2, 1, note).font = Font(name="Arial", size=9, italic=True, color=GREY)
            r0 = 4
        else:
            r0 = 3
    for j, h in enumerate(headers, start=1):
        c = ws.cell(r0, j, h)
        c.fill = HDR_FILL
        c.font = HDR_FONT
        c.alignment = Alignment(vertical="center", wrap_text=True)
        c.border = BORDER
    ws.row_dimensions[r0].height = 30
    for i, row in enumerate(rows):
        rr = r0 + 1 + i
        for j, val in enumerate(row, start=1):
            c = ws.cell(rr, j, val)
            c.font = BODY_FONT
            c.alignment = CENTER if j in centre_cols else TOP_WRAP
            c.border = BORDER
            if i % 2 == 1:
                c.fill = ZEBRA
        if height:
            ws.row_dimensions[rr].height = height
    for j, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(j)].width = w
    ref = f"A{r0}:{get_column_letter(len(headers))}{r0 + len(rows)}"
    ws.auto_filter.ref = ref
    ws.freeze_panes = ws.cell(r0 + 1, 1)
    return ws


# ---------------------------------------------------------------------------
# 1. Read me
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Read me")
ws.sheet_properties.tabColor = NAVY
ws.column_dimensions["A"].width = 22
ws.column_dimensions["B"].width = 118
rows = [
    ("", ""),
    ("Document", C.DOC["company"] + " - " + C.DOC["title"]),
    ("Workbook", "RACI matrix, interface register, requirement register and supporting registers"),
    ("Companion to", C.DOC["doc_id"] + " (Business Requirements Brief v1.0, Word) and the "
                     "process infographic pack (PowerPoint)"),
    ("Version", C.DOC["version"] + " - " + C.DOC["status"]),
    ("Date", C.DOC["date"]),
    ("Owner", C.DOC["owner"]),
    ("Audience", C.DOC["audience"]),
    ("Responds to", C.DOC["responds_to"]),
    ("", ""),
    ("Architecture", "EZ-Commerce is the planning brain: all quantitative calculation happens there. "
                     "SAP S/4HANA is the execution system of record: it receives an already-net requirement, "
                     "creates the purchase requisition and manages the purchase order."),
    ("Scope", "Single plant. Single-level BOM, finished goods to raw and packing materials. "
              "300-800 finished goods, 1,500-4,000 raw and packing materials. 12-month horizon, "
              "monthly buckets, weekly for the current month plus three (extendable to six)."),
    ("", ""),
    ("Tabs", ""),
    ("RACI", "Ownership of all 29 process steps across eight roles. Exactly one accountable role per step."),
    ("Interfaces", "Ten interfaces between EZ-Commerce and SAP, with mechanism, frequency, volume and error handling."),
    ("Requirements", "63 numbered, traceable requirements with MoSCoW priority. This is the contractual statement of requirement."),
    ("NFRs", "Fourteen non-functional requirements sized against the confirmed portfolio."),
    ("Master data", "Which system owns which object, who maintains it, and how it synchronises."),
    ("Controls", "Eight controls that detect divergence between the planning system and SAP."),
    ("Risks", "Ten risks with likelihood, impact and mitigation."),
    ("Gap analysis", "Fifteen gaps against the vendor scope document, each with the correction required."),
    ("Decisions", "Five design decisions: four closed, one open for the design workshop."),
    ("Open questions", "Ten questions to close in the design workshop, with owner and what each blocks."),
    ("UAT", "Sixteen acceptance scenarios. UAT-12 is the direct test of the double-netting defect."),
    ("Roadmap", "Six phases from readiness assessment through to network integration."),
]
ws.cell(1, 1, C.DOC["company"] + "  |  Integrated MPS & MRP Planning System").font = Font(
    name="Arial", size=15, bold=True, color=NAVY)
for i, (k, v) in enumerate(rows, start=2):
    a = ws.cell(i, 1, k)
    a.font = Font(name="Arial", size=9.5, bold=True, color=BLUE)
    a.alignment = Alignment(vertical="top")
    b = ws.cell(i, 2, v)
    b.font = BODY_FONT
    b.alignment = TOP_WRAP
    if v and len(v) > 110:
        ws.row_dimensions[i].height = 30
ws.cell(15, 1).font = Font(name="Arial", size=11, bold=True, color=NAVY)

# ---------------------------------------------------------------------------
# 2. RACI
# ---------------------------------------------------------------------------
raci_rows = []
stage_name = {s["id"]: s["name"] for s in C.STAGES}
for step_id, stage, name, assign in C.RACI:
    raci_rows.append([step_id, stage, stage_name[stage], name] +
                     [assign.get(rc, "") for rc in C.ROLE_CODES])
ws = sheet("RACI", ["Step", "Stage", "Stage name", "Activity"] + C.ROLE_CODES,
           raci_rows, [7, 7, 30, 62] + [7] * 8,
           centre_cols=tuple(range(5, 13)) + (1, 2), height=28,
           title="RACI matrix - process step ownership",
           note="R responsible  |  A accountable  |  C consulted  |  I informed  |  A/R both. "
                "Exactly one accountable role per step. Role codes are defined on the Roles block below the matrix.")
for r in range(5, 5 + len(raci_rows)):
    for j in range(5, 13):
        c = ws.cell(r, j)
        if isinstance(c.value, str) and c.value.startswith("A"):
            c.font = Font(name="Arial", size=9.5, bold=True, color=RED)
        elif c.value == "R":
            c.font = Font(name="Arial", size=9.5, bold=True, color=BLUE)
        elif c.value == "C":
            c.font = Font(name="Arial", size=9.5, color=SLATE)
        else:
            c.font = Font(name="Arial", size=9.5, color=GREY)
r = 5 + len(raci_rows) + 2
ws.cell(r, 1, "Role definitions").font = Font(name="Arial", size=11, bold=True, color=NAVY)
for i, (code, name, desc) in enumerate(C.ROLES, start=1):
    ws.cell(r + i, 1, code).font = Font(name="Arial", size=9.5, bold=True, color=BLUE)
    ws.cell(r + i, 3, name).font = BOLD_FONT
    ws.cell(r + i, 4, desc).font = BODY_FONT
    ws.cell(r + i, 4).alignment = TOP_WRAP
    ws.row_dimensions[r + i].height = 28

# ---------------------------------------------------------------------------
# 3. Interfaces
# ---------------------------------------------------------------------------
sheet("Interfaces",
      ["Ref", "Interface", "Direction", "In/Out", "Object", "Mechanism",
       "Frequency", "Volume", "Error handling"],
      [list(i) for i in C.INTERFACES],
      [7, 24, 24, 9, 26, 40, 20, 26, 40], centre_cols=(1, 4), height=48,
      title="Interface register",
      note="Ten interfaces between EZ-Commerce and SAP S/4HANA. IF-09 is not specified until Decision D-02 is closed.")

# ---------------------------------------------------------------------------
# 4. Requirements
# ---------------------------------------------------------------------------
ws = sheet("Requirements",
           ["Ref", "Group", "Requirement", "Priority", "Phase", "Status", "Vendor estimate", "Comment"],
           [[r[0], r[1], r[2], r[3], "", "Issued", "", ""] for r in C.REQUIREMENTS],
           [9, 14, 92, 10, 10, 12, 15, 30], centre_cols=(1, 2, 4, 5, 6), height=30,
           title="Requirement register",
           note="63 numbered requirements. This register, not the narrative, is the contractual statement of requirement. "
                "Phase, Status, Vendor estimate and Comment are left blank for the delivery team to complete.")
for r in range(5, 5 + len(C.REQUIREMENTS)):
    c = ws.cell(r, 4)
    if c.value == "Must":
        c.font = Font(name="Arial", size=9.5, bold=True, color=RED)
    elif c.value == "Should":
        c.font = Font(name="Arial", size=9.5, color=AMBER)
    else:
        c.font = Font(name="Arial", size=9.5, color=GREY)

# ---------------------------------------------------------------------------
# 5. NFRs
# ---------------------------------------------------------------------------
sheet("NFRs", ["Ref", "Area", "Requirement"], [list(n) for n in C.NFRS],
      [9, 30, 100], centre_cols=(1,), height=32,
      title="Non-functional requirements",
      note="Sized against a single plant, 300-800 finished goods and 1,500-4,000 raw and packing materials.")

# ---------------------------------------------------------------------------
# 6. Master data ownership
# ---------------------------------------------------------------------------
MASTER_DATA = [
    ["Material master and plant data", "SAP", "Master Data Steward", "Nightly (IF-02)"],
    ["Bill of material", "SAP", "Master Data Steward / R&D", "Nightly (IF-03)"],
    ["Routing and work centre", "SAP", "Master Data Steward / Operations", "Nightly (IF-04)"],
    ["Purchasing info record, source list", "SAP", "Procurement / Master Data Steward", "Nightly (IF-07)"],
    ["Inventory, batch, expiry, quality status", "SAP", "Plant / Warehouse", "Daily and on demand (IF-05)"],
    ["Open purchase orders and requisitions", "SAP", "Procurement", "Daily and on demand (IF-06)"],
    ["Stock norms and coverage policy", "EZ-Commerce", "MPS and Material Planner", "Not held in SAP; SAP safety stock = 0"],
    ["Lot-sizing policy and parameters", "EZ-Commerce", "MPS and Material Planner", "Not held in SAP; SAP lot size = EX"],
    ["Service priority weighting", "EZ-Commerce", "S&OP Manager", "Not applicable to SAP"],
    ["Changeover matrix", "EZ-Commerce", "Plant Operations", "Not applicable to SAP"],
    ["Campaign and family rules", "EZ-Commerce", "MPS Planner / Operations", "Not applicable to SAP"],
    ["Capacity calendar, shifts, efficiency", "EZ-Commerce", "Plant Operations", "Seeded from SAP routing, overlaid locally"],
    ["Planning calendar and time fences", "EZ-Commerce", "MPS Planner", "Not applicable to SAP"],
    ["Weekly demand profile for disaggregation", "EZ-Commerce", "Demand Planner", "Not applicable to SAP"],
]
ws = sheet("Master data", ["Object", "System of record", "Maintained by", "Sync into EZ-Commerce"],
           MASTER_DATA, [42, 18, 34, 44], centre_cols=(2,), height=22,
           title="Master data and parameter ownership  (Decision D-03)",
           note="One owner per object. SAP owns engineering and logistics master data. EZ-Commerce owns every planning parameter.")
for r in range(5, 5 + len(MASTER_DATA)):
    c = ws.cell(r, 2)
    c.font = Font(name="Arial", size=9.5, bold=True,
                  color=(BLUE if c.value == "EZ-Commerce" else "475569"))

# ---------------------------------------------------------------------------
# 7. Controls
# ---------------------------------------------------------------------------
sheet("Controls", ["Ref", "Control", "Test", "Owner", "Frequency"],
      [list(c) for c in C.CONTROLS], [8, 26, 78, 24, 14],
      centre_cols=(1, 5), height=32,
      title="Control register",
      note="These controls exist because the architecture deliberately splits calculation from execution. "
           "Divergence must be detected systematically, not discovered on the production line.")

# ---------------------------------------------------------------------------
# 8. Risks
# ---------------------------------------------------------------------------
ws = sheet("Risks", ["Ref", "Risk", "Likelihood", "Impact", "Description", "Mitigation"],
           [list(r) for r in C.RISKS], [8, 32, 12, 10, 62, 62],
           centre_cols=(1, 3, 4), height=48, title="Risk register")
for r in range(4, 4 + len(C.RISKS) + 1):
    for j in (3, 4):
        c = ws.cell(r, j)
        if c.value == "High":
            c.font = Font(name="Arial", size=9.5, bold=True, color=RED)
        elif c.value == "Medium":
            c.font = Font(name="Arial", size=9.5, color=AMBER)
        elif c.value == "Low":
            c.font = Font(name="Arial", size=9.5, color=GREEN)

# ---------------------------------------------------------------------------
# 9. Gap analysis
# ---------------------------------------------------------------------------
sheet("Gap analysis",
      ["Ref", "Where in vendor doc", "What the document says", "Why it is a problem",
       "Correction required", "Requirement"],
      [list(g) for g in C.GAPS], [8, 22, 52, 56, 56, 20],
      centre_cols=(1,), height=56, tab_color=AMBER,
      title="Gap analysis against the vendor scope document v1.0 (SCOPE-MARICO-EZ-SAP-v1.0)",
      note="Four gaps change cost and timeline materially: G-02, G-03, G-04 and G-08. Re-baseline scope and commercials before build.")

# ---------------------------------------------------------------------------
# 10. Decisions
# ---------------------------------------------------------------------------
dec_rows = []
for d in C.DECISIONS:
    dec_rows.append([d["id"], d["title"], d["status"], d["problem"], d["decision"],
                     "\n".join("- " + x for x in d["implementation"]) if d["implementation"] else "",
                     d["consequence"]])
ws = sheet("Decisions", ["Ref", "Decision", "Status", "Problem", "Decision taken",
                         "Implementation requirements", "Consequence"],
           dec_rows, [8, 34, 22, 66, 66, 60, 60], centre_cols=(1,), height=110,
           title="Design decision register")
for r in range(4, 4 + len(dec_rows) + 1):
    c = ws.cell(r, 3)
    if isinstance(c.value, str) and c.value.startswith("OPEN"):
        c.font = Font(name="Arial", size=9.5, bold=True, color=AMBER)
    elif isinstance(c.value, str) and c.value.startswith("DECIDED"):
        c.font = Font(name="Arial", size=9.5, bold=True, color=GREEN)

# ---------------------------------------------------------------------------
# 11. Open questions
# ---------------------------------------------------------------------------
sheet("Open questions", ["Ref", "Question", "Owner", "What it blocks", "Target date", "Status"],
      [[q[0], q[1], q[2], q[3], "", "Open"] for q in C.OPEN_QUESTIONS],
      [8, 76, 30, 34, 14, 12], centre_cols=(1, 5, 6), height=30, tab_color=AMBER,
      title="Open questions for the design workshop")

# ---------------------------------------------------------------------------
# 12. UAT
# ---------------------------------------------------------------------------
sheet("UAT", ["Ref", "Scenario", "Test", "Expected result", "Result", "Tester", "Date"],
      [[u[0], u[1], u[2], u[3], "", "", ""] for u in C.UAT],
      [9, 30, 66, 66, 12, 16, 12], centre_cols=(1, 5), height=40, tab_color=GREEN,
      title="Acceptance test scenarios",
      note="UAT-12 must pass before go-live: it is the direct test of the double-netting defect described in Decision D-01.")

# ---------------------------------------------------------------------------
# 13. Roadmap
# ---------------------------------------------------------------------------
road_rows = []
for name, title, dur, items in C.ROADMAP:
    for k, item in enumerate(items):
        road_rows.append([name if k == 0 else "", title if k == 0 else "",
                          dur if k == 0 else "", item])
sheet("Roadmap", ["Phase", "Theme", "Indicative duration", "Deliverable"],
      road_rows, [12, 34, 20, 92], centre_cols=(1, 3), height=18,
      title="Implementation roadmap")

wb.save(os.path.abspath(OUT))
print("Wrote", os.path.abspath(OUT), "-", len(wb.sheetnames), "tabs:", ", ".join(wb.sheetnames))
