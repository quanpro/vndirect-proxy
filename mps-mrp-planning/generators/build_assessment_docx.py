# -*- coding: utf-8 -*-
"""Build Annex D - assessment of the MPS Vietnam proposal - as a .docx."""
import os

from docxkit import *  # noqa: F401,F403
import content as C

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "Marico_MPS_Vietnam_Proposal_Assessment_v1.0.docx")

A = C.ASSESS

D = Doc()
d = D.d

# ---- COVER ---------------------------------------------------------------
D.d.add_paragraph()
D.p(C.DOC["company"].upper(), size=11, bold=True, color=C.BLUE, space_after=2)
p = D.d.add_paragraph()
r = p.add_run("Annex D")
r.bold = True
r.font.size = Pt(13)
r.font.name = "Arial"
r.font.color.rgb = rgb(C.GREY)
p.paragraph_format.space_after = Pt(2)
p = D.d.add_paragraph()
r = p.add_run(A["title"])
r.bold = True
r.font.size = Pt(26)
r.font.name = "Arial"
r.font.color.rgb = rgb(C.NAVY)
p.paragraph_format.space_after = Pt(2)
p = D.d.add_paragraph()
r = p.add_run(A["subtitle"])
r.font.size = Pt(14)
r.font.name = "Arial"
r.font.color.rgb = rgb(C.BLUE)
p.paragraph_format.space_after = Pt(14)
para_border(p, C.CYAN, 18, ("bottom",))

D.d.add_paragraph()
D.callout("Verdict", A["verdict"], "FEF3E2", C.AMBER)

D.d.add_paragraph()
D.table(
    ["Field", "Detail"],
    [
        ["Document ID", A["doc_id"]],
        ["Annex to", C.DOC["doc_id"] + "  (Business Process and Functional Requirements Brief v1.0)"],
        ["Document assessed", A["assessed"] + ",  " + A["assessed_date"] + ",  " + A["pages"]],
        ["Assessed against", "The seven-stage target process in section 8 of the main brief, and the "
                             "63-requirement register in section 15."],
        ["Version", "1.0  (" + C.DOC["status"] + ")"],
        ["Date", "25 November 2026"],
        ["Business owner", C.DOC["owner"]],
        ["Audience", C.DOC["audience"]],
        ["Status", "Issued for review. Extends the consolidated gap register with G-16 to G-24 and "
                   "adds open decisions D-06 to D-08."],
    ],
    [22, 78], size=9)

# ==========================================================================
D.pagebreak()
D.h1("D.1  Summary")

D.p("The MPS Vietnam proposal has been assessed against the target process and the requirement "
    "register issued in the main brief. The conclusion is narrow and specific: the proposal is a "
    "competent finished goods inventory coverage planning tool, and it is a reasonable first phase. "
    "It is not an MPS and MRP system, and accepting it as one would leave the larger half of the "
    "business requirement unbuilt, unfunded and unowned.")

D.h2("D.1.1  Where it lands against the target process")
D.p("Of the seven process stages in the target design, the proposal delivers one well, delivers "
    "part of a second, and does not address the remaining five.")
D.table(
    ["Ref", "Target process stage", "What the proposal provides", "Verdict"],
    [[m[0], m[1], m[2], m[3]] for m in C.ASSESS_MAPPING],
    [7, 23, 56, 14], size=8.5, aligns=[CEN, None, None, CEN])

D.h2("D.1.2  Requirement coverage")
total = sum(r[1] for r in C.ASSESS_COVERAGE)
full = sum(r[2] for r in C.ASSESS_COVERAGE)
part = sum(r[3] for r in C.ASSESS_COVERAGE)
none = sum(r[4] for r in C.ASSESS_COVERAGE)
D.p(f"Against the {total} numbered requirements in section 15 of the main brief, {full} are fully "
    f"met and {part} are partially met. {none} are not addressed. Four of the eight requirement "
    f"groups score zero.")
rows = [[r[0], r[1], r[2], r[3], r[4], r[5]] for r in C.ASSESS_COVERAGE]
rows.append(["Total", total, full, part, none, ""])
D.table(["Group", "Reqs", "Met", "Partial", "Not met", "Comment"], rows,
        [12, 7, 7, 8, 8, 58], size=8.5,
        aligns=[None, CEN, CEN, CEN, CEN, None])

