# -*- coding: utf-8 -*-
"""
Shared content registers for the Marico SEA MPS/MRP planning deliverables.

Single source of truth for the RACI matrix, interface register, requirement
register, controls, risks and gap analysis, so that the Word brief, the
PowerPoint infographic and the Excel register never drift apart.
"""

DOC = {
    "company": "Marico South East Asia",
    "title": "Integrated MPS & MRP Planning System",
    "subtitle": "Business Process and Functional Requirements Brief",
    "doc_id": "BRD-MARICO-MPSMRP-v1.0",
    "version": "1.0",
    "date": "12 August 2026",
    "status": "For review and design workshop",
    "owner": "Supply Chain Planning (Planning Director)",
    "audience": "IT Solution Delivery, Integration Architecture, Vendor Delivery Team",
    "responds_to": "Vendor Scope Document v1.0 (SCOPE-MARICO-EZ-SAP-v1.0)",
    "planning_system": "EZ-Commerce Planning Engine",
    "erp": "SAP S/4HANA (on-premise / private cloud)",
}

# Palette aligned to the vendor document so the pack reads as one family.
NAVY = "0F162A"
BLUE = "0369A1"
CYAN = "38BCF7"
SLATE = "1D283B"
LIGHT = "EEF3F9"
LIGHTER = "F7FAFC"
WHITE = "FFFFFF"
AMBER = "B45309"
RED = "9F1239"
GREEN = "15803D"
GREY = "64748B"

# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------
ROLES = [
    ("DP", "Demand Planner", "Owns the consensus demand forecast: statistical baseline, commercial overlay, promotional uplift and new product phasing. Delivers the locked forecast version that starts every planning cycle."),
    ("SOP", "S&OP Manager", "Owns the monthly S&OP cycle and the integrity of the 12-month plan. Arbitrates between service, cost and inventory when demand and supply cannot be reconciled at planner level."),
    ("MPS", "MPS / Production Planner", "Owns the Master Production Schedule. Reviews, edits and approves the constrained production plan for finished goods, and is the single approval gate before MRP may run."),
    ("MRP", "MRP / Material Planner", "Owns raw and packaging material requirements. Reviews and confirms the exploded material plan and is the single approval gate before any requirement is released to SAP."),
    ("BUY", "Procurement Buyer", "Converts released purchase requisitions into purchase orders inside the short-term window, manages supplier confirmation, price and delivery performance."),
    ("OPS", "Plant Operations", "Owns manufacturing capacity, line availability, shift calendars, changeover standards and the executability of the approved schedule on the shop floor."),
    ("MDS", "Master Data Steward", "Owns the accuracy and lifecycle of material master, BOM, routing, work centre, purchasing info record and source list data in SAP."),
    ("IT", "IT Integration Lead", "Owns the EZ-Commerce platform, the SAP integration layer, interface monitoring, error handling, environment management and change control."),
]
ROLE_CODES = [r[0] for r in ROLES]

# ---------------------------------------------------------------------------
# Process stages and steps
# ---------------------------------------------------------------------------
STAGES = [
    {
        "id": "S1",
        "name": "Demand Intake and Forecast Validation",
        "system": "EZ-Commerce",
        "owner": "Demand Planner",
        "purpose": "Convert the agreed commercial forecast into a locked, quality-checked, machine-readable demand signal that the planning engine can run against without further interpretation.",
        "trigger": "Monthly S&OP consensus sign-off, and each weekly MPS cycle for in-month reforecast.",
        "inputs": [
            "Consensus forecast by FG SKU by month, 12-month rolling horizon (Excel template, phase 1)",
            "Promotional and new product launch phasing overlay",
            "Prior locked forecast version, for variance comparison",
        ],
        "logic": [
            "Validate file structure, material code existence, plant assignment, unit of measure and date range against SAP master data already synchronised into EZ-Commerce.",
            "Reject records for materials not extended to the plant, inactive materials, or dates falling inside the frozen zone without an approved exception.",
            "Run duplicate detection on the natural key (material, plant, demand version, bucket) and block silent double-loading.",
            "Split monthly forecast into weekly buckets across the constrained window using the SKU weekly demand profile; monthly buckets are retained beyond it.",
            "Compute variance versus the previous locked version and highlight any SKU moving more than the configured tolerance.",
        ],
        "outputs": [
            "Locked, versioned demand plan with immutable version identifier and audit stamp",
            "Data quality exception report for rejected or suspect records",
            "Forecast variance report versus prior version",
        ],
        "gate": "Demand Planner locks the forecast version. No MPS run may execute against an unlocked or partially validated version.",
    },
    {
        "id": "S2",
        "name": "Unconstrained MPS Heuristic (12 Months, Monthly)",
        "system": "EZ-Commerce",
        "owner": "MPS / Production Planner",
        "purpose": "Establish what the business would need to produce if capacity and material were unlimited, giving a clean statement of true demand on the supply chain and early visibility of long-horizon pressure.",
        "trigger": "Automatically on forecast lock; on demand from the MPS Planner.",
        "inputs": [
            "Locked demand plan (S1)",
            "Current FG inventory, batch and expiry position from SAP",
            "Open production orders and confirmed receipts from SAP",
            "FG stock norms and planning parameters maintained in EZ-Commerce",
        ],
        "logic": [
            "Project inventory forward bucket by bucket across the 12-month horizon.",
            "Compute net requirement per bucket as demand plus target closing stock, less projected opening stock and less scheduled receipts.",
            "Apply lot-sizing policy (lot-for-lot, fixed lot, period of supply or minimum batch) to convert net requirement into proposed production quantities.",
            "Respect the frozen zone: buckets inside the frozen horizon are locked to the previously approved plan and are not re-planned.",
            "Flag any bucket where projected stock falls below safety stock, or where the plan implies an obvious capacity breach against nominal line rates.",
        ],
        "outputs": [
            "Unconstrained MPS proposal by FG SKU by month, 12 months",
            "Projected inventory and coverage profile",
            "Early warning list of capacity and material pressure points beyond the constrained window",
        ],
        "gate": "No approval gate. This is a diagnostic and input to S3.",
    },
    {
        "id": "S3",
        "name": "Constrained MPS Optimization (Weekly, 3 to 6 Months)",
        "system": "EZ-Commerce",
        "owner": "MPS / Production Planner",
        "purpose": "Produce a genuinely executable production plan inside the tactical window by resolving the plan against finite capacity, material availability, campaign rules and lot-sizing economics.",
        "trigger": "Automatically on completion of S2; re-runnable on demand for scenario comparison.",
        "inputs": [
            "Unconstrained MPS proposal (S2)",
            "Line and work centre capacity calendar, shift patterns, planned maintenance and efficiency factors",
            "Changeover matrix and campaign or family grouping rules",
            "Material availability signals: supplier constraints, allocations, long lead time items",
            "Minimum order quantity, minimum batch size and rounding values",
        ],
        "logic": [
            "Solve a mixed-integer optimization over weekly buckets for the current month plus the next three months, configurable to extend to six months.",
            "Hard constraints: available line capacity including changeover time, material availability, minimum and multiple lot sizes, and the frozen time fence.",
            "Objective, applied lexicographically: first minimise unmet or late demand, weighted by SKU service priority; then minimise total cost of changeover, overtime, inventory holding and expediting.",
            "Group production into campaigns where the changeover matrix makes sequencing economically material.",
            "Where demand cannot be met, the model must return an explicit, quantified shortfall with the binding constraint identified, not a silently truncated plan.",
        ],
        "outputs": [
            "Constrained MPS proposal by FG SKU by week across the tactical window",
            "Capacity utilisation profile by line and week",
            "Unmet demand report with binding constraint attribution",
            "Scenario comparison against the prior approved plan and against the unconstrained case",
        ],
        "gate": "No system approval. The output is a proposal for the MPS Planner.",
    },
    {
        "id": "S4",
        "name": "MPS Review and Approval Gate",
        "system": "EZ-Commerce",
        "owner": "MPS / Production Planner",
        "purpose": "Apply human judgement the model cannot hold, and establish a single, authorised, frozen production plan that becomes the sole demand input to material planning.",
        "trigger": "Constrained optimization complete, within the weekly MPS calendar.",
        "inputs": [
            "Constrained MPS proposal and exception reports (S3)",
            "Plant Operations feedback on executability",
            "Commercial priority guidance for allocation of short supply",
        ],
        "logic": [
            "Planner reviews exceptions first: unmet demand, capacity breaches, campaign violations and time fence conflicts.",
            "Planner may override any proposed quantity or timing. Every override is captured with user, timestamp, previous value, new value and mandatory reason code.",
            "System revalidates the edited plan against capacity and time fence rules and warns on any newly created infeasibility.",
            "Unresolved shortfalls are escalated to the S&OP Manager rather than absorbed silently.",
            "Planner approves and freezes the plan, creating an immutable, versioned MPS baseline.",
        ],
        "outputs": [
            "Approved and frozen MPS version, uniquely identified and fully auditable",
            "Override log with reason codes",
            "Escalation list for S&OP resolution",
        ],
        "gate": "MANDATORY APPROVAL GATE. MRP cannot be triggered against an unapproved MPS version. This gate is the defect that the vendor scope document omits.",
    },
    {
        "id": "S5",
        "name": "MRP Explosion and Netting",
        "system": "EZ-Commerce",
        "owner": "MRP / Material Planner",
        "purpose": "Translate the approved production plan into a time-phased, netted requirement for every raw and packaging material, calculated once and calculated in EZ-Commerce.",
        "trigger": "Automatically on MPS approval; scheduled daily refresh against live inventory.",
        "inputs": [
            "Approved MPS version (S4)",
            "Single-level BOM with component quantities, scrap and validity dates from SAP",
            "RM/PM inventory, batch, expiry and quality-hold status from SAP",
            "Open purchase orders, open purchase requisitions and goods in transit from SAP",
            "RM/PM stock norms, lead times, MOQ and rounding values",
        ],
        "logic": [
            "Explode the approved FG plan through the single-level BOM to gross component requirement, applying component scrap and BOM validity dates.",
            "Offset each requirement backwards by the material's planned delivery time plus goods receipt processing time to give the required order date.",
            "Net gross requirement against projected available stock, excluding quality-hold and expired batches, then against open purchase orders and goods in transit.",
            "Apply the RM/PM stock norm as target closing coverage, then apply lot-sizing, MOQ and rounding to give the proposed order quantity.",
            "Generate exceptions: shortages inside lead time, material expiring before consumption, MOQ forcing excess coverage, and requirements against blocked or unsourced materials.",
        ],
        "outputs": [
            "Net RM/PM requirement by material by week with required order date",
            "Projected material coverage profile",
            "MRP exception list",
        ],
        "gate": "No automatic release. Output is a proposal for the Material Planner.",
    },
    {
        "id": "S6",
        "name": "MRP Confirmation Gate",
        "system": "EZ-Commerce",
        "owner": "MRP / Material Planner",
        "purpose": "Ensure no requirement reaches SAP, and therefore no procurement commitment begins, without a named planner accepting responsibility for it.",
        "trigger": "MRP explosion complete.",
        "inputs": [
            "Net RM/PM requirement proposal and exception list (S5)",
            "Supplier capability and confirmed constraint feedback",
        ],
        "logic": [
            "Planner works the exception list before the full list, by design.",
            "Planner may adjust quantity, required date or lot size, with mandatory reason code and full audit capture.",
            "System blocks confirmation while any hard error remains unresolved, for example a requirement against a material with no valid source of supply.",
            "Planner confirms and releases; the confirmed set is versioned and locked against further edit.",
        ],
        "outputs": [
            "Confirmed and released RM/PM requirement set, versioned",
            "Release audit record naming the confirming planner",
        ],
        "gate": "MANDATORY APPROVAL GATE. Nothing is transmitted to SAP without this confirmation.",
    },
    {
        "id": "S7",
        "name": "Release to SAP, Procurement Execution and Feedback",
        "system": "EZ-Commerce to SAP S/4HANA",
        "owner": "IT Integration Lead / Procurement Buyer",
        "purpose": "Transmit the confirmed plan into SAP as the execution trigger, convert it into procurement documents, and close the loop by returning execution reality to the planning engine.",
        "trigger": "MRP planner confirmation (S6).",
        "inputs": [
            "Confirmed RM/PM requirement set (S6)",
            "SAP material master, MRP configuration and purchase requisition document type configuration",
        ],
        "logic": [
            "Transmit confirmed requirements to SAP as Planned Independent Requirements against a dedicated requirement type reserved for EZ-Commerce, using the S/4HANA OData planned independent requirement service.",
            "Transmission is idempotent and keyed on planning version, material, plant and bucket, so a replay corrects rather than duplicates.",
            "SAP MRP runs against the in-scope materials under the neutralised configuration defined in Decision D-01, converting requirements one-for-one into purchase requisitions of a dedicated document type.",
            "Buyer reviews purchase requisitions falling inside the short-term conversion window and converts them to purchase orders.",
            "SAP returns purchase requisition numbers, purchase order numbers, confirmed dates, goods receipts and stock movements to EZ-Commerce.",
            "Daily reconciliation compares requirement released from EZ-Commerce against requirement present in SAP and raises any variance as a control exception.",
        ],
        "outputs": [
            "Planned Independent Requirements in SAP",
            "Purchase requisitions of the dedicated document type",
            "Purchase orders inside the short-term window",
            "Closed-loop confirmation and reconciliation report in EZ-Commerce",
        ],
        "gate": "Automated, but under control C-05 reconciliation. Interface failure must alert, never fail silently.",
    },
]

