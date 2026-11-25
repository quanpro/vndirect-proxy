# -*- coding: utf-8 -*-
"""Build Annex D - assessment of the MPS Vietnam proposal - as a .docx.

Scoped to master production scheduling only. MRP is not assessed.
"""
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
D.callout("Scope of this assessment", A["scope_note"], C.LIGHT, C.BLUE)
D.callout("Verdict", A["verdict"], "FEF3E2", C.AMBER)

D.d.add_paragraph()
D.table(
    ["Field", "Detail"],
    [
        ["Document ID", A["doc_id"]],
        ["Annex to", C.DOC["doc_id"] + "  (Business Process and Functional Requirements Brief v1.0)"],
        ["Document assessed", A["assessed"] + ",  " + A["assessed_date"] + ",  " + A["pages"]],
        ["Assessed against", "Stages S1 to S4 of the target process in section 8 of the main brief, "
                             "and the 44 master production scheduling requirements in section 15."],
        ["Not assessed", "Stages S5 to S7: material requirements planning, the material planner "
                          "confirmation gate, and release of requirements to SAP. The proposal does "
                          "not claim these and they are not treated as gaps."],
        ["Version", "1.0  (" + C.DOC["status"] + ")"],
        ["Date", "25 November 2026"],
        ["Business owner", C.DOC["owner"]],
        ["Audience", C.DOC["audience"]],
        ["Status", "Issued for review. Extends the consolidated gap register with G-16 to G-24 and "
                   "adds open decisions D-06 and D-07."],
    ],
    [22, 78], size=9)

# ==========================================================================
D.pagebreak()
D.h1("D.1  What is and is not being assessed")

D.p("The MPS Vietnam proposal is a master production scheduling proposal. It does not claim "
    "material requirements planning, BOM explosion, component netting or release of requirements "
    "to SAP, and it is not criticised here for omitting them. Judging it against the full "
    "MPS-and-MRP requirement would be unfair and would also obscure the more important question.")
D.p("That question is narrower: as a master production schedule, does it do the job? A master "
    "production schedule is a commitment about what the factory will make, in what quantity, in "
    "which week, that the factory can actually execute and that a named person has approved. "
    "Measured against that definition rather than against MRP, the proposal has two specific "
    "shortfalls, and they are the subject of this annex.")

D.h2("D.1.1  Requirements in scope")
D.p(C.ASSESS_EXCLUDED)

D.h2("D.1.2  Process stages in scope")
D.table(
    ["Stage", "Target process stage", "In scope here?"],
    [
        ["S1", "Demand intake and forecast validation", "Yes"],
        ["S2", "Unconstrained MPS heuristic", "Yes"],
        ["S3", "Constrained MPS optimization", "Yes - this is MPS, not MRP"],
        ["S4", "MPS review and approval gate", "Yes"],
        ["S5", "MRP explosion and netting", "No - not assessed"],
        ["S6", "MRP confirmation gate", "No - not assessed"],
        ["S7", "Release to SAP, purchase requisition and purchase order", "No - not assessed"],
    ],
    [8, 52, 40], size=9, aligns=[CEN, None, None])
D.p("Stage S3 deserves a word, because it is the stage most often mistaken for someone else's "
    "problem. Resolving a production plan against finite line capacity, changeover and campaign "
    "rules is master production scheduling. It is not material requirements planning, and it is "
    "not something SAP will do later: standard SAP MPS plans at infinite capacity too. If it is "
    "not built here, it is not built anywhere.", size=9, italic=True)

# ==========================================================================
D.pagebreak()
D.h1("D.2  Summary")

D.h2("D.2.1  Where it lands against the four MPS stages")
D.table(
    ["Ref", "Target process stage", "What the proposal provides", "Verdict"],
    [[m[0], m[1], m[2], m[3]] for m in C.ASSESS_MAPPING],
    [7, 23, 56, 14], size=8.5, aligns=[CEN, None, None, CEN])

D.h2("D.2.2  Requirement coverage")
total = sum(r[1] for r in C.ASSESS_COVERAGE)
full = sum(r[2] for r in C.ASSESS_COVERAGE)
part = sum(r[3] for r in C.ASSESS_COVERAGE)
none = sum(r[4] for r in C.ASSESS_COVERAGE)
D.p(f"Against the {total} master production scheduling requirements, {full} are fully met and "
    f"{part} are partially met. {none} are not addressed. Three of the seven in-scope requirement "
    f"groups score zero.")
rows = [[r[0], r[1], r[2], r[3], r[4], r[5]] for r in C.ASSESS_COVERAGE]
rows.append(["Total", total, full, part, none, ""])
D.table(["Group", "In scope", "Met", "Partial", "Not met", "Comment"], rows,
        [16, 8, 7, 8, 8, 53], size=8.5,
        aligns=[None, CEN, CEN, CEN, CEN, None])

