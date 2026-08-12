# -*- coding: utf-8 -*-
"""Build the editable process infographic as a .pptx.

Every element is a native PowerPoint shape or table, so the deck can be
restyled, re-branded and rebuilt by hand without regenerating it.
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls

import content as C

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "Marico_MPS_MRP_Process_Infographic_v1.0.pptx")

W, H = Inches(13.333), Inches(7.5)


def rgb(h):
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


NAVY, BLUE, CYAN = rgb(C.NAVY), rgb(C.BLUE), rgb(C.CYAN)
LIGHT, LIGHTER, WHITE = rgb(C.LIGHT), rgb(C.LIGHTER), rgb("FFFFFF")
SLATE, GREY = rgb(C.SLATE), rgb(C.GREY)
AMBER, GREEN, RED = rgb(C.AMBER), rgb(C.GREEN), rgb(C.RED)

prs = Presentation()
prs.slide_width, prs.slide_height = W, H
BLANK = prs.slide_layouts[6]


# --------------------------------------------------------------------------
def slide():
    s = prs.slides.add_slide(BLANK)
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, H)
    bg.fill.solid()
    bg.fill.fore_color.rgb = WHITE
    bg.line.fill.background()
    bg.shadow.inherit = False
    return s


def txt(s, x, y, w, h, text, size=12, bold=False, color=SLATE,
        align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, italic=False, spacing=1.0):
    tb = s.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.02)
    tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        r = p.add_run()
        r.text = line
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = color
        r.font.name = "Arial"
    return tb


def box(s, x, y, w, h, text="", fill=WHITE, line=None, size=11, bold=False,
        color=SLATE, align=PP_ALIGN.CENTER, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
        line_w=1.0, anchor=MSO_ANCHOR.MIDDLE, spacing=0.95):
    sh = s.shapes.add_shape(shape, x, y, w, h)
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(line_w)
    sh.shadow.inherit = False
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        try:
            sh.adjustments[0] = 0.08
        except Exception:
            pass
    tf = sh.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.03)
    tf.vertical_anchor = anchor
    for i, line_txt in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        r = p.add_run()
        r.text = line_txt
        r.font.size = Pt(size)
        r.font.bold = bold if i == 0 else False
        r.font.color.rgb = color
        r.font.name = "Arial"
    return sh


def arrow(s, x1, y1, x2, y2, color=BLUE, width=1.75, dash=False):
    cx = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, x1, y1, x2, y2)
    cx.line.color.rgb = color
    cx.line.width = Pt(width)
    ln = cx.line._get_or_add_ln()
    if dash:
        ln.append(parse_xml('<a:prstDash %s val="dash"/>' % nsdecls("a")))
    ln.append(parse_xml('<a:tailEnd %s type="triangle" w="med" len="med"/>'
                        % nsdecls("a")))
    return cx


def header(s, kicker, title, sub=None):
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, Inches(0.9))
    bar.fill.solid()
    bar.fill.fore_color.rgb = NAVY
    bar.line.fill.background()
    bar.shadow.inherit = False
    txt(s, Inches(0.5), Inches(0.12), Inches(9), Inches(0.22), kicker,
        size=9.5, bold=True, color=CYAN)
    txt(s, Inches(0.5), Inches(0.34), Inches(11.5), Inches(0.42), title,
        size=20, bold=True, color=WHITE)
    if sub:
        txt(s, Inches(0.5), Inches(0.98), Inches(12.3), Inches(0.3), sub,
            size=10.5, color=GREY)


def footer(s, n):
    txt(s, Inches(0.5), Inches(7.13), Inches(9), Inches(0.25),
        f"{C.DOC['company']}  |  {C.DOC['doc_id']}  |  Accompanies the Business "
        f"Requirements Brief v1.0", size=8, color=GREY)
    txt(s, Inches(12.3), Inches(7.13), Inches(0.6), Inches(0.25), str(n),
        size=8, color=GREY, align=PP_ALIGN.RIGHT)


# ==========================================================================
# SLIDE 1 - title
# ==========================================================================
s = slide()
band = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, Inches(4.35))
band.fill.solid()
band.fill.fore_color.rgb = NAVY
band.line.fill.background()
band.shadow.inherit = False
accent = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(4.35), W, Inches(0.09))
accent.fill.solid()
accent.fill.fore_color.rgb = CYAN
accent.line.fill.background()
accent.shadow.inherit = False

txt(s, Inches(0.9), Inches(1.15), Inches(11), Inches(0.3),
    C.DOC["company"].upper(), size=13, bold=True, color=CYAN)
txt(s, Inches(0.9), Inches(1.6), Inches(11.5), Inches(1.0),
    "Integrated MPS & MRP Planning Process", size=40, bold=True, color=WHITE)
txt(s, Inches(0.9), Inches(2.75), Inches(11.5), Inches(0.5),
    "From consensus forecast to purchase order:  process flow, system boundary "
    "and ownership model", size=16, color=rgb("A9C3DC"))
txt(s, Inches(0.9), Inches(3.5), Inches(11.5), Inches(0.4),
    "Editable process pack for IT Solution Delivery  |  Version 1.0  |  " + C.DOC["date"],
    size=11, color=rgb("7E9AB8"))

cards = [
    ("Slide 2", "End-to-end process flow", "Seven stages, six roles, two mandatory approval gates."),
    ("Slide 3", "System boundary and interfaces", "What EZ-Commerce calculates, what SAP executes, and the ten interfaces between them."),
    ("Slide 4", "Planning calendar and time fences", "12-month horizon, weekly tactical window, two-week frozen zone."),
    ("Slide 5", "RACI at a glance", "Who is accountable at every stage."),
    ("Slide 6", "What changes versus the vendor scope", "The gap between an upload portal and a planning system."),
]
x = Inches(0.9)
for i, (lab, title, sub) in enumerate(cards):
    cw = Inches(2.25)
    box(s, x, Inches(4.85), cw, Inches(1.75), "", LIGHTER, line=rgb("D6E1EE"))
    txt(s, x + Inches(0.15), Inches(5.0), cw - Inches(0.3), Inches(0.2), lab,
        size=8.5, bold=True, color=BLUE)
    txt(s, x + Inches(0.15), Inches(5.25), cw - Inches(0.3), Inches(0.55), title,
        size=11, bold=True, color=NAVY, spacing=0.95)
    txt(s, x + Inches(0.15), Inches(5.85), cw - Inches(0.3), Inches(0.7), sub,
        size=8.5, color=GREY, spacing=0.95)
    x += cw + Inches(0.15)
footer(s, 1)

# ==========================================================================
# SLIDE 2 - swimlane process flow
# ==========================================================================
s = slide()
header(s, "PROCESS FLOW", "From forecast to purchase order: seven stages, two gates",
       "MPS and MRP are a sequence with a human approval gate between them. They are not one automated event triggered by a single upload.")

LANES = [
    ("Demand Planner", LIGHTER),
    ("MPS / Production Planner", LIGHT),
    ("MRP / Material Planner", LIGHTER),
    ("Procurement Buyer", LIGHT),
]
LANE_X = Inches(0.4)
LANE_LBL_W = Inches(1.55)
LANE_Y0 = Inches(1.55)
LANE_H = Inches(1.02)
FLOW_X0 = LANE_X + LANE_LBL_W
FLOW_W = W - FLOW_X0 - Inches(0.4)

for i, (name, fill) in enumerate(LANES):
    y = LANE_Y0 + Emu(int(LANE_H * i))
    box(s, LANE_X, y, LANE_LBL_W, LANE_H, name, NAVY if i % 2 == 0 else rgb("1B2942"),
        size=9.5, bold=True, color=WHITE, shape=MSO_SHAPE.RECTANGLE, spacing=0.9)
    lane = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, FLOW_X0, y, FLOW_W, LANE_H)
    lane.fill.solid()
    lane.fill.fore_color.rgb = fill
    lane.line.color.rgb = rgb("DCE5EF")
    lane.line.width = Pt(0.75)
    lane.shadow.inherit = False

# gate badge strip, then the system bands
BADGE_Y = LANE_Y0 + Emu(int(LANE_H * 4)) + Inches(0.07)
SYS_Y = BADGE_Y + Inches(0.32)
NCOL = 7
COL_W = Emu(int((FLOW_W - Inches(0.15) * (NCOL - 1)) / NCOL))
GAP = Inches(0.15)


def col_x(i):
    return FLOW_X0 + Emu(int((COL_W + GAP) * i))


box(s, LANE_X, SYS_Y, LANE_LBL_W, Inches(0.38), "System", rgb("475569"),
    size=9.5, bold=True, color=WHITE, shape=MSO_SHAPE.RECTANGLE)
ez_w = Emu(int((COL_W + GAP) * 6 - GAP))
box(s, col_x(0), SYS_Y, ez_w, Inches(0.38),
    "EZ-COMMERCE  -  all calculation happens here", BLUE, size=10, bold=True,
    color=WHITE, shape=MSO_SHAPE.RECTANGLE)
box(s, col_x(6), SYS_Y, COL_W, Inches(0.38), "SAP S/4HANA", rgb("475569"),
    size=10, bold=True, color=WHITE, shape=MSO_SHAPE.RECTANGLE)

STEPS = [
    (0, 0, "S1", "Demand intake\n& validation",
     "Forecast loaded, validated,\nversioned and locked", None),
    (1, 1, "S2", "Unconstrained MPS",
     "12 months, monthly. Net\nrequirement vs stock norm", None),
    (2, 1, "S3", "Constrained\noptimization",
     "Weekly, 3-6 months. Capacity,\nchangeover, campaign, MOQ", None),
    (3, 1, "S4", "MPS review\n& approval",
     "Planner edits, overrides\nlogged, plan frozen", "gate"),
    (4, 2, "S5", "MRP explosion\n& netting",
     "BOM to RM/PM. Net vs stock,\nopen PO, in transit", None),
    (5, 2, "S6", "MRP confirmation",
     "Planner confirms. Nothing\nreaches SAP before this", "gate"),
    (6, 3, "S7", "Release, PR & PO",
     "PIR to SAP, PR created,\nbuyer converts to PO", None),
]

centres = []
for ci, lane_i, sid, title, sub, kind in STEPS:
    x = col_x(ci)
    y = LANE_Y0 + Emu(int(LANE_H * lane_i)) + Inches(0.07)
    h = LANE_H - Inches(0.14)
    fill = rgb("FFF7ED") if kind == "gate" else WHITE
    edge = AMBER if kind == "gate" else BLUE
    sh = box(s, x, y, COL_W, h, "", fill, line=edge, line_w=1.5)
    txt(s, x + Inches(0.06), y + Inches(0.04), Inches(0.5), Inches(0.16), sid,
        size=8, bold=True, color=edge)
    txt(s, x + Inches(0.05), y + Inches(0.2), COL_W - Inches(0.1), Inches(0.32),
        title, size=9.5, bold=True, color=NAVY, align=PP_ALIGN.CENTER, spacing=0.86)
    txt(s, x + Inches(0.05), y + Inches(0.54), COL_W - Inches(0.1), Inches(0.3),
        sub, size=7, color=GREY, align=PP_ALIGN.CENTER, spacing=0.86)
    centres.append((x, y, h))

for i in range(6):
    x1, y1, h1 = centres[i]
    x2, y2, h2 = centres[i + 1]
    arrow(s, x1 + COL_W, y1 + Emu(int(h1 / 2)), x2, y2 + Emu(int(h2 / 2)),
          AMBER if STEPS[i][5] == "gate" else BLUE, 2.0)

# Gate badges, tied back to their stage box by a dashed drop line.
for ci in (3, 5):
    gx, gy, gh = centres[ci]
    mid = gx + Emu(int(COL_W / 2))
    drop = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, mid, gy + gh, mid, BADGE_Y)
    drop.line.color.rgb = AMBER
    drop.line.width = Pt(1.0)
    drop.line._get_or_add_ln().append(
        parse_xml('<a:prstDash %s val="sysDash"/>' % nsdecls("a")))
    box(s, gx, BADGE_Y, COL_W, Inches(0.24), "MANDATORY APPROVAL GATE",
        AMBER, size=7, bold=True, color=WHITE, shape=MSO_SHAPE.RECTANGLE)

NOTE_Y = Inches(6.5)
notes = [
    ("The gates are the correction", "No MRP may run against an unapproved MPS. "
     "Nothing reaches SAP without MRP planner confirmation.", AMBER),
    ("Netting happens once", "EZ-Commerce nets against stock and open supply. "
     "SAP-side netting is neutralised (Decision D-01).", RED),
    ("SAP cannot do S3", "Standard SAP MPS and MRP plan at infinite capacity. "
     "Constraint resolution must sit in EZ-Commerce.", BLUE),
]
nx = Inches(0.4)
nw = Inches(4.13)
for title, body, colr in notes:
    box(s, nx, NOTE_Y, nw, Inches(0.58), "", LIGHTER, line=rgb("D6E1EE"))
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, nx, NOTE_Y, Inches(0.045), Inches(0.58))
    bar.fill.solid()
    bar.fill.fore_color.rgb = colr
    bar.line.fill.background()
    bar.shadow.inherit = False
    txt(s, nx + Inches(0.16), NOTE_Y + Inches(0.05), nw - Inches(0.3), Inches(0.19),
        title, size=9, bold=True, color=colr)
    txt(s, nx + Inches(0.16), NOTE_Y + Inches(0.25), nw - Inches(0.3), Inches(0.3),
        body, size=7.5, color=SLATE, spacing=0.9)
    nx += nw + Inches(0.15)
footer(s, 2)

# ==========================================================================
# SLIDE 3 - system boundary and interfaces
# ==========================================================================
s = slide()
header(s, "SYSTEM BOUNDARY", "EZ-Commerce is the planning brain. SAP is the execution system of record.",
       "The boundary is a single point: the confirmed net requirement. Everything that decides a number is to the left of it.")

PANEL_Y = Inches(1.6)
PANEL_H = Inches(3.55)
LW_ = Inches(4.9)
RW_ = Inches(4.9)
MIDW = Inches(2.6)
LX = Inches(0.4)
MX = LX + LW_ + Inches(0.25)
RX = MX + MIDW + Inches(0.25)

box(s, LX, PANEL_Y, LW_, Inches(0.45), "EZ-COMMERCE  (non-SAP planning engine)",
    BLUE, size=11.5, bold=True, color=WHITE, shape=MSO_SHAPE.RECTANGLE)
box(s, LX, PANEL_Y + Inches(0.45), LW_, PANEL_H - Inches(0.45), "", LIGHTER,
    line=rgb("D6E1EE"), shape=MSO_SHAPE.RECTANGLE)
left_items = [
    "Demand intake, validation, versioning, locking",
    "Stock norms and all planning parameters",
    "Unconstrained MPS heuristic  -  12 months, monthly",
    "Constrained optimization  -  weekly, 3 to 6 months",
    "Capacity, changeover, campaign and MOQ modelling",
    "MPS planner review, override and approval",
    "BOM explosion to raw and packing materials",
    "Netting vs stock, open PO and goods in transit",
    "Lot sizing and lead-time offsetting",
    "MRP planner review and confirmation",
    "Exception workbench and scenario comparison",
    "Reconciliation against SAP",
]
yy = PANEL_Y + Inches(0.58)
for it in left_items:
    dot = s.shapes.add_shape(MSO_SHAPE.OVAL, LX + Inches(0.18), yy + Inches(0.055),
                             Inches(0.07), Inches(0.07))
    dot.fill.solid()
    dot.fill.fore_color.rgb = BLUE
    dot.line.fill.background()
    dot.shadow.inherit = False
    txt(s, LX + Inches(0.34), yy, LW_ - Inches(0.5), Inches(0.22), it, size=9.5)
    yy += Inches(0.245)

box(s, RX, PANEL_Y, RW_, Inches(0.45), "SAP S/4HANA  (execution system of record)",
    rgb("475569"), size=11.5, bold=True, color=WHITE, shape=MSO_SHAPE.RECTANGLE)
box(s, RX, PANEL_Y + Inches(0.45), RW_, PANEL_H - Inches(0.45), "", LIGHTER,
    line=rgb("D6E1EE"), shape=MSO_SHAPE.RECTANGLE)
right_items = [
    "Material master, BOM, routing, work centre",
    "Purchasing info records and source lists",
    "Inventory, batch, expiry and quality status",
    "Receipt of Planned Independent Requirements",
    "MRP run under neutralised configuration (D-01)",
    "Purchase requisition creation, dedicated type",
    "Purchase order creation and management",
    "Goods receipt and inventory movement",
    "Production execution and confirmation",
    "Costing, valuation and financial record",
    "Supplier collaboration and invoice matching",
    "Execution feedback to EZ-Commerce",
]
yy = PANEL_Y + Inches(0.58)
for it in right_items:
    dot = s.shapes.add_shape(MSO_SHAPE.OVAL, RX + Inches(0.18), yy + Inches(0.055),
                             Inches(0.07), Inches(0.07))
    dot.fill.solid()
    dot.fill.fore_color.rgb = rgb("475569")
    dot.line.fill.background()
    dot.shadow.inherit = False
    txt(s, RX + Inches(0.34), yy, RW_ - Inches(0.5), Inches(0.22), it, size=9.5)
    yy += Inches(0.245)

box(s, MX, PANEL_Y + Inches(0.15), MIDW, Inches(0.32), "THE BOUNDARY",
    NAVY, size=9.5, bold=True, color=WHITE, shape=MSO_SHAPE.RECTANGLE)
box(s, MX, PANEL_Y + Inches(0.62), MIDW, Inches(0.95),
    "IF-08\nConfirmed NET requirement\nas Planned Independent\nRequirement",
    rgb("FFF7ED"), line=AMBER, size=9, bold=True, color=rgb("7C3F0B"), line_w=1.5,
    spacing=0.95)
arrow(s, MX + Inches(0.3), PANEL_Y + Inches(1.72), MX + MIDW - Inches(0.3),
      PANEL_Y + Inches(1.72), AMBER, 2.5)
box(s, MX, PANEL_Y + Inches(1.88), MIDW, Inches(0.8),
    "IF-01 to IF-07\nMaster data, inventory\nand open supply",
    LIGHT, line=rgb("B7CBE0"), size=9, color=SLATE, spacing=0.95)
arrow(s, MX + MIDW - Inches(0.3), PANEL_Y + Inches(2.82), MX + Inches(0.3),
      PANEL_Y + Inches(2.82), BLUE, 2.5)
box(s, MX, PANEL_Y + Inches(2.98), MIDW, Inches(0.5),
    "IF-10  Execution feedback", LIGHT, line=rgb("B7CBE0"), size=9, color=SLATE)

box(s, Inches(0.4), Inches(5.33), Inches(12.53), Inches(0.74), "",
    rgb("FDF2F4"), line=RED, line_w=1.25, shape=MSO_SHAPE.RECTANGLE)
txt(s, Inches(0.6), Inches(5.42), Inches(3.0), Inches(0.22),
    "DECISION D-01  |  Net once", size=10, bold=True, color=RED)
txt(s, Inches(0.6), Inches(5.65), Inches(12.1), Inches(0.4),
    "EZ-Commerce sends NET requirement. For in-scope materials SAP safety stock is set to zero, lot size to lot-for-lot (EX), "
    "no rounding and no coverage profile, so SAP does not net a second time. Daily reconciliation (C-05) and weekly "
    "configuration drift check (C-06) prove it stays that way.", size=9, color=SLATE)

txt(s, Inches(0.4), Inches(6.2), Inches(12.5), Inches(0.28),
    "What SAP is no longer asked to do", size=11.5, bold=True, color=NAVY)
nots = ["Stock availability check", "BOM explosion", "Netting against stock and open supply",
        "Capacity or constraint resolution", "Stock norm and lot-sizing decisions"]
nx = Inches(0.4)
for n in nots:
    bw = Inches(2.45)
    box(s, nx, Inches(6.53), bw, Inches(0.4), n, WHITE, line=rgb("D6C2C8"),
        size=9, color=rgb("8B2942"))
    nx += bw + Inches(0.07)
footer(s, 3)

# ==========================================================================
# SLIDE 4 - planning calendar and time fences
# ==========================================================================
s = slide()
header(s, "PLANNING CALENDAR", "Horizon, buckets and time fences",
       "The vendor scope leaves demand frequency as an open question for the business. It is a foundational design input and it is fixed here.")

TL_Y = Inches(1.85)
TL_X = Inches(0.5)
TL_W = Inches(12.33)
zones = [
    ("FROZEN", "Weeks 1-2", rgb("9F1239"), 0.12,
     "Locked to the approved plan.\nChange only by formal exception\nwith S&OP Manager approval."),
    ("FIRM", "Weeks 3-13  (current month + 3)", rgb("B45309"), 0.36,
     "Constrained optimization.\nRe-planned weekly, but change is\nmeasured for stability (control C-08)."),
    ("EXTENDED", "Months 4-6  (optional)", rgb("0369A1"), 0.18,
     "Constrained weekly buckets when\nthe extension is enabled, for long\nlead-time materials."),
    ("FREE", "Months 4-12", rgb("475569"), 0.34,
     "Unconstrained monthly heuristic.\nFully re-planned each cycle.\nNo change control."),
]
x = TL_X
for name, span, colr, frac, desc in zones:
    zw = Emu(int(TL_W * frac))
    box(s, x, TL_Y, zw - Inches(0.06), Inches(0.5), name, colr, size=12, bold=True,
        color=WHITE, shape=MSO_SHAPE.RECTANGLE)
    txt(s, x, TL_Y + Inches(0.56), zw - Inches(0.06), Inches(0.22), span,
        size=9.5, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
    txt(s, x, TL_Y + Inches(0.82), zw - Inches(0.06), Inches(0.7), desc,
        size=8.5, color=GREY, align=PP_ALIGN.CENTER, spacing=0.95)
    x += zw

axis = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, TL_X, TL_Y + Inches(1.62), TL_W, Inches(0.02))
axis.fill.solid()
axis.fill.fore_color.rgb = rgb("CBD5E1")
axis.line.fill.background()
axis.shadow.inherit = False
for lab, frac in [("Today", 0.0), ("Week 2", 0.12), ("Week 13", 0.48), ("Month 6", 0.66), ("Month 12", 1.0)]:
    px = TL_X + Emu(int(TL_W * frac))
    tick = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, px, TL_Y + Inches(1.55), Inches(0.02), Inches(0.16))
    tick.fill.solid()
    tick.fill.fore_color.rgb = rgb("94A3B8")
    tick.line.fill.background()
    tick.shadow.inherit = False
    txt(s, px - Inches(0.5), TL_Y + Inches(1.74), Inches(1.0), Inches(0.2), lab,
        size=8.5, color=GREY, align=PP_ALIGN.CENTER)

box(s, Inches(0.5), Inches(4.1), Inches(6.0), Inches(0.38), "BUCKET PROFILE",
    NAVY, size=10, bold=True, color=WHITE, shape=MSO_SHAPE.RECTANGLE)
rows = [
    ("Weeks 1-13", "Weekly", "Constrained optimization"),
    ("Months 4-6", "Weekly (optional)", "Constrained when extension enabled"),
    ("Months 4-12", "Monthly", "Unconstrained heuristic"),
]
yy = Inches(4.55)
for a, b, c_ in rows:
    box(s, Inches(0.5), yy, Inches(1.7), Inches(0.36), a, LIGHTER, line=rgb("D6E1EE"),
        size=9, color=NAVY)
    box(s, Inches(2.25), yy, Inches(1.6), Inches(0.36), b, WHITE, line=rgb("D6E1EE"), size=9)
    box(s, Inches(3.9), yy, Inches(2.6), Inches(0.36), c_, WHITE, line=rgb("D6E1EE"), size=9)
    yy += Inches(0.42)

box(s, Inches(6.83), Inches(4.1), Inches(6.0), Inches(0.38), "WEEKLY MPS CYCLE",
    NAVY, size=10, bold=True, color=WHITE, shape=MSO_SHAPE.RECTANGLE)
days = [
    ("MON", "Forecast locked\nSAP data synced", BLUE),
    ("TUE", "MPS runs\nOptimization runs", BLUE),
    ("WED", "Plan adjusted\nMPS APPROVED", AMBER),
    ("THU", "MRP runs\nMRP CONFIRMED", AMBER),
    ("FRI", "PIR to SAP\nPR and PO", rgb("475569")),
]
dx = Inches(6.83)
for d, body, colr in days:
    dw = Inches(1.15)
    box(s, dx, Inches(4.55), dw, Inches(0.3), d, colr, size=9, bold=True,
        color=WHITE, shape=MSO_SHAPE.RECTANGLE)
    box(s, dx, Inches(4.85), dw, Inches(0.62), body, WHITE, line=rgb("D6E1EE"),
        size=8, color=SLATE, spacing=0.92)
    dx += dw + Inches(0.06)

box(s, Inches(6.83), Inches(5.62), Inches(6.0), Inches(0.62), "", LIGHTER,
    line=rgb("D6E1EE"), shape=MSO_SHAPE.RECTANGLE)
txt(s, Inches(7.0), Inches(5.72), Inches(5.7), Inches(0.2),
    "Monthly S&OP sets the 12-month plan and resolves escalated shortfalls.",
    size=9, bold=True, color=NAVY)
txt(s, Inches(7.0), Inches(5.94), Inches(5.7), Inches(0.24),
    "MRP can refresh daily against live inventory without a new MPS approval.",
    size=9, color=GREY)

box(s, Inches(0.5), Inches(6.42), Inches(12.33), Inches(0.55), "",
    rgb("FFF7ED"), line=AMBER, line_w=1.25, shape=MSO_SHAPE.RECTANGLE)
txt(s, Inches(0.7), Inches(6.52), Inches(12.0), Inches(0.4),
    "Trade-off stated explicitly:  a two-week frozen zone buys demand responsiveness and costs procurement "
    "stability. Control C-08 measures change inside the firm horizon each week, so the cost of that choice is "
    "managed rather than absorbed silently.", size=9.5, color=rgb("7C3F0B"), spacing=1.0)
footer(s, 4)

# ==========================================================================
# SLIDE 5 - RACI at a glance
# ==========================================================================
s = slide()
header(s, "OWNERSHIP", "RACI at a glance",
       "R responsible, A accountable, C consulted, I informed. Exactly one accountable role per stage. The full step-level matrix is in the accompanying Excel register.")

STAGE_RACI = [
    ("S1", "Demand intake and forecast lock", {"DP": "R", "SOP": "A", "MPS": "C", "MRP": "I", "BUY": "", "OPS": "", "MDS": "C", "IT": "C"}),
    ("S2", "Unconstrained MPS, 12 months", {"DP": "I", "SOP": "I", "MPS": "A/R", "MRP": "I", "BUY": "", "OPS": "C", "MDS": "", "IT": "C"}),
    ("S3", "Constrained optimization", {"DP": "", "SOP": "I", "MPS": "A/R", "MRP": "C", "BUY": "C", "OPS": "C", "MDS": "", "IT": "C"}),
    ("S4", "MPS review and approval  (GATE)", {"DP": "I", "SOP": "C", "MPS": "A/R", "MRP": "I", "BUY": "I", "OPS": "C", "MDS": "", "IT": "I"}),
    ("S5", "MRP explosion and netting", {"DP": "", "SOP": "I", "MPS": "C", "MRP": "A/R", "BUY": "C", "OPS": "", "MDS": "C", "IT": "C"}),
    ("S6", "MRP confirmation  (GATE)", {"DP": "", "SOP": "I", "MPS": "I", "MRP": "A/R", "BUY": "C", "OPS": "", "MDS": "", "IT": "I"}),
    ("S7", "Release to SAP, PR and PO", {"DP": "", "SOP": "I", "MPS": "I", "MRP": "R", "BUY": "R", "OPS": "", "MDS": "C", "IT": "A"}),
]
tx, ty = Inches(0.4), Inches(1.72)
tw = Inches(12.53)
rows_n = len(STAGE_RACI) + 1
gtbl = s.shapes.add_table(rows_n, 10, tx, ty, tw, Inches(3.1)).table
gtbl.columns[0].width = Inches(0.6)
gtbl.columns[1].width = Inches(3.53)
for i in range(2, 10):
    gtbl.columns[i].width = Inches(1.05)
gtbl.rows[0].height = Inches(0.55)
for i in range(1, rows_n):
    gtbl.rows[i].height = Inches(0.36)

hdr = ["", "Process stage"] + [r[0] for r in C.ROLES]
for j, h in enumerate(hdr):
    cell = gtbl.cell(0, j)
    cell.text = ""
    cell.fill.solid()
    cell.fill.fore_color.rgb = NAVY
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = cell.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT if j == 1 else PP_ALIGN.CENTER
    r = p.add_run()
    r.text = h
    r.font.size = Pt(10)
    r.font.bold = True
    r.font.color.rgb = WHITE
    r.font.name = "Arial"

for i, (sid, name, assign) in enumerate(STAGE_RACI, start=1):
    gate = "GATE" in name
    vals = [sid, name] + [assign.get(rc, "") for rc in C.ROLE_CODES]
    for j, v in enumerate(vals):
        cell = gtbl.cell(i, j)
        cell.text = ""
        cell.fill.solid()
        if gate:
            cell.fill.fore_color.rgb = rgb("FFF7ED")
        else:
            cell.fill.fore_color.rgb = WHITE if i % 2 else LIGHTER
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.margin_left = cell.margin_right = Inches(0.06)
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT if j == 1 else PP_ALIGN.CENTER
        r = p.add_run()
        r.text = v
        r.font.size = Pt(10 if j < 2 else 10)
        r.font.name = "Arial"
        if j == 0:
            r.font.bold = True
            r.font.color.rgb = AMBER if gate else BLUE
        elif j == 1:
            r.font.bold = gate
            r.font.color.rgb = rgb("7C3F0B") if gate else SLATE
        else:
            r.font.bold = v.startswith("A")
            r.font.color.rgb = (RED if v.startswith("A") else
                                (BLUE if v == "R" else GREY))

ry = Inches(5.16)
txt(s, Inches(0.4), ry, Inches(12.5), Inches(0.25), "The eight roles",
    size=12, bold=True, color=NAVY)
rx = Inches(0.4)
for code, name, desc in C.ROLES:
    bw = Inches(1.53)
    box(s, rx, ry + Inches(0.32), bw, Inches(0.34), code, BLUE, size=10, bold=True,
        color=WHITE, shape=MSO_SHAPE.RECTANGLE)
    txt(s, rx + Inches(0.02), ry + Inches(0.7), bw - Inches(0.04), Inches(0.42),
        name, size=8.5, bold=True, color=NAVY, align=PP_ALIGN.CENTER, spacing=0.9)
    rx += bw + Inches(0.08)

box(s, Inches(0.4), Inches(6.42), Inches(12.53), Inches(0.55), "",
    rgb("ECFDF3"), line=GREEN, line_w=1.25, shape=MSO_SHAPE.RECTANGLE)
txt(s, Inches(0.6), Inches(6.52), Inches(12.1), Inches(0.4),
    "The vendor scope document has no RACI and no role definitions at all - ownership is expressed only as a "
    "'System Responsible' column. Systems do not own decisions, people do. Without named accountability the two "
    "approval gates cannot be enforced and exceptions have no owner.", size=9.5, color=rgb("14532D"))
footer(s, 5)

# ==========================================================================
# SLIDE 6 - before / after
# ==========================================================================
s = slide()
header(s, "GAP ANALYSIS", "What changes versus the vendor scope document",
       "Vendor scope v1.0 (SCOPE-MARICO-EZ-SAP-v1.0) specifies a competent upload-and-trigger integration. It is not a specification for a planning system.")

box(s, Inches(0.4), Inches(1.7), Inches(6.15), Inches(0.45),
    "VENDOR SCOPE v1.0  -  what is specified today", rgb("8B2942"), size=11.5,
    bold=True, color=WHITE, shape=MSO_SHAPE.RECTANGLE)
box(s, Inches(6.78), Inches(1.7), Inches(6.15), Inches(0.45),
    "REQUIRED  -  what the business needs", GREEN, size=11.5, bold=True,
    color=WHITE, shape=MSO_SHAPE.RECTANGLE)

pairs = [
    ("Upload screen, duplicate check, BAPI connectors, results dashboard, error log.",
     "A planning engine: MPS heuristic, constrained optimizer, netting, exception workbench."),
    ("MPS and MRP triggered together from one upload.",
     "A sequence: MPS, approval gate, MRP, confirmation gate, then release."),
    ("MPS described in a single line, no logic, no horizon, no buckets.",
     "Full MPS specification: 12-month monthly heuristic, net requirement formula, stock norms."),
    ("No optimizer. No capacity, changeover, campaign, MOQ or objective function.",
     "Mixed-integer optimizer, weekly 3-6 months, lexicographic objective: service then cost."),
    ("SAP expected to honour supply constraints.",
     "SAP plans at infinite capacity and cannot. All constraint resolution sits in EZ-Commerce."),
    ("SAP performs stock check, BOM explosion and netting.",
     "EZ-Commerce nets once. SAP-side netting neutralised under Decision D-01."),
    ("Safety stock listed as 'if applicable', held in SAP.",
     "Stock norms and all planning parameters owned in EZ-Commerce under change control."),
    ("Demand frequency left open: 'Daily / Weekly / Monthly'.",
     "Fixed: monthly across 12 months, weekly for the current month plus three."),
    ("No time fences, no frozen period.",
     "Two-week frozen zone, measured firm zone, defined change authority in each."),
    ("No approval gates anywhere in the flow.",
     "Two mandatory gates with override audit and reason codes."),
    ("No RACI, no role definitions, no process flow diagram.",
     "Eight-role RACI across 29 steps, plus this process pack."),
    ("No NFRs, volumes, run times, controls, test scenarios or phasing.",
     "63 numbered requirements, 14 NFRs, 8 controls, 16 UAT scenarios, 6-phase roadmap."),
]
yy = Inches(2.22)
rowh = Inches(0.338)
for i, (before, after) in enumerate(pairs):
    fill = WHITE if i % 2 == 0 else LIGHTER
    box(s, Inches(0.4), yy, Inches(6.15), rowh - Inches(0.025), before, fill,
        line=rgb("E4D2D7"), size=8.5, color=SLATE, align=PP_ALIGN.LEFT,
        shape=MSO_SHAPE.RECTANGLE)
    box(s, Inches(6.78), yy, Inches(6.15), rowh - Inches(0.025), after, fill,
        line=rgb("CFE6D8"), size=8.5, color=SLATE, align=PP_ALIGN.LEFT,
        shape=MSO_SHAPE.RECTANGLE)
    tri = s.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE, Inches(6.6), yy + Inches(0.09),
                             Inches(0.14), Inches(0.16))
    tri.rotation = 90
    tri.fill.solid()
    tri.fill.fore_color.rgb = GREEN
    tri.line.fill.background()
    tri.shadow.inherit = False
    yy += rowh

box(s, Inches(0.4), Inches(6.4), Inches(12.53), Inches(0.6), "",
    rgb("FEF3E2"), line=AMBER, line_w=1.25, shape=MSO_SHAPE.RECTANGLE)
txt(s, Inches(0.6), Inches(6.5), Inches(12.1), Inches(0.42),
    "Four of the fifteen gaps change cost and timeline materially:  G-02 and G-04 (the MPS logic and the optimizer "
    "are unspecified, therefore unpriced),  G-03 (SAP cannot perform constrained planning),  G-08 (netting assigned "
    "to SAP creates the double-netting defect).  Re-baseline scope and commercials before build.",
    size=9.5, color=rgb("7C3F0B"))
footer(s, 6)

prs.save(os.path.abspath(OUT))
print("Wrote", os.path.abspath(OUT), "-", len(prs.slides.__iter__.__self__._sldIdLst), "slides")