# ---------------------------------------------------------------------------
# RACI  (R responsible, A accountable, C consulted, I informed)
# ---------------------------------------------------------------------------
RACI = [
    ("1.1", "S1", "Prepare and agree the consensus demand forecast", {"DP": "R", "SOP": "A", "MPS": "C", "MRP": "I", "BUY": "I", "OPS": "I", "MDS": "", "IT": ""}),
    ("1.2", "S1", "Load forecast into EZ-Commerce and clear validation errors", {"DP": "R", "SOP": "A", "MPS": "C", "MRP": "I", "BUY": "", "OPS": "", "MDS": "C", "IT": "C"}),
    ("1.3", "S1", "Resolve master data rejections raised by validation", {"DP": "C", "SOP": "I", "MPS": "C", "MRP": "C", "BUY": "", "OPS": "", "MDS": "R", "IT": "A"}),
    ("1.4", "S1", "Lock the forecast version for the planning cycle", {"DP": "R", "SOP": "A", "MPS": "I", "MRP": "I", "BUY": "", "OPS": "", "MDS": "", "IT": "I"}),
    ("2.1", "S2", "Synchronise master data and inventory from SAP", {"DP": "I", "SOP": "", "MPS": "I", "MRP": "I", "BUY": "", "OPS": "", "MDS": "C", "IT": "A/R"}),
    ("2.2", "S2", "Maintain FG stock norms and planning parameters", {"DP": "C", "SOP": "A", "MPS": "R", "MRP": "C", "BUY": "", "OPS": "C", "MDS": "I", "IT": "I"}),
    ("2.3", "S2", "Run the unconstrained MPS heuristic over 12 months", {"DP": "I", "SOP": "I", "MPS": "A/R", "MRP": "I", "BUY": "", "OPS": "I", "MDS": "", "IT": "C"}),
    ("2.4", "S2", "Review projected inventory and long-horizon pressure points", {"DP": "C", "SOP": "C", "MPS": "A/R", "MRP": "C", "BUY": "I", "OPS": "C", "MDS": "", "IT": ""}),
    ("3.1", "S3", "Maintain capacity calendar, shift pattern and line efficiency", {"DP": "", "SOP": "I", "MPS": "C", "MRP": "", "BUY": "", "OPS": "A/R", "MDS": "I", "IT": "I"}),
    ("3.2", "S3", "Maintain changeover matrix, campaign rules, MOQ and lot sizes", {"DP": "", "SOP": "I", "MPS": "R", "MRP": "C", "BUY": "C", "OPS": "A", "MDS": "C", "IT": "I"}),
    ("3.3", "S3", "Confirm material supply constraints and supplier allocations", {"DP": "", "SOP": "I", "MPS": "C", "MRP": "R", "BUY": "A", "OPS": "I", "MDS": "", "IT": ""}),
    ("3.4", "S3", "Run the constrained optimization across the tactical window", {"DP": "", "SOP": "I", "MPS": "A/R", "MRP": "I", "BUY": "", "OPS": "C", "MDS": "", "IT": "C"}),
    ("3.5", "S3", "Review optimization exceptions and unmet demand", {"DP": "C", "SOP": "C", "MPS": "A/R", "MRP": "C", "BUY": "I", "OPS": "C", "MDS": "", "IT": ""}),
    ("4.1", "S4", "Adjust and override the proposed production plan", {"DP": "I", "SOP": "C", "MPS": "A/R", "MRP": "I", "BUY": "", "OPS": "C", "MDS": "", "IT": ""}),
    ("4.2", "S4", "Validate the edited plan against frozen and firm time fences", {"DP": "", "SOP": "C", "MPS": "A/R", "MRP": "I", "BUY": "", "OPS": "C", "MDS": "", "IT": ""}),
    ("4.3", "S4", "Approve and freeze the MPS version", {"DP": "I", "SOP": "C", "MPS": "A/R", "MRP": "I", "BUY": "I", "OPS": "I", "MDS": "", "IT": "I"}),
    ("4.4", "S4", "Escalate unresolved capacity or supply shortfalls", {"DP": "C", "SOP": "A", "MPS": "R", "MRP": "C", "BUY": "C", "OPS": "C", "MDS": "", "IT": ""}),
    ("5.1", "S5", "Explode the approved MPS through the BOM to RM/PM", {"DP": "", "SOP": "", "MPS": "I", "MRP": "A/R", "BUY": "I", "OPS": "", "MDS": "C", "IT": "C"}),
    ("5.2", "S5", "Net against stock, open purchase orders and goods in transit", {"DP": "", "SOP": "", "MPS": "I", "MRP": "A/R", "BUY": "C", "OPS": "", "MDS": "", "IT": "C"}),
    ("5.3", "S5", "Maintain RM/PM stock norms, lead times and lot-sizing policy", {"DP": "", "SOP": "I", "MPS": "C", "MRP": "A/R", "BUY": "C", "OPS": "", "MDS": "C", "IT": ""}),
    ("5.4", "S5", "Review MRP exceptions: shortage, expiry, MOQ, unsourced material", {"DP": "", "SOP": "I", "MPS": "C", "MRP": "A/R", "BUY": "C", "OPS": "", "MDS": "C", "IT": ""}),
    ("6.1", "S6", "Adjust the proposed material requirement", {"DP": "", "SOP": "", "MPS": "C", "MRP": "A/R", "BUY": "C", "OPS": "", "MDS": "", "IT": ""}),
    ("6.2", "S6", "Confirm and release the material requirement set", {"DP": "", "SOP": "I", "MPS": "I", "MRP": "A/R", "BUY": "C", "OPS": "", "MDS": "", "IT": "I"}),
    ("7.1", "S7", "Transmit Planned Independent Requirements to SAP", {"DP": "", "SOP": "", "MPS": "I", "MRP": "C", "BUY": "I", "OPS": "", "MDS": "", "IT": "A/R"}),
    ("7.2", "S7", "Monitor interface execution and resolve transmission failures", {"DP": "", "SOP": "", "MPS": "I", "MRP": "C", "BUY": "I", "OPS": "", "MDS": "", "IT": "A/R"}),
    ("7.3", "S7", "Execute SAP MRP to convert requirements into purchase requisitions", {"DP": "", "SOP": "", "MPS": "", "MRP": "C", "BUY": "I", "OPS": "", "MDS": "C", "IT": "A/R"}),
    ("7.4", "S7", "Review and convert purchase requisitions to purchase orders", {"DP": "", "SOP": "", "MPS": "", "MRP": "C", "BUY": "A/R", "OPS": "", "MDS": "", "IT": "I"}),
    ("7.5", "S7", "Return purchase order, receipt and stock confirmations to EZ-Commerce", {"DP": "", "SOP": "", "MPS": "I", "MRP": "C", "BUY": "C", "OPS": "", "MDS": "", "IT": "A/R"}),
    ("7.6", "S7", "Reconcile released plan against SAP and clear variances", {"DP": "", "SOP": "I", "MPS": "C", "MRP": "R", "BUY": "C", "OPS": "", "MDS": "C", "IT": "A"}),
]