D.h2("D.2.3  The two gaps that decide it")
D.p("Setting aside everything that can be added incrementally, two gaps determine whether this is "
    "a master production schedule or a very good inventory coverage report.")
D.table(
    ["Ref", "Gap", "Why it is decisive"],
    [
        ["G-16", "No constrained optimization",
         "The plan is not guaranteed to be executable. The model can propose a batch in a week the "
         "line cannot run, and it has no way to tell the planner which constraint is binding. This "
         "is the larger half of master production scheduling and it cannot be delegated to SAP."],
        ["G-17", "No approval gate, plan version or audit trail",
         "The plan is recalculated rather than approved. Nothing is frozen, no one is accountable "
         "for the result, and the factory has no stable commitment to execute against. A schedule "
         "that can change silently is not a schedule."],
    ],
    [7, 25, 68], size=9)
D.callout(
    "The distinction that matters",
    "The proposal computes what inventory coverage says you should make. A master production "
    "schedule states what you will make, given what the plant can actually do, and holds that "
    "statement still long enough for people to act on it. The gap between those two things is "
    "G-16 and G-17, and everything else in this annex is secondary to them.",
    C.LIGHT, C.BLUE)

# ==========================================================================
D.pagebreak()
D.h1("D.3  What the proposal gets right")
D.p("The planning instinct in this document is sound, and in several respects it is closer to what "
    "a planner needs than the vendor scope document assessed in Annex A. These strengths should be "
    "retained and built on, not rebuilt.")
for title, body in C.ASSESS_STRENGTHS:
    D.h3(title)
    D.p(body, size=9.5)

D.callout(
    "The planner-facing design is the strongest part of the proposal",
    "Week Cover measured against Policy Week with red, amber and green banding, batch-level "
    "rounding shown transparently, in-transit and quality inspection stock separated out, and a "
    "simulation control to test an intervention before committing. A planner could work from this "
    "screen tomorrow. The problem with this proposal is scope and governance, not craft, and that "
    "is the better problem to have.",
    "ECFDF3", C.GREEN)

# ==========================================================================
D.section(landscape=True)
D.h1("D.4  Gap register extension")
D.p("These entries extend the consolidated gap register in Annex A, which covers the vendor scope "
    "document. Entries G-01 to G-15 relate to that document; G-16 to G-24 below relate to the MPS "
    "Vietnam proposal and are confined to master production scheduling.")
D.table(
    ["Ref", "Gap", "What the proposal does", "Why it matters", "Requirement affected"],
    [[g[0], g[1], g[2], g[3], g[4]] for g in C.ASSESS_GAPS],
    [4, 15, 32, 34, 15], size=8)

# ==========================================================================
D.section(landscape=False)
D.h1("D.5  Specification defects")
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
D.h1("D.6  Reconciliation with the vendor scope document")
D.p("Two proposals are now live and both claim master production scheduling, in different systems, "
    "using different logic. This has to be resolved before either is built, independently of "
    "anything to do with MRP.")

D.table(
    ["", "Vendor scope document v1.0", "MPS Vietnam proposal"],
    [
        ["Master scheduling logic", "Absent. One line, delegated to SAP.",
         "Present. Coverage-driven, weekly buckets."],
        ["Where MPS runs", "Inside SAP.",
         "In the SQL calculation engine on the data warehouse."],
        ["Constrained optimization", "Absent. Assumed to be SAP, which cannot do it.", "Absent."],
        ["MPS approval gate", "Absent.", "Absent."],
        ["Horizon", "Not defined. Left open as a business question.",
         "5 months, stated inconsistently as 28 weeks."],
        ["Planner front end", "Portal with upload and results dashboard.",
         "Planning application with a time-phased grid."],
        ["Capacity master data", "Not in scope.", "Not in scope."],
    ],
    [22, 39, 39], size=8.5, bold_col0=True)

D.callout(
    "If both were built as written",
    "The business would have two master scheduling engines in two systems producing two different "
    "schedules, two planner front ends for one process, no constrained optimization in either, and "
    "no approval gate in either. The duplication is the expensive part; the shared blind spot is "
    "the dangerous part.",
    "FEF3E2", C.AMBER)

D.h2("D.6.1  Decisions this forces")
D.table(
    ["Ref", "Decision required", "Why it is open", "Owner", "Consequence of delay"],
    [[x[0], x[1], x[2], x[3], x[4]] for x in C.ASSESS_DECISIONS],
    [7, 24, 31, 16, 22], size=8.5)
D.p("These extend the decision register in section 12 of the main brief, which already carries "
    "D-01 to D-05. D-06 and D-07 should be closed in the same design workshop as D-02.",
    size=9, italic=True)

# ==========================================================================
D.pagebreak()
D.h1("D.7  Recommendation")