D.h2("D.1.3  The three gaps that decide the programme")
D.table(
    ["Ref", "Gap", "Consequence"],
    [
        ["G-16", "No constrained optimization",
         "The capability the business specifically asked for in the 3 to 6 month window does not "
         "exist in either proposal. The plan produced is not guaranteed to be executable."],
        ["G-17", "No material requirements planning",
         "No BOM explosion, no component netting. The second half of the requirement is absent."],
        ["G-18", "Nothing is written back to SAP",
         "The plan cannot drive procurement. The loop from planning decision to purchase order "
         "stays manual."],
    ],
    [7, 25, 68], size=9)

# ==========================================================================
D.pagebreak()
D.h1("D.2  What the proposal gets right")
D.p("The planning instinct in this document is sound, and in several respects it is closer to what "
    "a planner needs than the vendor scope document assessed in Annex A. These strengths should be "
    "retained, not rebuilt.")
for title, body in C.ASSESS_STRENGTHS:
    D.h3(title)
    D.p(body, size=9.5)

D.callout(
    "The planner-facing design is the strongest part of the proposal",
    "Week Cover measured against Policy Week with red, amber and green banding, batch-level "
    "rounding shown transparently, in-transit and quality inspection stock separated out, and a "
    "simulation control to test an intervention before committing. A planner could work from this "
    "screen. That is not true of the vendor scope document, which has no process map at all. The "
    "problem with this proposal is scope, not craft.",
    "ECFDF3", C.GREEN)

# ==========================================================================
D.section(landscape=True)
D.h1("D.3  Gap register extension")
D.p("These entries extend the consolidated gap register in Annex A, which covers the vendor scope "
    "document. Entries G-01 to G-15 relate to that document; G-16 to G-24 below relate to the MPS "
    "Vietnam proposal. Together they form one list covering both.")
D.table(
    ["Ref", "Gap", "What the proposal does", "Why it matters", "Requirement affected"],
    [[g[0], g[1], g[2], g[3], g[4]] for g in C.ASSESS_GAPS],
    [4, 15, 32, 34, 15], size=8)

# ==========================================================================
D.section(landscape=False)
D.h1("D.4  Specification defects")
D.p("These are defects in the document itself rather than gaps in scope. They are individually "
    "small, but SD-01 concerns the only output the tool exists to produce and must be closed before "
    "build begins.")
D.table(
    ["Ref", "Where", "Defect", "Correction"],
    [[s[0], s[1], s[2], s[3]] for s in C.ASSESS_DEFECTS],
    [8, 16, 41, 35], size=8.5)

D.callout(
    "SD-01 in plain terms",
    "Section 5.1 defines Policy Week, Closing Stock and Total Demand. It does not define Production "
    "Planned Quantity. The Closing Stock formula then uses Production Planned as one of its inputs, "
    "so the specification asks for a number to be calculated from a number that is never derived. "
    "The intent is described in prose in section 1.1 as the inventory gap required to reach the "
    "coverage target, but prose is not a specification. Two developers would build two different "
    "answers from it.",
    "FDF2F4", C.RED)

# ==========================================================================
D.pagebreak()
D.h1("D.5  Reconciliation with the vendor scope document")
D.p("Two proposals are now live, and they do not fit together. Each covers roughly half of what the "
    "other omits, they overlap on the half that matters most, and between them the remaining half "
    "of the requirement has no owner.")

D.table(
    ["", "Vendor scope document v1.0", "MPS Vietnam proposal"],
    [
        ["Master scheduling logic", "Absent. One line, delegated to SAP.", "Present. Coverage-driven, weekly buckets."],
        ["Constrained optimization", "Absent. Assumed to be SAP, which cannot do it.", "Absent."],
        ["BOM explosion and MRP", "Delegated to SAP MRP.", "Absent."],
        ["Write-back to SAP", "Present. PIR, MRP trigger, purchase requisition.", "Absent. One-way flow only."],
        ["Approval gates", "Absent.", "Absent."],
        ["Planner front end", "Portal with upload and results dashboard.", "Planning application with time-phased grid."],
        ["Where MPS runs", "Inside SAP.", "In the SQL calculation engine on the data warehouse."],
        ["Horizon", "Not defined. Left open as a business question.", "5 months, stated inconsistently as 28 weeks."],
    ],
    [22, 39, 39], size=8.5, bold_col0=True)

D.callout(
    "If both were built as written",
    "The business would have two master scheduling engines in two systems, two planner front ends "
    "for one process, no constrained optimization anywhere, no material requirements planning "
    "anywhere, and the double-netting defect described in Decision D-01, because the MPS Vietnam "
    "model nets finished goods against stock and open orders while the vendor scope asks SAP to net "
    "the same demand a second time.",
    "FEF3E2", C.AMBER)