# ---------------------------------------------------------------------------
# Interface register
# ---------------------------------------------------------------------------
INTERFACES = [
    ("IF-01", "Consensus demand forecast", "Source demand system to EZ-Commerce", "Inbound", "Forecast by FG SKU, plant, bucket",
     "Phase 1: validated Excel/CSV upload through the portal. Phase 2: scheduled API or file transfer from the successor demand planning system.",
     "Weekly, and on monthly S&OP lock", "300-800 FG SKU x 12 months = up to 9,600 rows per version",
     "Row-level validation with rejection report; whole-file rollback on structural failure; version never partially committed."),
    ("IF-02", "Material master and MRP attributes", "SAP to EZ-Commerce", "Inbound", "Material master, plant data, MRP views, UoM, procurement type",
     "OData / CDS extraction from S/4HANA, delta by change pointer where available.", "Nightly", "Up to 5,000 material-plant records",
     "Delta failure falls back to full extract; stale-data alert if the last successful sync exceeds 26 hours."),
    ("IF-03", "Bill of material", "SAP to EZ-Commerce", "Inbound", "Single-level BOM header and components, quantity, scrap, validity",
     "OData / CDS extraction, validity-date aware.", "Nightly", "300-800 headers, roughly 6,000-12,000 component lines",
     "BOM with no valid component set blocks planning for that FG and raises a master data exception."),
    ("IF-04", "Routing, work centre and capacity", "SAP to EZ-Commerce", "Inbound", "Routing operations, work centre, standard rate, available capacity",
     "OData / CDS extraction; shift calendar and efficiency factor overlaid in EZ-Commerce.", "Nightly", "Under 1,000 records",
     "Missing routing defaults to the planner-maintained nominal line rate, flagged as an assumption in the optimization log."),
    ("IF-05", "Inventory position", "SAP to EZ-Commerce", "Inbound", "Unrestricted, quality-hold, blocked stock by material, plant, batch, expiry",
     "OData / CDS extraction; on-demand refresh callable immediately before an MRP run.", "Daily, plus on demand", "Up to 5,000 material-plant records, batch level higher",
     "MRP run is blocked if the inventory snapshot is older than the configured tolerance; planner is told the snapshot age explicitly."),
    ("IF-06", "Open supply elements", "SAP to EZ-Commerce", "Inbound", "Open purchase orders, open purchase requisitions, goods in transit, confirmed dates",
     "OData / CDS extraction.", "Daily, plus on demand", "1,500-4,000 open documents",
     "Netting must not run against a partial supply picture; incomplete extract aborts the run rather than under-stating supply."),
    ("IF-07", "Purchasing info record and source list", "SAP to EZ-Commerce", "Inbound", "Vendor, planned delivery time, MOQ, rounding value, price, validity",
     "OData / CDS extraction.", "Nightly", "2,000-6,000 records",
     "Material with no valid source of supply is blocked from release and raised as an exception at gate S6."),
    ("IF-08", "RM/PM Planned Independent Requirements", "EZ-Commerce to SAP", "Outbound", "Planned Independent Requirement, dedicated requirement type",
     "S/4HANA OData planned independent requirement service. Idempotent, keyed on planning version, material, plant and bucket.",
     "On MRP planner confirmation; typically weekly, capable of daily", "1,500-4,000 materials x weekly buckets",
     "Synchronous response captured per record; partial failure quarantines only failed records and permits targeted replay. Full audit of payload and response retained."),
    ("IF-09", "FG production plan", "EZ-Commerce to SAP", "Outbound", "Subject to open Decision D-02: FG Planned Independent Requirement, or planned order",
     "To be confirmed in the design workshop. See section 12, Decision D-02.", "On MPS approval, weekly", "300-800 FG SKU x weekly buckets",
     "Design pending. Interface must not be built before D-02 is closed."),
    ("IF-10", "Execution feedback", "SAP to EZ-Commerce", "Inbound", "Purchase requisition and purchase order numbers, confirmed dates, goods receipts",
     "OData / CDS extraction, keyed back to the originating planning version.", "Daily", "1,500-4,000 documents",
     "Feeds reconciliation control C-05; unmatched SAP documents are reported as orphans."),
]