D.h2("D.7.1  Accept it as the first phase of the MPS build")
D.p("The recommendation is to accept the MPS Vietnam proposal as Phase 1a of the master production "
    "scheduling build: demand intake plus an unconstrained schedule. That is a sensible first "
    "delivery which gives planners something genuinely useful on its own, and the coverage logic "
    "and interface design are worth keeping.")
D.p("What matters is the framing. If this is signed off as the MPS solution, the programme will "
    "record master production scheduling as delivered while the constrained stage and the approval "
    "gate remain unbuilt. Those are not refinements. They are what turns a coverage calculation "
    "into a production schedule, and they need to be scoped and funded now.")

D.h2("D.7.2  Required to complete the unconstrained stage")
D.p("Eight additions are needed before the proposal fully delivers stages S1, S2 and S4. None is a "
    "large piece of work, and all are cheaper now than after the data model is frozen. RA-01 is a "
    "precondition to build rather than an enhancement.")
D.table(
    ["Ref", "Addition", "Detail", "Requirement"],
    [[a[0], a[1], a[2], a[3]] for a in C.ASSESS_ADDITIONS],
    [8, 21, 53, 18], size=8.5)

D.h2("D.7.3  Scope and fund the constrained stage separately")
D.p("Stage S3 is not in this proposal and is the larger half of master production scheduling. It "
    "should be scoped, estimated and funded explicitly rather than assumed into the existing "
    "statement of work. Three things are needed before it can start:")
D.bullet("routing, work centre, standard rate and shift calendar in the inbound scope (RA-08);",
         bold_lead="Data  ")
D.bullet("a changeover matrix at least at product family level, and campaign rules from Plant "
         "Operations;", bold_lead="Rules  ")
D.bullet("an optimization engine and the decision on solver technology and licensing. The model is "
         "specified in section 9.4 of the main brief.", bold_lead="Engine  ")
D.p("Benchmark the solver at full portfolio volume during build, not at user acceptance testing. "
    "Run time is a functional constraint: an optimizer that does not finish inside the weekly "
    "planning window is unusable however correct its answer.", size=9, italic=True)

D.h2("D.7.4  Architectural caution")
D.callout(
    "An analytics stack is the right place for the calculation and the wrong place for the state",
    "A SQL engine over a data warehouse is a good fit for computing a schedule. It is not a natural "
    "fit for the things that make a schedule authoritative: an immutable approved version, a "
    "planner approval that gates what happens next, an override audit trail, and a frozen zone that "
    "survives recalculation. Those need an application layer with transactional integrity sitting "
    "alongside the warehouse. This should be settled in the design workshop, before the "
    "architecture is frozen, because retrofitting plan state onto a reporting stack is expensive "
    "and is usually discovered late.",
    C.LIGHT, C.BLUE)

D.h2("D.7.5  Immediate next steps")
D.table(
    ["#", "Action", "Owner"],
    [
        ["1", "Close decisions D-06 and D-07 in the design workshop, alongside D-02.",
         "Supply Chain Planning and IT"],
        ["2", "Issue defects SD-01 to SD-05 to the authors, with SD-01 as a precondition to build.",
         "Supply Chain Planning"],
        ["3", "Add RA-01 to RA-08 to the Phase 1a scope before the statement of work is signed.",
         "Supply Chain Planning and IT"],
        ["4", "Reframe the proposal as Phase 1a of the MPS build in the programme plan, and record "
              "explicitly that the constrained stage and the approval gate are not covered by it.",
         "Programme management"],
        ["5", "Scope, estimate and fund the constrained optimization stage as a separate workstream.",
         "IT and Procurement"],
        ["6", "Add routing, work centre and capacity extraction to the current integration "
              "workstream rather than opening a second one later.", "IT Integration"],
    ],
    [5, 72, 23], size=9)

# ==========================================================================
D.pagebreak()
D.h1("D.8  Looking ahead")
D.p("Three forward notes, recorded so that decisions taken now do not quietly foreclose options "
    "later. None of these changes the assessment above.")
for title, body in C.ASSESS_FORWARD:
    D.h3(title)
    D.p(body, size=9.5)

D.callout(
    "The one cheap insurance policy",
    "Material requirements planning is out of scope today and is correctly absent from this "
    "proposal. But whatever eventually consumes the master production schedule will need to read "
    "it. Defining the approved plan as a versioned, machine-readable output now (RA-07) costs "
    "very little while the data model is still open, and removes a rework item from whichever "
    "project picks up the next stage.",
    "ECFDF3", C.GREEN)

D.d.add_paragraph()
D.p("End of Annex D", size=9, italic=True, color=C.GREY, align=CEN)

d.save(os.path.abspath(OUT))
print("Wrote", os.path.abspath(OUT))
