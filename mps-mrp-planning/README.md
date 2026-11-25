# Marico SEA — Integrated MPS & MRP Planning System

Business requirements pack for the non-SAP planning engine (EZ-Commerce) that calculates
Master Production Scheduling and Material Requirements Planning, and releases Planned
Independent Requirements into SAP S/4HANA for procurement execution.

Prepared by Supply Chain Planning for IT Solution Delivery and the vendor delivery team.
Responds to and supersedes the vendor scope document v1.0 (`SCOPE-MARICO-EZ-SAP-v1.0`)
as the statement of business requirement.

## Deliverables

| File | Format | Purpose |
|---|---|---|
| `Marico_MPS_MRP_Business_Requirements_Brief_v1.0.docx` | Word, 59 pages | The statement of business requirement: process, calculation logic, system boundary, interfaces, decisions, RACI, controls, 63 numbered requirements, NFRs, UAT scenarios, roadmap, risks, and a gap analysis against the vendor scope document. |
| `Marico_MPS_MRP_Process_Infographic_v1.0.pptx` | PowerPoint, 6 slides | Editable process pack: swimlane process flow, system boundary and interface map, planning calendar and time fences, RACI at a glance, and a before/after comparison against the vendor scope. All native shapes — restyle or re-brand directly. |
| `Marico_MPS_MRP_RACI_and_Registers_v1.0.xlsx` | Excel, 13 tabs | Filterable registers for the build team: RACI, interfaces, requirements, NFRs, master data ownership, controls, risks, gap analysis, decisions, open questions, UAT and roadmap. |
| `Marico_MPS_Vietnam_Proposal_Assessment_v1.0.docx` | Word, 12 pages | **Annex D** — assessment of the *MPS Vietnam Data Architecture & Integration Document* (19 Nov 2026), **scoped to master production scheduling only**. MRP, the material planner gate and release to SAP are deliberately not assessed. Extends the gap register with G-16 to G-24, adds specification defects SD-01 to SD-05, required additions RA-01 to RA-08 and open decisions D-06 and D-07. |

## The architecture in one sentence

EZ-Commerce is the planning brain; SAP S/4HANA is the execution system of record.
Every quantitative planning decision — netting, stock norms, lot sizing, capacity
resolution, BOM explosion — is calculated once, in EZ-Commerce. SAP receives an
already-net, already-feasible requirement, converts it into a purchase requisition,
and manages the purchase order, goods receipt and financial record.

## Three non-negotiable design points

1. **MPS and MRP are a sequence with a human gate between them**, not one automated
   event. No MRP against an unapproved MPS; nothing reaches SAP without MRP planner
   confirmation.
2. **Constrained planning must happen in EZ-Commerce.** Standard SAP MPS and MRP plan
   at infinite capacity and cannot honour line capacity, changeover, campaign rules or
   supplier allocation.
3. **Requirements are netted exactly once** (Decision D-01). If EZ-Commerce nets and
   SAP nets the same requirement again, the business systematically under-orders.

## Confirmed scope

- Single plant; single-level BOM, finished goods to raw and packing materials
- 300–800 finished goods, 1,500–4,000 raw and packing materials
- 12-month horizon in monthly buckets; weekly buckets for the current month plus three,
  extendable to six
- Constrained optimization: capacity and material availability, plus changeover/campaign
  and MOQ/lot-sizing; objective is lexicographic — minimise unmet demand, then cost
- Monthly S&OP, weekly MPS, two-week frozen zone
- Semi-finished/bulk planning deferred to phase 2 (Decision D-05)

## Open decision

**D-02 — how the approved finished goods plan reaches SAP** so production orders can be
created, confirmed, backflushed and costed. Three options are documented with pros, cons
and effort. Interface `IF-09` must not be built until this is closed.

## Two proposals are live, and both claim MPS

| | Vendor scope document v1.0 | MPS Vietnam proposal |
|---|---|---|
| Master scheduling logic | Absent — delegated to SAP | **Present** — coverage-driven, weekly |
| Where MPS runs | Inside SAP | SQL engine on the data warehouse |
| Constrained optimization | Absent | Absent |
| MPS approval gate | Absent | Absent |
| Horizon | Not defined | 5 months, stated inconsistently |
| Capacity master data | Not in scope | Not in scope |

Both place master production scheduling in a different system, and neither delivers the
constrained stage or the approval gate. See Annex D for the assessment and decisions
D-06 and D-07.

The MPS Vietnam proposal is scoped to MPS only, so Annex D does not assess MRP. Stages
S5 to S7 of the target process — BOM explosion, the material planner confirmation gate
and release to SAP — remain unaddressed by either document and will need their own
scope and owner when the business is ready.

## Regenerating the documents

```bash
python3 -m pip install python-docx python-pptx openpyxl Pillow
cd generators
python3 build_docx.py
python3 build_pptx.py
python3 build_xlsx.py
python3 build_assessment_docx.py
```

`generators/content.py` holds the shared registers (RACI, interfaces, requirements,
controls, risks, decisions, gap analysis, assessment) so the Word, PowerPoint and Excel
outputs cannot drift apart. Edit content there, not in the individual builders.
`generators/docxkit.py` holds the shared python-docx styling helpers used by both Word
documents.

Use `python3 -m pip`, not `pip3` — on some images `pip3` targets a different interpreter
than `python3`.