# ---------------------------------------------------------------------------
# Requirement register
# ---------------------------------------------------------------------------
REQUIREMENTS = [
    # Demand
    ("REQ-101", "Demand", "The system shall accept a consensus forecast by FG SKU, plant and monthly bucket over a rolling 12-month horizon.", "Must"),
    ("REQ-102", "Demand", "The system shall validate every uploaded record against synchronised SAP master data and reject records for materials not extended to the plant, inactive, or without a valid unit of measure.", "Must"),
    ("REQ-103", "Demand", "The system shall detect and block duplicate demand records on the natural key of material, plant, demand version and bucket.", "Must"),
    ("REQ-104", "Demand", "The system shall version every forecast load immutably, with user, timestamp and source file retained for audit.", "Must"),
    ("REQ-105", "Demand", "The system shall disaggregate monthly forecast into weekly buckets across the constrained window using a maintainable SKU-level weekly profile.", "Must"),
    ("REQ-106", "Demand", "The system shall report variance between the current and prior locked forecast version and highlight SKUs exceeding a configurable tolerance.", "Should"),
    ("REQ-107", "Demand", "The system shall prevent any planning run from executing against an unlocked forecast version.", "Must"),
    ("REQ-108", "Demand", "The system shall support a future API-based forecast feed without redesign of the demand data model.", "Should"),
    # MPS
    ("REQ-201", "MPS", "The system shall run an unconstrained MPS heuristic across a 12-month horizon in monthly buckets.", "Must"),
    ("REQ-202", "MPS", "The system shall compute net requirement as gross demand plus target closing stock less projected opening stock less scheduled receipts, per bucket.", "Must"),
    ("REQ-203", "MPS", "The system shall support FG stock norms expressed as days of cover, fixed quantity, or statistical safety stock derived from demand variability and lead time at a configurable service level.", "Must"),
    ("REQ-204", "MPS", "The system shall apply configurable lot-sizing policies including lot-for-lot, fixed lot size, minimum batch and period of supply.", "Must"),
    ("REQ-205", "MPS", "The system shall hold all buckets inside the frozen horizon at the previously approved plan and exclude them from re-planning.", "Must"),
    ("REQ-206", "MPS", "The system shall project and display the forward inventory and coverage profile for every FG SKU across the full horizon.", "Must"),
    ("REQ-207", "MPS", "The system shall maintain all FG planning parameters within EZ-Commerce, under change control, and shall not depend on SAP MRP parameters for planning logic.", "Must"),
    # Optimization
    ("REQ-301", "Optimization", "The system shall run a constrained optimization in weekly buckets across the current month plus three months, configurable to extend to six months.", "Must"),
    ("REQ-302", "Optimization", "The optimization shall enforce finite line and work centre capacity, including changeover time consumption, as a hard constraint.", "Must"),
    ("REQ-303", "Optimization", "The optimization shall enforce material availability constraints for constrained and allocated materials as a hard constraint.", "Must"),
    ("REQ-304", "Optimization", "The optimization shall enforce minimum order quantity, minimum batch size and rounding value as hard constraints.", "Must"),
    ("REQ-305", "Optimization", "The optimization shall support sequence-dependent changeover cost and time through a maintainable changeover matrix.", "Must"),
    ("REQ-306", "Optimization", "The optimization shall support campaign or family grouping rules that keep related SKUs together within a production window.", "Must"),
    ("REQ-307", "Optimization", "The objective function shall be lexicographic: minimise weighted unmet or late demand first, then minimise total changeover, overtime, holding and expediting cost.", "Must"),
    ("REQ-308", "Optimization", "The system shall support SKU-level service priority weighting used by the objective function.", "Must"),
    ("REQ-309", "Optimization", "Where demand cannot be met, the system shall report the quantified shortfall and identify the binding constraint, and shall never silently truncate demand.", "Must"),
    ("REQ-310", "Optimization", "The system shall support saving, naming and comparing at least three what-if scenarios side by side before approval.", "Should"),
    ("REQ-311", "Optimization", "The system shall log every optimization run with input version, parameter set, solver status, objective value and run time.", "Must"),
    ("REQ-312", "Optimization", "The system shall return a feasible best-known solution with a reported optimality gap if the configured time limit is reached.", "Must"),
    # Workflow
    ("REQ-401", "Workflow", "The system shall require explicit MPS Planner approval before any MRP calculation may execute against a plan version.", "Must"),
    ("REQ-402", "Workflow", "The system shall require explicit MRP Planner confirmation before any requirement is transmitted to SAP.", "Must"),
    ("REQ-403", "Workflow", "The system shall capture every planner override with user, timestamp, previous value, new value and a mandatory reason code from a maintainable list.", "Must"),
    ("REQ-404", "Workflow", "The system shall revalidate an edited plan against capacity and time fence rules and warn the planner of any newly created infeasibility before approval.", "Must"),
    ("REQ-405", "Workflow", "The system shall present an exception workbench that allows planners to work by exception rather than reviewing the full plan line by line.", "Must"),
    ("REQ-406", "Workflow", "The system shall enforce segregation of duties so that the approving role is configurable and auditable per plant.", "Should"),
    ("REQ-407", "Workflow", "The system shall retain every approved plan version and support comparison of any two versions.", "Must"),
    ("REQ-408", "Workflow", "The system shall provide an escalation route for unresolved shortfalls to the S&OP Manager, with status tracking.", "Should"),
    # MRP
    ("REQ-501", "MRP", "The system shall explode the approved MPS through the single-level BOM to raw and packaging material requirements, honouring component scrap and BOM validity dates.", "Must"),
    ("REQ-502", "MRP", "The system shall offset each component requirement by planned delivery time plus goods receipt processing time to derive the required order date.", "Must"),
    ("REQ-503", "MRP", "The system shall net gross requirement against projected available stock, excluding quality-hold, blocked and expired batches.", "Must"),
    ("REQ-504", "MRP", "The system shall net against open purchase orders, open purchase requisitions and goods in transit, using confirmed dates where available.", "Must"),
    ("REQ-505", "MRP", "The system shall apply RM/PM stock norms, MOQ, rounding value and lot-sizing policy to derive the proposed order quantity.", "Must"),
    ("REQ-506", "MRP", "The system shall raise exceptions for shortages inside lead time, materials expiring before planned consumption, MOQ-driven excess coverage, and materials with no valid source of supply.", "Must"),
    ("REQ-507", "MRP", "The system shall support a daily MRP refresh against updated inventory and supply data without requiring a new MPS approval.", "Should"),
    ("REQ-508", "MRP", "The data model shall support a semi-finished or bulk planning level in a later phase without restructuring, even though phase 1 plans a single BOM level.", "Should"),
    # Integration
    ("REQ-601", "Integration", "The system shall transmit confirmed RM/PM requirements to SAP as Planned Independent Requirements against a dedicated requirement type reserved for EZ-Commerce.", "Must"),
    ("REQ-602", "Integration", "Outbound transmission shall be idempotent, keyed on planning version, material, plant and bucket, so that a replay corrects rather than duplicates requirements.", "Must"),
    ("REQ-603", "Integration", "The system shall transmit net requirement, and SAP netting shall be neutralised for in-scope materials in line with Decision D-01, so that requirements are netted exactly once.", "Must"),
    ("REQ-604", "Integration", "The system shall capture and retain the request payload and SAP response for every transmitted record.", "Must"),
    ("REQ-605", "Integration", "Partial transmission failure shall quarantine only the failed records and permit targeted replay without resending the successful set.", "Must"),
    ("REQ-606", "Integration", "The system shall alert a named support group on any interface failure, and shall never fail silently.", "Must"),
    ("REQ-607", "Integration", "The system shall refresh inventory and open supply data on demand immediately before an MRP run, and block the run if the snapshot exceeds a configurable age.", "Must"),
    ("REQ-608", "Integration", "SAP shall assign a dedicated purchase requisition document type to requisitions arising from EZ-Commerce requirements, distinguishable from manual requisitions.", "Must"),
    ("REQ-609", "Integration", "The system shall receive purchase requisition and purchase order numbers, confirmed dates and goods receipts back from SAP and link them to the originating planning version.", "Must"),
    ("REQ-610", "Integration", "All master data interfaces shall support both delta and full extraction, with automatic fallback to full extraction on delta failure.", "Should"),
    # Data
    ("REQ-701", "Data", "SAP shall remain the system of record for material master, BOM, routing, work centre capacity, purchasing info records and inventory.", "Must"),
    ("REQ-702", "Data", "EZ-Commerce shall be the system of record for planning parameters: stock norms, coverage policy, lot-sizing policy, service priority, campaign rules, changeover matrix and planning calendars.", "Must"),
    ("REQ-703", "Data", "Every planning parameter change shall be subject to change control with maker-checker approval and full audit history.", "Must"),
    ("REQ-704", "Data", "The system shall report master data quality exceptions that block planning, and shall route them to the Master Data Steward.", "Must"),
    ("REQ-705", "Data", "The system shall retain planning versions, override logs and interface payloads for a minimum of 24 months.", "Should"),
    # Control
    ("REQ-801", "Control", "The system shall perform a daily reconciliation between requirements released from EZ-Commerce and requirements present in SAP, and report any variance.", "Must"),
    ("REQ-802", "Control", "The system shall identify SAP purchase requisitions of the dedicated document type that have no matching EZ-Commerce requirement, as orphan records.", "Must"),
    ("REQ-803", "Control", "The system shall measure and report plan stability, comparing each approved MPS version against the prior version inside the firm horizon.", "Should"),
    ("REQ-804", "Control", "The system shall report MPS attainment, comparing approved plan against actual production confirmed in SAP.", "Should"),
    ("REQ-805", "Control", "The system shall report forecast accuracy and bias by SKU and by month, to feed the S&OP cycle.", "Could"),
]