D.h2("D.5.1  Decisions this forces")
D.table(
    ["Ref", "Decision required", "Why it is open", "Owner", "Consequence of delay"],
    [[x[0], x[1], x[2], x[3], x[4]] for x in C.ASSESS_DECISIONS],
    [7, 24, 31, 16, 22], size=8.5)
D.p("These extend the decision register in section 12 of the main brief, which already carries D-01 "
    "to D-05. D-06 to D-08 should be closed in the same design workshop as D-02.", size=9, italic=True)

# ==========================================================================
D.pagebreak()
D.h1("D.6  Recommendation")

D.h2("D.6.1  Accept it, but reframe it")
D.p("The recommendation is to accept the MPS Vietnam proposal as Phase 1a of the target roadmap, "
    "not as the MPS and MRP solution. It maps closely onto Phase 1a in section 18 of the main "
    "brief: demand intake plus an unconstrained master production schedule. That is a sensible "
    "first delivery which gives planners something useful on its own, and the coverage logic and "
    "interface design are worth keeping.")
D.p("What matters is the framing. If this is signed off as the MPS and MRP tool, the programme will "
    "record the requirement as delivered while five of seven process stages remain unbuilt. The "
    "cost conversation about those stages needs to happen now, not in six months when the "
    "application goes live and the planners ask where the material plan is.")

D.h2("D.6.2  Required before it is even a complete Stage 2")
D.p("Six additions are needed before the proposal fully delivers the unconstrained MPS stage it is "
    "closest to. None of these is a large piece of work; all of them are cheaper now than later.")
D.table(
    ["Ref", "Addition", "Detail", "Requirement"],
    [[a[0], a[1], a[2], a[3]] for a in C.ASSESS_ADDITIONS],
    [8, 21, 53, 18], size=8.5)

D.h2("D.6.3  Treat the remaining stages as separate, unfunded scope")
D.p("Stages S3, S5, S6 and S7 are not covered by either proposal. They should be scoped, estimated "
    "and funded explicitly rather than assumed into an existing statement of work:")
D.bullet("the constrained optimizer, specified in section 9.4 of the main brief;", bold_lead="S3  ")
D.bullet("BOM explosion and component netting, specified in section 9.5;", bold_lead="S5  ")
D.bullet("the material planner confirmation gate;", bold_lead="S6  ")
D.bullet("release to SAP as Planned Independent Requirements, with the Decision D-01 guardrail and "
         "the reconciliation controls.", bold_lead="S7  ")

D.h2("D.6.4  Architectural caution")
D.callout(
    "An analytics stack is the right place for the calculation and the wrong place for the state",
    "A SQL engine over a data warehouse is a good fit for computing a plan. It is not a natural fit "
    "for the things that make a plan authoritative: an immutable approved version, a planner "
    "approval that gates downstream processing, an override audit trail, and a transactional "
    "write-back to SAP that must be idempotent and replayable. Those need an application layer with "
    "transactional integrity sitting alongside the warehouse. This should be settled in the design "
    "workshop, before the architecture is frozen, because retrofitting plan state onto a reporting "
    "stack is expensive and is usually discovered late.",
    C.LIGHT, C.BLUE)

D.h2("D.6.5  Immediate next steps")
D.table(
    ["#", "Action", "Owner"],
    [
        ["1", "Close decisions D-06, D-07 and D-08 in the design workshop, alongside D-02.",
         "Supply Chain Planning and IT"],
        ["2", "Reframe the MPS Vietnam proposal as Phase 1a in the programme plan, and record "
              "explicitly that stages S3, S5, S6 and S7 are not covered by it.",
         "Programme management"],
        ["3", "Issue defects SD-01 to SD-05 to the authors for correction, with SD-01 as a "
              "precondition to build.", "Supply Chain Planning"],
        ["4", "Add requirements RA-01 to RA-06 to the Phase 1a scope before the statement of work "
              "is signed.", "Supply Chain Planning and IT"],
        ["5", "Scope, estimate and fund the optimizer, MRP and SAP write-back as separate "
              "workstreams.", "IT and Procurement"],
        ["6", "Confirm which integration workstream will deliver BOM, routing, capacity, purchasing "
              "info record, source list and open purchase order extraction, none of which is in the "
              "current inbound scope.", "IT Integration"],
    ],
    [5, 72, 23], size=9)

D.d.add_paragraph()
D.p("End of Annex D", size=9, italic=True, color=C.GREY, align=CEN)

d.save(os.path.abspath(OUT))
print("Wrote", os.path.abspath(OUT))