# ---------------------------------------------------------------------------
# Non-functional requirements
# ---------------------------------------------------------------------------
NFRS = [
    ("NFR-01", "Performance: unconstrained MPS", "Complete a full 12-month monthly run for the entire FG portfolio in under 10 minutes."),
    ("NFR-02", "Performance: constrained optimization", "Return a solution with an optimality gap of 5 percent or better within 30 minutes for the full portfolio over a 13-week window; a configurable time limit must always return the best feasible solution found."),
    ("NFR-03", "Performance: MRP explosion", "Complete a full BOM explosion and netting cycle for the full material portfolio in under 15 minutes."),
    ("NFR-04", "Volume", "Support 800 finished goods and 4,000 raw and packaging materials in a single plant, with headroom for 100 percent growth without re-architecture."),
    ("NFR-05", "Volume: transactions", "Support transmission of at least 50,000 requirement records per release cycle."),
    ("NFR-06", "Concurrency", "Support at least 15 concurrent planning users with no material degradation of interactive response."),
    ("NFR-07", "Interactive response", "Screen and grid interactions to respond within 3 seconds for datasets up to 20,000 rows."),
    ("NFR-08", "Availability", "99.5 percent availability during the planning window, defined as 07:00 to 19:00 local time, Monday to Saturday."),
    ("NFR-09", "Recovery", "Recovery point objective of 4 hours and recovery time objective of 8 hours for the planning database."),
    ("NFR-10", "Auditability", "Every plan version, parameter change, override and interface payload to be retained and queryable for 24 months."),
    ("NFR-11", "Security", "Role-based access control with segregation between demand, MPS, MRP and procurement roles; approval rights not delegable without audit."),
    ("NFR-12", "Integration resilience", "SAP unavailability must degrade gracefully: planning continues on the last good snapshot, with snapshot age shown to the planner and release blocked."),
    ("NFR-13", "Traceability", "Every requirement transmitted to SAP must be traceable back through MRP run, approved MPS version and locked forecast version."),
    ("NFR-14", "Usability", "A planner must be able to complete the weekly review and approval cycle working only from the exception workbench."),
]

# ---------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------
CONTROLS = [
    ("C-01", "Forecast completeness", "Locked forecast covers every active FG SKU with expected demand; missing SKUs reported before the MPS run.", "Demand Planner", "Each cycle"),
    ("C-02", "Master data readiness", "Every FG in the approved plan has a valid, in-date BOM and every component has a valid source of supply.", "Master Data Steward", "Daily"),
    ("C-03", "Snapshot freshness", "Inventory and open supply snapshot age is within tolerance at the moment of the MRP run; run blocked otherwise.", "IT Integration Lead", "Each run"),
    ("C-04", "Approval integrity", "No MRP execution without an approved MPS version, and no SAP transmission without MRP planner confirmation; violations logged as control breaches.", "MPS / MRP Planner", "Each cycle"),
    ("C-05", "Plan to SAP reconciliation", "Requirement quantity and date released from EZ-Commerce equals the requirement present in SAP, material by material, bucket by bucket.", "IT Integration Lead", "Daily"),
    ("C-06", "Double-netting guard", "In-scope materials carry the neutralised SAP MRP configuration defined in D-01; any drift in safety stock, lot size or coverage profile is reported.", "Master Data Steward", "Weekly"),
    ("C-07", "Orphan document check", "Purchase requisitions of the dedicated document type with no matching EZ-Commerce requirement are identified and cleared.", "Material Planner", "Weekly"),
    ("C-08", "Plan stability", "Change to the firm horizon between consecutive approved MPS versions is measured and reported against a stability threshold.", "S&OP Manager", "Weekly"),
]

# ---------------------------------------------------------------------------
# Risks
# ---------------------------------------------------------------------------
RISKS = [
    ("R-01", "Double netting understates requirements", "High", "High", "Requirements netted in EZ-Commerce are netted a second time by SAP MRP against the same stock and open orders, producing systematic under-ordering and unplanned shortages.", "Implement Decision D-01 in full: neutralised SAP configuration for in-scope materials, plus daily reconciliation control C-05 and configuration drift control C-06."),
    ("R-02", "Vendor scope does not include a planning engine", "High", "High", "The current vendor scope funds an upload portal and dashboards. The MPS heuristic and the optimizer, which carry the business value, are not specified and therefore not priced or scheduled.", "Reissue scope against this document and its numbered requirement register; re-baseline cost and timeline before build commences."),
    ("R-03", "Expectation that SAP performs constrained planning", "High", "High", "Standard SAP MPS and MRP plan at infinite capacity. Any design relying on SAP to honour capacity or supply constraints will fail in test, late.", "State the boundary explicitly in design; keep all constraint handling in EZ-Commerce; validate in UAT scenario UAT-04."),
    ("R-04", "Master data quality blocks go-live", "High", "Medium", "BOM validity, source lists, lead times, MOQ and rounding values are frequently incomplete; planning quality cannot exceed data quality.", "Run a master data readiness assessment before build completes; make control C-02 a go-live gate with a published threshold."),
    ("R-05", "Optimizer run time exceeds the planning window", "Medium", "High", "A mixed-integer model with changeover and campaign logic over 800 SKUs can fail to solve inside the weekly cycle.", "Design decomposition by line and product family from the start; enforce NFR-02 time limits with best-feasible return; benchmark at full volume during build, not at UAT."),
    ("R-06", "Planner adoption and trust", "Medium", "High", "If planners cannot see why the optimizer proposed a quantity, they will revert to spreadsheets and the investment is stranded.", "Mandate explainability: binding constraint attribution on every shortfall, exception workbench, and scenario comparison before approval."),
    ("R-07", "Parameter ownership drift", "Medium", "Medium", "Planning parameters maintained in both SAP and EZ-Commerce diverge, producing two different answers and undermining confidence.", "Enforce REQ-702 ownership split with change control; control C-06 reports drift weekly."),
    ("R-08", "Interface silent failure", "Medium", "High", "Partial transmission failures leave SAP with an incomplete requirement picture while the planner believes release succeeded.", "Idempotent keyed transmission, per-record response capture, quarantine and targeted replay, mandatory alerting under REQ-606."),
    ("R-09", "Scope creep into semi-finished planning", "Medium", "Medium", "The vendor scope assumes multi-level BOM including semi-finished goods; phase 1 is single level. Ambiguity becomes a change request.", "Decision D-05 records the single-level phase 1 boundary and the phase 2 intent explicitly, so neither party can claim change of scope."),
    ("R-10", "Forecast source migration", "Low", "Medium", "The phase 1 Excel intake becomes embedded, making the later move to a system feed a second project.", "Build the demand intake against an abstract interface from day one per REQ-108; Excel is one adapter, not the design."),
]

# ---------------------------------------------------------------------------
# Gap analysis against the vendor scope document
# ---------------------------------------------------------------------------
GAPS = [
    ("G-01", "Section 2, step 2-3", "Vendor scope treats MPS and MRP as a single automated sequence triggered from one upload, with SAP MRP run immediately after PIR creation.",
     "MPS and MRP are different decisions taken by different roles at different times. Running them together removes the Production Planner's control of the finished goods plan, which is the point of MPS.",
     "Separate the process into MPS, an approval gate, MRP, a confirmation gate, and only then release. No MRP execution against an unapproved MPS version.", "REQ-401, REQ-402"),
    ("G-02", "Section 2, step 2 (MPS Execution)", "MPS is described in a single line as an SAP run against 'Stock on hand, Inventory, Supply Constrain'.",
     "The entire master scheduling calculation is unspecified. There is no logic, no horizon, no bucket definition, no norms treatment and therefore nothing that can be estimated or built.",
     "Adopt the full MPS specification in sections 8 and 9, including the unconstrained heuristic and the constrained optimization model.", "REQ-201 to REQ-207"),
    ("G-03", "Section 2 and section 3.2", "Constraint handling is assumed to sit inside the SAP MPS and MRP run.",
     "Standard SAP MPS and MRP plan at infinite capacity. They cannot honour line capacity, changeover, campaign or supplier allocation constraints. This is a factual defect that will surface late in testing.",
     "Move all constraint handling into the EZ-Commerce optimizer. SAP receives an already-feasible plan.", "REQ-301 to REQ-309"),
    ("G-04", "Whole document", "No optimization capability of any kind is described: no capacity model, no changeover matrix, no campaign rules, no MOQ or lot-sizing economics, no objective function.",
     "The primary source of value, a feasible least-cost plan that protects service, is absent from the scope.",
     "Adopt the mixed-integer formulation in section 9.4 with the lexicographic objective and the constraint set defined there.", "REQ-301 to REQ-312"),
    ("G-05", "Section 4, pre-requisite 1", "Demand upload frequency is listed as an open question for the business: 'Daily/Weekly/Monthly'.",
     "Horizon and bucket profile are foundational design inputs, not a detail to settle later. They determine the data model, the solver size and the entire user experience.",
     "Fix the profile now: 12 months in monthly buckets, with weekly buckets for the current month plus three, extendable to six.", "REQ-101, REQ-105, REQ-301"),
    ("G-06", "Whole document", "No time fence or frozen period concept appears anywhere.",
     "Without a frozen zone the plan is rewritten every cycle, production loses stability, and procurement commitments are made against a plan that has already changed.",
     "Adopt the two-week frozen, firm and free zone policy in section 7, with defined change authority in each zone.", "REQ-205, REQ-404"),
    ("G-07", "Section 2, step 6", "The process ends with results 'rendered dynamically in EZ-Commerce'; there are no approval gates anywhere in the flow.",
     "Requirements would reach SAP, and procurement commitments would begin, with no named person having accepted responsibility for them.",
     "Insert the two mandatory gates at S4 and S6, with full override audit and reason codes.", "REQ-401 to REQ-407"),
    ("G-08", "Section 2, steps 4-5; section 3.2", "SAP performs the stock check, BOM explosion and netting, and generates planned orders and purchase requisitions.",
     "This contradicts the agreed architecture in which all quantitative calculation is performed in EZ-Commerce. It also creates the double-netting defect: requirements netted in EZ-Commerce are netted again by SAP.",
     "Restate the split per section 6. All calculation in EZ-Commerce; SAP receives requirements, creates purchase requisitions and manages purchase orders. Implement the D-01 guardrail.", "REQ-603, REQ-608"),
    ("G-09", "Section 3.2, Procurement Configuration", "Safety stock is listed as 'safety stock rules - If applicable', held in SAP.",
     "Stock norms are a core planning input, not an optional SAP setting. Holding them in SAP conflicts with the agreed ownership split and with the D-01 guardrail, which requires SAP-side safety stock to be zero for in-scope materials.",
     "Move all stock norms and planning parameters into EZ-Commerce under change control; set SAP safety stock to zero for in-scope materials.", "REQ-203, REQ-505, REQ-702"),
    ("G-10", "Whole document", "No RACI, no role definitions. Ownership is expressed only as a 'System Responsible' column.",
     "Systems do not own decisions, people do. Without defined accountability the approval gates cannot be enforced and exceptions have no owner.",
     "Adopt the eight-role RACI in section 13 and the accompanying register.", "REQ-406"),
    ("G-11", "Whole document", "No process flow diagram is present. The only images in the file are the vendor logo.",
     "A document describing a process mapping requirement contains no process map, so there is no shared visual understanding to design or test against.",
     "Use the swimlane flow and system map issued as the accompanying infographic pack.", "n/a"),
    ("G-12", "Whole document", "No non-functional requirements, data volumes, run-time expectations, reconciliation controls, test scenarios or phasing.",
     "The solution cannot be sized, engineered or accepted. Run time in particular is critical: an optimizer that does not finish inside the weekly cycle is unusable regardless of correctness.",
     "Adopt sections 14, 16, 17 and 18: controls, non-functional requirements, acceptance criteria and phased roadmap.", "NFR-01 to NFR-14"),
    ("G-13", "Section 1 and section 3", "Scope covers finished goods, semi-finished goods and raw and packing materials with multi-level BOM explosion.",
     "Phase 1 is a single plant with a single BOM level, finished goods to raw and packing materials. The mismatch is a live change-request risk in both directions.",
     "Record the phase 1 boundary and the phase 2 intent formally under Decision D-05.", "REQ-501, REQ-508"),
    ("G-14", "Section 5, MPS versus MRP table", "The comparison is generic textbook material, contrasting MRP types M0 and PD and listing transaction codes.",
     "It describes how SAP labels these runs, not how Marico will plan. It gives the build team no requirement to work from.",
     "Replace with the process definition in section 8 and the calculation logic in section 9.", "n/a"),
    ("G-15", "Section 2, step 2", "Planned Independent Requirements are referred to in a flow where the term is used loosely, and elsewhere the object is described as a purchase requirement.",
     "PIR is the Planned Independent Requirement, a demand element created through MD61 or its API. A purchase requisition is a different object created by MRP. Conflating them produces the wrong interface design.",
     "Use the terminology defined in Annex B consistently across all design documents.", "REQ-601"),
]

# ---------------------------------------------------------------------------
# Decisions
# ---------------------------------------------------------------------------
DECISIONS = [
    {
        "id": "D-01",
        "title": "Preventing double netting between EZ-Commerce and SAP",
        "status": "DECIDED - Option B",
        "problem": "EZ-Commerce nets gross requirements against stock, open purchase orders and goods in transit, and applies stock norms. If SAP MRP then nets the transmitted requirement against the same stock and the same open orders, the same supply is deducted twice. The result is systematic under-ordering: the plan looks correct in both systems, and the shortage appears only on the shop floor. This is the single highest technical risk in the design and it is not addressed anywhere in the vendor scope document.",
        "options": [
            ("A", "Send gross requirement, let SAP net", "EZ-Commerce transmits gross requirement and SAP MRP performs the netting.", "Uses SAP exactly as designed; no configuration gymnastics.", "Contradicts the agreed architecture. Netting logic, stock norms and lot sizing would be governed by SAP parameters, so the two systems would produce different answers and the planner would not be able to explain either."),
            ("B", "Send net requirement, neutralise SAP netting", "EZ-Commerce transmits net requirement. For in-scope materials, SAP is configured so that its MRP run performs no second netting and converts requirements one-for-one into purchase requisitions.", "Preserves the single planning brain. SAP still produces standard purchase requisitions through a standard MRP run, so no bespoke SAP development is needed. Planner sees one number in both systems.", "Requires disciplined and monitored SAP configuration for in-scope materials, and a reconciliation control to detect drift."),
            ("C", "Bypass SAP MRP, create purchase requisitions directly", "EZ-Commerce creates purchase requisitions in SAP directly through the purchase requisition API.", "Removes the double-netting problem completely; the shortest path from plan to procurement.", "SAP MRP is bypassed entirely for these materials, weakening standard SAP exception handling, rescheduling and pegging. Heavier interface, and a larger deviation from standard for the SAP support team to carry."),
        ],
        "decision": "Option B is adopted. EZ-Commerce transmits net requirement as Planned Independent Requirements against a dedicated requirement type, and SAP netting is neutralised for in-scope materials.",
        "implementation": [
            "Safety stock set to zero in SAP for all in-scope materials; the stock norm is applied in EZ-Commerce only.",
            "Lot size set to lot-for-lot (EX) with no rounding value and no minimum lot size in SAP; lot-sizing economics are applied in EZ-Commerce only.",
            "No range of coverage profile and no reorder point applied to in-scope materials in SAP.",
            "A dedicated requirement type reserved for EZ-Commerce, so its requirements are identifiable and separable from any other demand.",
            "A dedicated purchase requisition document type, so requisitions arising from EZ-Commerce are distinguishable from manual requisitions.",
            "Daily reconciliation, control C-05, comparing requirement released against requirement present in SAP, material by material and bucket by bucket.",
            "Weekly configuration drift check, control C-06, verifying that in-scope materials still carry the neutralised settings.",
        ],
        "consequence": "SAP performs no planning arithmetic for in-scope materials. It becomes the execution system of record: requirement in, purchase requisition out, purchase order managed, goods received, stock and cost recorded. Any future change to SAP MRP parameters for these materials must go through planning change control, not SAP master data change control.",
    },
    {
        "id": "D-02",
        "title": "How the approved finished goods production plan reaches SAP",
        "status": "OPEN - for design workshop",
        "problem": "The agreed architecture states that SAP receives Planned Independent Requirements, creates purchase requisitions and manages purchase orders. That describes the procurement path for raw and packaging materials. It does not yet answer how the approved finished goods production plan reaches SAP so that production orders can be created, confirmed, backflushed and costed. Production execution, shop floor confirmation, finished goods costing and inventory valuation all depend on this answer, so it must be closed before interface IF-09 is built.",
        "options": [
            ("A", "FG Planned Independent Requirement", "The approved MPS is transmitted as finished goods Planned Independent Requirements. SAP MRP converts them into planned orders, which the plant converts into production orders.", "Symmetrical with the raw and packing material path, uses the same interface pattern and the same SAP objects. Standard, well understood by any SAP support team.", "Adds a second SAP planning run for finished goods, which must also be neutralised under the D-01 principle to avoid re-netting the finished goods plan."),
            ("B", "Planned orders created directly", "The approved MPS is written into SAP directly as planned orders, bypassing the finished goods requirement layer.", "The approved plan appears in SAP exactly as approved, with no intermediate SAP calculation able to alter it. Tightest control of the finished goods schedule.", "A heavier and less standard interface. Planned order creation, change and deletion must all be managed across cycles, including the removal of orders that a re-plan has cancelled."),
            ("C", "Finished goods plan stays in EZ-Commerce", "Only raw and packing material requirements are sent to SAP. The finished goods schedule is executed from EZ-Commerce.", "Smallest integration footprint in phase 1.", "Leaves production orders, confirmations, backflush, finished goods costing and inventory valuation without an answer. Not recommended without a separate and explicit execution design."),
        ],
        "decision": "Not yet taken. To be closed in the design workshop before IF-09 is specified. Option A is the lowest-risk starting position because it reuses the pattern already being built for raw and packing materials, but the decision depends on how tightly the plant needs the approved schedule to be protected from SAP-side recalculation.",
        "implementation": [],
        "consequence": "Interface IF-09 remains unspecified until this decision is closed. No build effort should be committed against it. The decision does not block phase 1 development of the raw and packing material path.",
    },
    {
        "id": "D-03",
        "title": "Ownership of planning parameters",
        "status": "DECIDED",
        "problem": "Stock norms, coverage policy, lot-sizing rules, service priorities and campaign rules can be held in SAP or in EZ-Commerce. If they are held in both, the two systems produce different answers and planner confidence collapses.",
        "options": [],
        "decision": "SAP remains the system of record for engineering and logistics master data: material master, BOM, routing, work centre capacity, purchasing info records, source lists and inventory. EZ-Commerce is the system of record for all planning parameters: stock norms, coverage policy, lot-sizing policy, service priority weighting, campaign and changeover rules, and planning calendars.",
        "implementation": [
            "Planning parameter changes follow maker-checker approval inside EZ-Commerce with full audit history.",
            "SAP planning parameters for in-scope materials are set to the neutral values required by Decision D-01 and are not used for planning logic.",
        ],
        "consequence": "Planners can change planning behaviour without an SAP master data request, which materially shortens the change cycle. In exchange, EZ-Commerce must carry proper parameter governance rather than free-text fields.",
    },
    {
        "id": "D-04",
        "title": "Forecast source and its evolution",
        "status": "DECIDED",
        "problem": "The consensus forecast is prepared in Excel today, but will later originate from a dedicated demand planning system. Designing only for the Excel case would make the later migration a second project.",
        "options": [],
        "decision": "Phase 1 ingests a validated Excel or CSV consensus forecast through the portal. The demand intake is built against an abstract demand interface so that a system feed becomes an additional adapter, not a redesign.",
        "implementation": [
            "Demand data model, versioning and validation are independent of the transport mechanism.",
            "The Excel template is one adapter implementation; an API adapter is added in a later phase without changing the planning engine.",
        ],
        "consequence": "A small amount of additional design effort in phase 1 removes a disproportionately large migration cost later.",
    },
    {
        "id": "D-05",
        "title": "BOM depth and the phase boundary",
        "status": "DECIDED",
        "problem": "The vendor scope document assumes multi-level BOM explosion including semi-finished goods. The agreed phase 1 scope is a single plant with a single BOM level, finished goods to raw and packing materials. Left ambiguous, this becomes a change request in one direction or the other.",
        "options": [],
        "decision": "Phase 1 plans a single BOM level: finished goods to raw and packing materials, single plant. Semi-finished and bulk planning is explicitly deferred to phase 2, and the data model and engine are designed so that an additional planning level can be enabled without restructuring.",
        "implementation": [
            "The requirement and netting data model is level-agnostic from day one, per REQ-508.",
            "The phase 1 boundary and the phase 2 intent are both recorded in the contracted scope, so neither party can claim change of scope later.",
        ],
        "consequence": "Phase 1 build and test effort is materially smaller. Phase 2 adds a planning level rather than rebuilding the engine.",
    },
]

# ---------------------------------------------------------------------------
# UAT scenarios
# ---------------------------------------------------------------------------
UAT = [
    ("UAT-01", "Forecast validation and rejection", "Upload a forecast containing an inactive material, a material not extended to the plant, and a duplicate row.", "All three records are rejected with specific reasons; valid records are unaffected; no partial version is committed."),
    ("UAT-02", "Forecast version locking", "Attempt to run MPS against an unlocked forecast version.", "The run is refused with a clear message naming the unlocked version."),
    ("UAT-03", "Unconstrained MPS netting", "Run MPS for an SKU with known opening stock, a known stock norm and a known scheduled receipt.", "Net requirement equals demand plus target closing stock less opening stock less scheduled receipts, verified by hand calculation for at least ten SKUs."),
    ("UAT-04", "Capacity constraint is binding", "Load a demand pattern exceeding available line capacity in a specific week.", "The optimizer does not exceed available capacity; it reports quantified unmet demand and names capacity as the binding constraint."),
    ("UAT-05", "Changeover and campaign behaviour", "Plan a week containing several SKUs from two product families with a material changeover penalty between families.", "Production is grouped into campaigns; the changeover time consumed is visible in the capacity utilisation report."),
    ("UAT-06", "MOQ and rounding", "Plan an SKU whose net requirement is below its minimum batch size.", "The proposed quantity equals the minimum batch size; the resulting excess coverage is reported as an exception, not hidden."),
    ("UAT-07", "Frozen zone protection", "Attempt to change a quantity inside the two-week frozen zone.", "The change is blocked, or permitted only through the defined exception path with approval and reason code recorded."),
    ("UAT-08", "MPS approval gate", "Attempt to trigger MRP against an MPS version that has not been approved.", "MRP is refused; the audit log records the attempt."),
    ("UAT-09", "BOM explosion accuracy", "Explode an approved plan for an FG with a known BOM including component scrap and a validity date change mid-horizon.", "Component requirements match hand calculation, scrap is applied, and the validity date change is honoured at the correct bucket."),
    ("UAT-10", "Netting against open supply", "Run MRP for a material with unrestricted stock, a quality-hold batch, an expired batch and an open purchase order.", "Quality-hold and expired batches are excluded; the open purchase order is netted at its confirmed date."),
    ("UAT-11", "MRP confirmation gate and release", "Confirm and release a material requirement set.", "Planned Independent Requirements appear in SAP against the dedicated requirement type, quantity and bucket for quantity and date matching exactly; the release audit names the confirming planner."),
    ("UAT-12", "No double netting", "Release a requirement for a material holding significant free stock and an open purchase order, then run SAP MRP.", "The resulting purchase requisition quantity equals the requirement released by EZ-Commerce; stock and open orders are not deducted a second time."),
    ("UAT-13", "Idempotent replay", "Transmit the same confirmed requirement set twice.", "SAP holds one set of requirements, not two; the second transmission corrects rather than duplicates."),
    ("UAT-14", "Partial failure and targeted replay", "Force a transmission failure on a subset of records.", "Failed records are quarantined and reported; successful records remain; targeted replay corrects only the failed subset."),
    ("UAT-15", "Reconciliation control", "Manually alter a Planned Independent Requirement in SAP after release.", "The daily reconciliation reports the variance the following day, identifying material, bucket and difference."),
    ("UAT-16", "Solver time limit behaviour", "Run the optimizer at full portfolio volume with a restrictive time limit.", "A feasible plan is returned within the limit, with the optimality gap reported to the planner."),
]

# ---------------------------------------------------------------------------
# Roadmap
# ---------------------------------------------------------------------------
ROADMAP = [
    ("Phase 0", "Foundation and readiness", "6 to 8 weeks", [
        "Close Decision D-02 in the design workshop",
        "Master data readiness assessment against control C-02, with a published remediation plan",
        "SAP configuration design for D-01: requirement type, purchase requisition document type, neutralised MRP settings",
        "Confirm optimizer technology and benchmark solve time at full portfolio volume",
        "Re-baseline vendor scope and commercials against this requirement register",
    ]),
    ("Phase 1a", "Demand intake and unconstrained MPS", "8 to 10 weeks", [
        "Demand upload, validation, versioning and locking (REQ-101 to REQ-108)",
        "Inbound master data and inventory interfaces IF-02 to IF-07",
        "Unconstrained MPS heuristic over 12 months (REQ-201 to REQ-207)",
        "Projected inventory and coverage views",
    ]),
    ("Phase 1b", "Constrained optimization and MPS approval", "10 to 12 weeks", [
        "Capacity, changeover and campaign model (REQ-302 to REQ-306)",
        "Mixed-integer optimizer with lexicographic objective (REQ-301, REQ-307 to REQ-312)",
        "Exception workbench, override audit and scenario comparison",
        "MPS approval gate and version freeze (REQ-401, REQ-403 to REQ-407)",
    ]),
    ("Phase 1c", "MRP, release and controls", "8 to 10 weeks", [
        "BOM explosion, netting and lot sizing (REQ-501 to REQ-506)",
        "MRP confirmation gate (REQ-402)",
        "Outbound interface IF-08 with idempotency, quarantine and replay (REQ-601 to REQ-607)",
        "Execution feedback IF-10 and reconciliation controls C-05 to C-07",
        "UAT-01 to UAT-16, then pilot on a limited product family before full cutover",
    ]),
    ("Phase 2", "Semi-finished planning and daily MRP", "To be scoped", [
        "Enable the semi-finished and bulk planning level (REQ-508)",
        "Daily MRP refresh cycle (REQ-507)",
        "Close Decision D-02 implementation for the finished goods path, interface IF-09",
    ]),
    ("Phase 3", "Network and demand system integration", "To be scoped", [
        "API-based forecast feed from the successor demand planning system (REQ-108)",
        "Multi-plant and distribution network deployment logic",
        "Co-packer and subcontracting flows",
    ]),
]

# ---------------------------------------------------------------------------
# Glossary
# ---------------------------------------------------------------------------
GLOSSARY = [
    ("PIR - Planned Independent Requirement", "A planned demand element in SAP, held per material, plant and period, created through transaction MD61 or its equivalent API. It represents planned demand, not a purchasing document. Note: PIR is Planned Independent Requirement. It is not a purchase independent requirement, and it is not a purchase requisition. The vendor scope document uses the terms interchangeably in places, which leads directly to the wrong interface design."),
    ("PR - Purchase Requisition", "An internal request to procure, created by MRP or manually. It is the output of the material planning run and the input to purchase order creation. Distinct from PIR."),
    ("PO - Purchase Order", "The commercial commitment placed on a supplier, created by converting a purchase requisition."),
    ("MPS - Master Production Scheduling", "The process of deciding what finished goods to produce, in what quantity, in which period, balancing demand against capacity and material availability. In this design it is performed in EZ-Commerce, not SAP."),
    ("MRP - Material Requirements Planning", "The process of translating the approved production plan into time-phased raw and packaging material requirements through BOM explosion and netting. In this design it is performed in EZ-Commerce, not SAP."),
    ("Unconstrained plan", "A plan computed as if capacity and material were unlimited. It states true demand on the supply chain and is the input to constrained optimization."),
    ("Constrained plan", "A plan resolved against finite capacity, material availability, lot-sizing rules and campaign rules, and therefore executable."),
    ("Frozen zone", "The near horizon, two weeks in this design, in which the plan may not change without a formal exception. It gives production and procurement a stable commitment."),
    ("Firm zone", "The horizon beyond the frozen zone in which change is permitted but controlled and measured for stability."),
    ("Free zone", "The far horizon in which the plan is fully re-planned each cycle."),
    ("Time fence", "The boundary between planning zones, defining who may change the plan and under what authority."),
    ("Net requirement", "Gross demand plus target closing stock, less projected opening stock and less scheduled receipts. The quantity that actually has to be produced or purchased."),
    ("Stock norm", "The target inventory the business intends to hold, expressed as days of cover, a fixed quantity, or a statistically derived safety stock at a defined service level."),
    ("Lot-for-lot (EX)", "A lot-sizing rule producing exactly the net requirement, with no rounding or minimum. Required in SAP for in-scope materials under Decision D-01."),
    ("MOQ - Minimum Order Quantity", "The smallest quantity a supplier will accept, or the smallest economic production batch."),
    ("Changeover matrix", "The table of time and cost penalties incurred when switching production between two products, used by the optimizer to sequence economically."),
    ("Campaign", "A grouping of related products run together to avoid repeated changeover, for example by fragrance, flavour or allergen status."),
    ("Lexicographic objective", "An optimization objective applied in strict priority order: the second goal is optimised only among solutions that are already optimal for the first. Here, service is protected before cost is minimised."),
    ("Idempotency", "The property that transmitting the same message twice produces the same end state as transmitting it once. Essential for safe interface replay."),
    ("Double netting", "The defect in which the same stock and open supply are deducted twice, once in the planning system and once again in SAP, systematically understating requirements. Prevented by Decision D-01."),
]

OPEN_QUESTIONS = [
    ("Q-01", "Decision D-02: how does the approved finished goods plan reach SAP for production execution?", "Supply Chain Planning and IT", "Blocks interface IF-09"),
    ("Q-02", "Which optimization technology and solver will be used, and is a commercial solver licence required at the target volume?", "IT and vendor", "Blocks the Phase 1b estimate"),
    ("Q-03", "What is the confirmed line and work centre structure, including shift patterns and standard efficiency factors?", "Plant Operations", "Blocks the capacity model"),
    ("Q-04", "Is the changeover matrix available today, and at what level: SKU to SKU, or family to family?", "Plant Operations and MPS Planner", "Blocks REQ-305"),
    ("Q-05", "What service priority classification will drive the objective function weighting?", "S&OP Manager and Commercial", "Blocks REQ-308"),
    ("Q-06", "What is the current completeness of source lists, purchasing info records, lead times and MOQ for raw and packing materials?", "Master Data Steward and Procurement", "Determines the Phase 0 remediation effort"),
    ("Q-07", "Which requirement type and purchase requisition document type will be reserved for EZ-Commerce in SAP?", "SAP Functional and IT", "Blocks Decision D-01 implementation"),
    ("Q-08", "Is there an existing middleware layer, for example SAP Integration Suite, that the interfaces should use?", "IT Integration Architecture", "Determines the integration pattern"),
    ("Q-09", "What is the agreed short-term window inside which purchase requisitions are converted to purchase orders?", "Procurement", "Defines the buyer conversion rule at step 7.4"),
    ("Q-10", "Which product family will be used for the pilot before full cutover?", "Supply Chain Planning", "Blocks the Phase 1c cutover plan"),
]
