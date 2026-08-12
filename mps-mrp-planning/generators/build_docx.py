# -*- coding: utf-8 -*-
"""Build the MPS/MRP Business Requirements Brief as a .docx."""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

import content as C

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "Marico_MPS_MRP_Business_Requirements_Brief_v1.0.docx")

A4_W, A4_H = Cm(21.0), Cm(29.7)
MARGIN = Cm(2.0)
PW = Cm(17.0)     # portrait content width
LW = Cm(25.7)     # landscape content width


# --------------------------------------------------------------------------
# low level helpers
# --------------------------------------------------------------------------
def rgb(h):
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# WordprocessingML enforces child element order inside property containers.
# Appending blindly produces a file Word and LibreOffice both refuse to open,
# so every property element is inserted at its schema position.
PPR_ORDER = [
    "w:pStyle", "w:keepNext", "w:keepLines", "w:pageBreakBefore", "w:framePr",
    "w:widowControl", "w:numPr", "w:suppressLineNumbers", "w:pBdr", "w:shd",
    "w:tabs", "w:suppressAutoHyphens", "w:kinsoku", "w:wordWrap",
    "w:overflowPunct", "w:topLinePunct", "w:autoSpaceDE", "w:autoSpaceDN",
    "w:bidi", "w:adjustRightInd", "w:snapToGrid", "w:spacing", "w:ind",
    "w:contextualSpacing", "w:mirrorIndents", "w:suppressOverlap", "w:jc",
    "w:textDirection", "w:textAlignment", "w:textboxTightWrap", "w:outlineLvl",
    "w:divId", "w:cnfStyle", "w:rPr", "w:sectPr", "w:pPrChange",
]
TBLPR_ORDER = [
    "w:tblStyle", "w:tblpPr", "w:tblOverlap", "w:bidiVisual",
    "w:tblStyleRowBandSize", "w:tblStyleColBandSize", "w:tblW", "w:jc",
    "w:tblCellSpacing", "w:tblInd", "w:tblBorders", "w:shd", "w:tblLayout",
    "w:tblCellMar", "w:tblLook", "w:tblCaption", "w:tblDescription",
    "w:tblPrChange",
]
TCPR_ORDER = [
    "w:cnfStyle", "w:tcW", "w:gridSpan", "w:hMerge", "w:vMerge", "w:tcBorders",
    "w:shd", "w:noWrap", "w:tcMar", "w:textDirection", "w:tcFitText",
    "w:vAlign", "w:hideMark", "w:headers", "w:cellIns", "w:cellDel",
    "w:cellMerge", "w:tcPrChange",
]
TRPR_ORDER = [
    "w:cnfStyle", "w:divId", "w:gridBefore", "w:gridAfter", "w:wBefore",
    "w:wAfter", "w:cantSplit", "w:trHeight", "w:tblHeader", "w:tblCellSpacing",
    "w:jc", "w:hidden", "w:ins", "w:del", "w:trPrChange",
]


def put(parent, el, order):
    """Insert el into parent at its schema-mandated position, replacing any
    existing element of the same tag."""
    name = el.tag
    qnames = [qn(o) for o in order]
    idx = qnames.index(name)
    for existing in parent.findall(name):
        parent.remove(existing)
    for successor in qnames[idx + 1:]:
        found = parent.find(successor)
        if found is not None:
            found.addprevious(el)
            return el
    parent.append(el)
    return el


def shade(cell, fill):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    put(cell._tc.get_or_add_tcPr(), shd, TCPR_ORDER)


def cell_margins(cell, top=60, bottom=60, left=90, right=90):
    mar = OxmlElement("w:tcMar")
    for tag, val in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        el = OxmlElement("w:" + tag)
        el.set(qn("w:w"), str(val))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    put(cell._tc.get_or_add_tcPr(), mar, TCPR_ORDER)


def repeat_header(row):
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    put(row._tr.get_or_add_trPr(), el, TRPR_ORDER)


def no_split(row):
    put(row._tr.get_or_add_trPr(), OxmlElement("w:cantSplit"), TRPR_ORDER)


def set_borders(table, color="C9D4E2", sz=4):
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement("w:" + edge)
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(sz))
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color)
        borders.append(el)
    put(table._tbl.tblPr, borders, TBLPR_ORDER)


def para_shading(p, fill):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), fill)
    put(p._p.get_or_add_pPr(), shd, PPR_ORDER)


def para_border(p, color=C.BLUE, size=6, edges=("left",)):
    bdr = OxmlElement("w:pBdr")
    for e in ("top", "left", "bottom", "right"):
        if e in edges:
            el = OxmlElement("w:" + e)
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), str(size))
            el.set(qn("w:space"), "8")
            el.set(qn("w:color"), color)
            bdr.append(el)
    put(p._p.get_or_add_pPr(), bdr, PPR_ORDER)


def write_cell(cell, text, bold=False, size=8.5, color=C.SLATE, align=None,
               italic=False, fill=None):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    if align:
        p.alignment = align
    lines = text.split("\n") if isinstance(text, str) else [str(text)]
    for i, line in enumerate(lines):
        if i:
            p = cell.add_paragraph()
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            if align:
                p.alignment = align
        r = p.add_run(line)
        r.bold = bold
        r.italic = italic
        r.font.size = Pt(size)
        r.font.color.rgb = rgb(color)
        r.font.name = "Arial"
    if fill:
        shade(cell, fill)
    cell_margins(cell)


# --------------------------------------------------------------------------
# document level helpers
# --------------------------------------------------------------------------
class Doc:
    def __init__(self):
        self.d = Document()
        self._styles()
        s = self.d.sections[0]
        s.page_width, s.page_height = A4_W, A4_H
        s.left_margin = s.right_margin = MARGIN
        s.top_margin = Cm(1.8)
        s.bottom_margin = Cm(1.8)
        self.width = PW
        self._footer(s)

    def _styles(self):
        st = self.d.styles["Normal"]
        st.font.name = "Arial"
        st.font.size = Pt(9.5)
        st.font.color.rgb = rgb(C.SLATE)
        st.paragraph_format.space_after = Pt(6)
        st.paragraph_format.line_spacing = 1.12
        rpr = st.element.get_or_add_rPr()
        rf = rpr.get_or_add_rFonts()
        rf.set(qn("w:eastAsia"), "Arial")
        for name, size, color, before, after in (
            ("Heading 1", 16, C.NAVY, 20, 8),
            ("Heading 2", 12.5, C.BLUE, 14, 5),
            ("Heading 3", 10.5, C.SLATE, 11, 4),
        ):
            s = self.d.styles[name]
            s.font.name = "Arial"
            s.font.size = Pt(size)
            s.font.bold = True
            s.font.color.rgb = rgb(color)
            s.paragraph_format.space_before = Pt(before)
            s.paragraph_format.space_after = Pt(after)
            s.paragraph_format.keep_with_next = True

    def _footer(self, section):
        f = section.footer
        p = f.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(f"{C.DOC['doc_id']}   |   {C.DOC['company']}   |   Page ")
        r.font.size = Pt(7.5)
        r.font.color.rgb = rgb(C.GREY)
        r.font.name = "Arial"
        fld = OxmlElement("w:fldSimple")
        fld.set(qn("w:instr"), "PAGE")
        fr = OxmlElement("w:r")
        ft = OxmlElement("w:t")
        ft.text = "1"
        fr.append(ft)
        fld.append(fr)
        p._p.append(fld)

    # ---- structure -------------------------------------------------------
    def section(self, landscape=False):
        s = self.d.add_section(WD_SECTION.NEW_PAGE)
        if landscape:
            s.orientation = WD_ORIENT.LANDSCAPE
            s.page_width, s.page_height = A4_H, A4_W
            self.width = LW
        else:
            s.orientation = WD_ORIENT.PORTRAIT
            s.page_width, s.page_height = A4_W, A4_H
            self.width = PW
        s.left_margin = s.right_margin = MARGIN
        s.top_margin = Cm(1.8)
        s.bottom_margin = Cm(1.8)
        return s

    def h1(self, text):
        p = self.d.add_paragraph(text, style="Heading 1")
        para_border(p, C.CYAN, 12, ("bottom",))
        return p

    def h2(self, text):
        return self.d.add_paragraph(text, style="Heading 2")

    def h3(self, text):
        return self.d.add_paragraph(text, style="Heading 3")

    def p(self, text, size=9.5, bold=False, italic=False, color=C.SLATE,
          space_after=6, align=None):
        p = self.d.add_paragraph()
        p.paragraph_format.space_after = Pt(space_after)
        if align:
            p.alignment = align
        r = p.add_run(text)
        r.bold = bold
        r.italic = italic
        r.font.size = Pt(size)
        r.font.color.rgb = rgb(color)
        r.font.name = "Arial"
        return p

    def bullet(self, text, level=0, bold_lead=None):
        p = self.d.add_paragraph(style="List Bullet")
        p.paragraph_format.left_indent = Cm(0.6 + 0.5 * level)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.1
        if bold_lead:
            r = p.add_run(bold_lead)
            r.bold = True
            r.font.size = Pt(9.5)
            r.font.name = "Arial"
            r.font.color.rgb = rgb(C.SLATE)
        r = p.add_run(text)
        r.font.size = Pt(9.5)
        r.font.name = "Arial"
        r.font.color.rgb = rgb(C.SLATE)
        return p

    def callout(self, title, body, fill=C.LIGHT, accent=C.BLUE):
        t = self.d.add_table(rows=1, cols=1)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        c = t.cell(0, 0)
        c.width = self.width
        c.text = ""
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(title)
        r.bold = True
        r.font.size = Pt(9.5)
        r.font.name = "Arial"
        r.font.color.rgb = rgb(accent)
        p2 = c.add_paragraph()
        p2.paragraph_format.space_after = Pt(0)
        r2 = p2.add_run(body)
        r2.font.size = Pt(9)
        r2.font.name = "Arial"
        r2.font.color.rgb = rgb(C.SLATE)
        shade(c, fill)
        cell_margins(c, 120, 120, 160, 160)
        set_borders(t, accent, 4)
        self.d.add_paragraph().paragraph_format.space_after = Pt(4)
        return t

    def table(self, headers, rows, widths, size=8.5, header_fill=C.NAVY,
              zebra=True, aligns=None, bold_col0=False):
        total = sum(widths)
        widths = [Emu(int(self.width * (w / total))) for w in widths]
        t = self.d.add_table(rows=1, cols=len(headers))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        set_borders(t)
        # The grid columns, not the cell widths, drive layout under a fixed
        # table layout, so both have to be set.
        for i, col in enumerate(t.columns):
            col.width = widths[i]
        for i, h in enumerate(headers):
            c = t.cell(0, i)
            c.width = widths[i]
            write_cell(c, h, bold=True, size=size, color="FFFFFF", fill=header_fill,
                       align=(aligns[i] if aligns else None))
        repeat_header(t.rows[0])
        for ri, row in enumerate(rows):
            cells = t.add_row().cells
            no_split(t.rows[-1])
            fill = (C.LIGHTER if (zebra and ri % 2 == 1) else None)
            for i, val in enumerate(row):
                c = cells[i]
                c.width = widths[i]
                write_cell(c, "" if val is None else str(val), size=size,
                           bold=(bold_col0 and i == 0), fill=fill,
                           align=(aligns[i] if aligns else None))
        for r in t.rows:
            for i, c in enumerate(r.cells):
                c.width = widths[i]
        self.d.add_paragraph().paragraph_format.space_after = Pt(2)
        return t

    def caption(self, text):
        p = self.d.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(10)
        r = p.add_run(text)
        r.italic = True
        r.font.size = Pt(8)
        r.font.color.rgb = rgb(C.GREY)
        r.font.name = "Arial"
        return p

    def pagebreak(self):
        self.d.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    def toc(self):
        p = self.d.add_paragraph()
        fld = OxmlElement("w:fldSimple")
        fld.set(qn("w:instr"), 'TOC \\o "1-2" \\h \\z \\u')
        run = OxmlElement("w:r")
        t = OxmlElement("w:t")
        t.text = "Right-click and select Update Field to build the table of contents."
        run.append(t)
        fld.append(run)
        p._p.append(fld)


CEN = WD_ALIGN_PARAGRAPH.CENTER

# ==========================================================================
D = Doc()
d = D.d

# ---- COVER ---------------------------------------------------------------
for _ in range(2):
    D.d.add_paragraph()
p = D.p(C.DOC["company"].upper(), size=11, bold=True, color=C.BLUE, space_after=2)
p = D.d.add_paragraph()
r = p.add_run(C.DOC["title"])
r.bold = True
r.font.size = Pt(28)
r.font.name = "Arial"
r.font.color.rgb = rgb(C.NAVY)
p.paragraph_format.space_after = Pt(2)
p = D.d.add_paragraph()
r = p.add_run(C.DOC["subtitle"])
r.font.size = Pt(15)
r.font.name = "Arial"
r.font.color.rgb = rgb(C.BLUE)
p.paragraph_format.space_after = Pt(14)
para_border(p, C.CYAN, 18, ("bottom",))

D.d.add_paragraph()
D.p("Prepared by Supply Chain Planning for IT Solution Delivery and the vendor delivery team. "
    "This document defines the target planning process, the calculation logic, the system boundary "
    "and the ownership model for the integrated Master Production Scheduling and Material "
    "Requirements Planning capability.", size=10.5)

D.d.add_paragraph()
D.table(
    ["Field", "Detail"],
    [
        ["Document ID", C.DOC["doc_id"]],
        ["Version", C.DOC["version"] + "  (" + C.DOC["status"] + ")"],
        ["Date", C.DOC["date"]],
        ["Business owner", C.DOC["owner"]],
        ["Audience", C.DOC["audience"]],
        ["Responds to", C.DOC["responds_to"]],
        ["Planning system", C.DOC["planning_system"] + "  (non-SAP)"],
        ["ERP", C.DOC["erp"]],
        ["Scope boundary", "Single plant. Single-level BOM, finished goods to raw and packing materials. "
                           "300-800 finished goods, 1,500-4,000 raw and packing materials."],
        ["Status of this document", "Supersedes the vendor scope document as the statement of business requirement. "
                                    "Annex A lists the specific corrections required."],
    ],
    [22, 78], size=9)

D.pagebreak()
D.h1("Contents")
D.toc()

# ==========================================================================
D.pagebreak()
D.h1("1.  Executive summary")

D.p("Marico is building a planning engine outside SAP that will take the consensus forecast, "
    "produce a feasible master production schedule, explode it into material requirements, and "
    "release those requirements into SAP S/4HANA for procurement execution. This document "
    "specifies what that engine must do, who owns each decision, and exactly where the boundary "
    "with SAP sits.")

D.h2("1.1  The architecture in one sentence")
D.callout(
    "EZ-Commerce is the planning brain. SAP S/4HANA is the execution system of record.",
    "Every quantitative planning decision - netting, stock norms, lot sizing, capacity resolution, "
    "BOM explosion - is calculated once, in EZ-Commerce. SAP receives an already-final requirement, "
    "converts it into a purchase requisition, and manages the purchase order, the goods receipt and "
    "the financial record. SAP performs no planning arithmetic for in-scope materials.",
    C.LIGHT, C.BLUE)

D.h2("1.2  Three non-negotiable design points")
D.p("These three points are the difference between a planning system and an upload portal. Each of "
    "them is either absent from or contradicted by the current vendor scope document.")

D.table(
    ["#", "Design point", "Why it is non-negotiable"],
    [
        ["1", "MPS and MRP are a sequence with a human gate between them, not one automated event.",
         "The Production Planner must confirm the finished goods plan before any material requirement "
         "is calculated from it. Running both together removes the planner's control of the plan, which "
         "is the entire purpose of master scheduling. The vendor scope triggers both from a single upload."],
        ["2", "Constrained planning must happen in EZ-Commerce, because standard SAP cannot do it.",
         "SAP MPS and MRP plan at infinite capacity. They cannot honour line capacity, changeover, "
         "campaign rules or supplier allocation. Any design that expects SAP to resolve supply "
         "constraints will fail in testing, late and expensively."],
        ["3", "Requirements are netted exactly once.",
         "If EZ-Commerce nets against stock and open orders and SAP then nets the same requirement "
         "against the same stock and the same open orders, the business systematically under-orders. "
         "The plan looks correct in both systems and the shortage appears only on the line. "
         "Decision D-01 in section 12 closes this."],
    ],
    [4, 30, 66], size=9)

D.h2("1.3  What this means for the current vendor scope")
D.p("The vendor scope document specifies an upload-and-trigger portal: an upload screen, a duplicate "
    "check, connectors that call SAP, a results dashboard and an error log. Every planning decision in "
    "it sits inside SAP. That is the opposite of the agreed architecture, and it leaves the two "
    "components that carry the business value - the master scheduling logic and the constrained "
    "optimizer - entirely unspecified, and therefore unestimated and unpriced.")
D.p("Annex A sets out fifteen specific corrections. The four that change cost and timeline most are:")
D.bullet("the MPS calculation is described in one line and has no specification at all;", bold_lead="G-02  ")
D.bullet("there is no optimizer of any kind - no capacity model, no changeover matrix, no campaign "
         "rules, no lot-sizing economics, no objective function;", bold_lead="G-04  ")
D.bullet("SAP is expected to perform constrained planning, which it cannot do;", bold_lead="G-03  ")
D.bullet("there are no approval gates anywhere in the flow, so requirements would reach SAP and "
         "procurement commitments would begin with no named person accountable for them.", bold_lead="G-07  ")

D.h2("1.4  Decisions requested")
D.table(
    ["Ref", "Decision", "Status", "Impact if not closed"],
    [
        ["D-01", "Send net requirement and neutralise SAP-side netting, with a daily reconciliation control.",
         "Decided", "Systematic under-ordering across the entire material portfolio."],
        ["D-02", "How the approved finished goods plan reaches SAP so that production orders can be created.",
         "Open - workshop", "Interface IF-09 cannot be specified or built. Does not block phase 1."],
        ["D-03", "SAP owns engineering and logistics master data; EZ-Commerce owns all planning parameters.",
         "Decided", "Two systems produce different answers; planner confidence collapses."],
        ["D-04", "Excel forecast intake in phase 1, built behind an abstract interface for a later system feed.",
         "Decided", "The later migration to a demand planning system becomes a second project."],
        ["D-05", "Single BOM level in phase 1; semi-finished planning explicitly deferred to phase 2.",
         "Decided", "Live change-request risk in both directions against the vendor."],
    ],
    [6, 44, 14, 36], size=8.5)

D.h2("1.5  What is being asked of IT")
D.bullet("Treat this document, and the numbered requirement register in section 15, as the statement "
         "of business requirement. Re-baseline the vendor scope and commercials against it.")
D.bullet("Close Decision D-02 in a design workshop before interface IF-09 is specified.")
D.bullet("Implement the SAP-side configuration for Decision D-01 exactly as set out in section 12, "
         "including the dedicated requirement type and purchase requisition document type.")
D.bullet("Benchmark the optimizer at full portfolio volume during build, not at user acceptance "
         "testing. Run time is a functional constraint here: an optimizer that does not finish inside "
         "the weekly planning window is unusable regardless of how correct it is.")

# ==========================================================================
D.pagebreak()
D.h1("2.  How to read this document")
D.p("The document is written for several audiences at once. This table indicates the shortest useful "
    "path through it for each.")
D.table(
    ["Reader", "Read first", "Purpose"],
    [
        ["Solution architect", "Sections 6, 9, 11, 12", "System boundary, calculation logic, interfaces and the two architectural decisions."],
        ["Developer / build team", "Sections 9, 15, 16, 17", "Algorithms to implement, numbered requirements to build, performance targets and acceptance tests."],
        ["Integration engineer", "Sections 11, 12, 14", "Interface register, the D-01 guardrail and the reconciliation controls."],
        ["SAP functional consultant", "Sections 6, 12, Annex B", "What SAP must and must not do, the required configuration, and correct terminology."],
        ["Project manager / vendor", "Sections 5, 15, 18, Annex A", "Scope boundary, requirement register, phasing and the corrections required to the current scope."],
        ["Supply chain leadership", "Sections 1, 3, 7, 13", "The argument, the value case, the operating rhythm and the ownership model."],
        ["Planners (end users)", "Sections 7, 8, 13", "The target operating process, the approval gates and their own accountabilities."],
    ],
    [20, 20, 60], size=9)

# ==========================================================================
D.pagebreak()
D.h1("3.  Business objective and value case")
D.h2("3.1  Objective")
D.p("Convert a commercial forecast into an executable production plan and a reliable material supply "
    "plan, systematically and repeatably, with the calculation performed outside SAP and the execution "
    "performed inside it.")
D.p("Today the chain from forecast to purchase order depends on spreadsheets and individual judgement. "
    "That has three consequences: the plan is not reproducible, constraint resolution happens in "
    "someone's head rather than in a model, and there is no audit trail explaining why a quantity was "
    "ordered. The target system removes all three.")

D.h2("3.2  Where the value comes from")
D.table(
    ["Value driver", "Mechanism", "Indicative measure"],
    [
        ["Customer service", "Constrained optimization protects service first, before cost, and makes "
                             "unmet demand explicit and quantified rather than discovered late.",
         "Case fill rate; unmet demand quantified per cycle"],
        ["Finished goods inventory", "Stock norms applied consistently by rule rather than by planner "
                                     "habit, with projected coverage visible across the full horizon.",
         "Days of cover versus norm, by SKU class"],
        ["Material availability", "Netting against live stock, open purchase orders and goods in transit, "
                                  "with lead-time offset applied correctly and shortage exceptions raised inside lead time.",
         "Line stoppages attributable to material; expediting cost"],
        ["Manufacturing efficiency", "Campaign grouping and a real changeover matrix in the objective "
                                     "function, so sequencing is decided economically rather than by convention.",
         "Changeover hours as a share of available capacity"],
        ["Working capital", "Lot-sizing and MOQ economics applied explicitly, with MOQ-driven excess "
                            "coverage reported as an exception instead of absorbed silently.",
         "Raw and packing material days of cover; slow-moving value"],
        ["Planner productivity", "Exception-based working. The planner reviews what is wrong, not the "
                                 "entire plan line by line.",
         "Planning cycle time; proportion of plan touched manually"],
        ["Plan stability", "A two-week frozen zone and measured change inside the firm horizon.",
         "Change to the firm horizon between consecutive approved versions"],
    ],
    [20, 52, 28], size=8.5)

D.h2("3.3  Success measures for the system itself")
D.bullet("MPS attainment: approved plan versus actual production confirmed in SAP.")
D.bullet("Plan stability: the proportion of the firm horizon that changes between consecutive approved versions.")
D.bullet("Release integrity: zero unexplained variance between requirement released from EZ-Commerce "
         "and requirement present in SAP, measured daily by control C-05.")
D.bullet("Cycle time: the weekly planning cycle completed inside the published planning calendar, every week.")
D.bullet("Exception load: the number of exceptions a planner must clear per cycle, trending down as "
         "parameters mature.")

# ==========================================================================
D.pagebreak()
D.h1("4.  Design principles")
D.p("Seven principles govern every design decision that follows. Where a detailed requirement appears "
    "to conflict with a principle, the principle wins and the requirement is wrong.")
D.table(
    ["#", "Principle", "What it means in practice"],
    [
        ["P1", "One planning brain",
         "All quantitative calculation happens in EZ-Commerce. No planning arithmetic is duplicated in SAP. "
         "There is one place to look when a number is questioned."],
        ["P2", "SAP is the execution system of record",
         "SAP owns the transactional and financial truth: requirements received, purchase requisitions, "
         "purchase orders, goods receipts, inventory and cost. Planning proposes; SAP records."],
        ["P3", "Sequence, not simultaneity",
         "MPS runs, a planner approves, then MRP runs, then a planner confirms, then release happens. "
         "Each stage has a defined input state and a defined exit condition."],
        ["P4", "The system proposes, the planner disposes",
         "Every calculated output is a proposal until a named person approves it. Every override is "
         "captured with user, timestamp, before and after values, and a mandatory reason code."],
        ["P5", "Net once",
         "Stock, open purchase orders and goods in transit are deducted exactly one time, in EZ-Commerce. "
         "SAP-side netting is neutralised and the neutralisation is monitored."],
        ["P6", "Constrain where it matters",
         "Infinite capacity across the 12-month horizon for visibility; finite capacity, changeover, "
         "campaign and MOQ constraints inside the tactical window where the plan must be executable."],
        ["P7", "Build phase 1 so phase 2 is an extension",
         "Single BOM level and single plant now, but a level-agnostic and plant-agnostic data model, so "
         "semi-finished planning and network deployment are additions rather than rebuilds."],
    ],
    [5, 26, 69], size=9)

# ==========================================================================
D.pagebreak()
D.h1("5.  Scope")
D.h2("5.1  In scope")
D.table(
    ["Dimension", "Phase 1 scope"],
    [
        ["Network", "Single manufacturing plant."],
        ["Planning levels", "Finished goods, and raw and packing materials. Single-level BOM explosion."],
        ["Portfolio", "300 to 800 finished goods; 1,500 to 4,000 raw and packing materials."],
        ["Horizon", "12 months rolling."],
        ["Buckets", "Monthly across 12 months. Weekly for the current month plus three, configurable to extend to six."],
        ["Planning processes", "Demand intake and validation; unconstrained MPS; constrained MPS optimization; "
                               "MPS approval; MRP explosion and netting; MRP confirmation; release to SAP."],
        ["Constraints modelled", "Line and work centre capacity including changeover time; material availability "
                                 "and supplier allocation; minimum order quantity, minimum batch and rounding; "
                                 "campaign and family grouping; frozen time fence."],
        ["Integration", "Inbound master data, inventory and open supply from SAP. Outbound Planned Independent "
                        "Requirements for raw and packing materials. Inbound execution feedback."],
        ["Governance", "Monthly S&OP cycle; weekly MPS cycle; two-week frozen zone; two mandatory approval gates."],
    ],
    [20, 80], size=9)

D.h2("5.2  Out of scope for phase 1")
D.table(
    ["Item", "Rationale and treatment"],
    [
        ["Semi-finished and bulk planning level",
         "Deferred to phase 2 under Decision D-05. The data model is built level-agnostic so the level "
         "can be enabled without restructuring. Note that the vendor scope currently assumes multi-level "
         "explosion including semi-finished goods; that assumption must be corrected."],
        ["Multi-plant and distribution network deployment",
         "Single plant in phase 1. Deployment and network sourcing logic deferred to phase 3."],
        ["Co-packers, tollers and subcontracting flows", "Not modelled in phase 1."],
        ["Statistical forecasting", "The forecast is an input, produced by Demand Planning. The engine does "
                                    "not generate it. See Decision D-04."],
        ["Detailed finite scheduling and sequencing on the line",
         "The engine produces a weekly constrained plan with campaign grouping. Shift-level and machine-level "
         "sequencing remains with Plant Operations."],
        ["Finished goods production execution path",
         "Subject to open Decision D-02. Interface IF-09 is not specified until that decision closes."],
        ["Purchase order execution, supplier collaboration and invoice matching",
         "Remains in SAP. The engine ends at the released requirement and consumes execution feedback."],
    ],
    [26, 74], size=9)

D.h2("5.3  Assumptions")
D.bullet("SAP S/4HANA is available with OData and CDS access for the objects listed in section 11.")
D.bullet("Material master, BOM, routing, purchasing info records and source lists are maintained in SAP "
         "and are the system of record for those objects.")
D.bullet("The consensus forecast is produced by Demand Planning outside this system and is available "
         "before each planning cycle.")
D.bullet("Plant Operations can supply a line and work centre structure, shift calendars, standard rates "
         "and a changeover matrix at least at product family level.")
D.bullet("A dedicated requirement type and purchase requisition document type can be configured in SAP "
         "for exclusive use by EZ-Commerce.")

# ==========================================================================
D.pagebreak()
D.h1("6.  Target architecture and system responsibility split")
D.h2("6.1  System boundary")
D.p("The boundary is drawn at a single point: the confirmed material requirement. Everything that "
    "decides a number sits to the left of it, in EZ-Commerce. Everything that executes and records "
    "sits to the right of it, in SAP.")

D.table(
    ["EZ-Commerce  (planning brain, non-SAP)", "Boundary", "SAP S/4HANA  (execution system of record)"],
    [
        ["Demand intake, validation, versioning and locking\n"
         "Stock norm and planning parameter governance\n"
         "Unconstrained MPS heuristic, 12 months\n"
         "Constrained optimization, weekly tactical window\n"
         "Capacity, changeover, campaign and MOQ modelling\n"
         "MPS planner review, override and approval\n"
         "BOM explosion to raw and packing materials\n"
         "Netting against stock, open orders and goods in transit\n"
         "Lot sizing and requirement date offsetting\n"
         "MRP planner review and confirmation\n"
         "Exception management and scenario comparison\n"
         "Reconciliation against SAP",
         "Confirmed\nnet\nrequirement\n\n>>>\n\nPlanned\nIndependent\nRequirement\n(IF-08)",
         "Material master, BOM, routing, work centre\n"
         "Purchasing info records and source lists\n"
         "Inventory, batch, expiry and quality status\n"
         "Receipt of Planned Independent Requirements\n"
         "MRP run under neutralised configuration (D-01)\n"
         "Purchase requisition creation, dedicated type\n"
         "Purchase order creation and management\n"
         "Goods receipt and inventory movement\n"
         "Production execution and confirmation\n"
         "Costing, valuation and financial record\n"
         "Supplier collaboration and invoice matching\n"
         "Execution feedback to EZ-Commerce (IF-10)"],
    ],
    [40, 14, 46], size=8.5, zebra=False, aligns=[None, CEN, None])
D.caption("Figure 1. System boundary. The boundary is the confirmed net requirement. SAP performs no "
          "planning arithmetic for in-scope materials.")

D.h2("6.2  Who calculates what")
D.p("This table is the operative correction to the vendor scope document, which places almost every "
    "row in the SAP column.")
D.table(
    ["Calculation or decision", "Owner system", "Note"],
    [
        ["Forecast validation and versioning", "EZ-Commerce", "SAP has no visibility of forecast versions."],
        ["Finished goods stock norm", "EZ-Commerce", "SAP safety stock set to zero for in-scope materials (D-01)."],
        ["Net requirement for finished goods", "EZ-Commerce", "Demand plus target closing stock less opening stock less receipts."],
        ["Lot sizing for finished goods", "EZ-Commerce", "SAP lot size set to lot-for-lot for in-scope materials."],
        ["Capacity resolution", "EZ-Commerce", "SAP cannot do this. Standard MPS and MRP are infinite capacity."],
        ["Changeover and campaign sequencing", "EZ-Commerce", "Not a standard SAP MRP capability."],
        ["Production plan approval", "EZ-Commerce", "Human gate. No equivalent exists in the vendor design."],
        ["BOM explosion", "EZ-Commerce", "Single level in phase 1. SAP holds the BOM; EZ-Commerce explodes it."],
        ["Netting against stock and open supply", "EZ-Commerce", "Performed once, here. Not repeated in SAP."],
        ["Raw and packing material stock norm", "EZ-Commerce", "SAP safety stock zero for in-scope materials."],
        ["Lead-time offset and required order date", "EZ-Commerce", "Planned delivery time plus goods receipt processing time."],
        ["MOQ, rounding and lot sizing for materials", "EZ-Commerce", "SAP rounding and minimum lot size removed for in-scope materials."],
        ["Material requirement confirmation", "EZ-Commerce", "Human gate before anything reaches SAP."],
        ["Purchase requisition creation", "SAP", "Through the MRP run, one-for-one from the received requirement."],
        ["Purchase order creation and management", "SAP", "Buyer converts inside the short-term window."],
        ["Goods receipt, inventory and valuation", "SAP", "System of record."],
        ["Master data: material, BOM, routing, source list", "SAP", "System of record. Synchronised into EZ-Commerce."],
    ],
    [42, 18, 40], size=8.5)

D.h2("6.3  What SAP will no longer be asked to do")
D.callout(
    "Correction to the vendor scope document",
    "The vendor scope has SAP performing the stock check, the BOM explosion, the netting and the "
    "generation of planned orders and purchase requisitions. Under the agreed architecture SAP does "
    "none of the first three. It receives a requirement that is already net and already feasible, and "
    "converts it into a purchase requisition. Leaving SAP-side netting active while EZ-Commerce also "
    "nets is not a configuration detail; it is a defect that under-orders every material in the "
    "portfolio. Decision D-01 in section 12 sets out the required configuration and the control that "
    "detects drift.",
    "FEF3E2", C.AMBER)

# ==========================================================================
D.pagebreak()
D.h1("7.  Planning calendar, horizon and time fences")
D.h2("7.1  Horizon and bucket profile")
D.p("The vendor scope leaves this open, listing demand upload frequency as a question for the business. "
    "It is a foundational design input: it determines the data model, the size of the optimization "
    "problem and the entire planner experience. It is fixed here.")
D.table(
    ["Horizon segment", "Bucket", "Planning treatment", "Purpose"],
    [
        ["Weeks 1-2 (frozen)", "Weekly", "Locked to the approved plan. Change only by formal exception.",
         "Stable commitment for production and procurement."],
        ["Weeks 3-13 (current month plus 3)", "Weekly", "Constrained optimization. Finite capacity, changeover, "
                                                        "campaign, MOQ.", "The executable tactical plan."],
        ["Months 4-6 (optional extension)", "Weekly", "Constrained optimization when the extension is enabled; "
                                                      "otherwise monthly unconstrained.",
         "Extended constrained view for long lead-time materials."],
        ["Months 4-12", "Monthly", "Unconstrained heuristic. Infinite capacity.",
         "Demand visibility, capacity pressure signalling, supplier forecasting."],
    ],
    [22, 10, 40, 28], size=8.5)

D.h2("7.2  Time fence policy")
D.table(
    ["Zone", "Horizon", "Who may change the plan", "Rule"],
    [
        ["Frozen", "Weeks 1-2", "MPS Planner, with S&OP Manager approval",
         "No system-driven re-planning. Manual change only through the exception path, with reason code, "
         "and only where materials and capacity permit."],
        ["Firm", "Weeks 3-13", "MPS Planner",
         "Re-planned each cycle, but change is measured. Stability is reported under control C-08."],
        ["Free", "Month 4 onwards", "System, reviewed by MPS Planner",
         "Fully re-planned each cycle. No change control."],
    ],
    [10, 14, 26, 50], size=8.5)
D.p("The frozen horizon is deliberately short at two weeks, reflecting a responsive category. The "
    "trade-off is accepted explicitly: a shorter freeze means better demand responsiveness and more "
    "expediting pressure on procurement. Control C-08 measures whether that trade-off is being managed "
    "or merely absorbed.", size=9, italic=True)

D.h2("7.3  Operating rhythm")
D.table(
    ["Cycle", "Frequency", "Trigger", "Output"],
    [
        ["S&OP", "Monthly", "Consensus forecast sign-off",
         "Locked 12-month demand plan; resolution of escalated shortfalls; agreed service and inventory targets."],
        ["MPS", "Weekly", "Forecast version locked",
         "Approved and frozen master production schedule across the tactical window."],
        ["MRP", "Weekly, with daily refresh capability", "MPS approval, then daily against live inventory",
         "Confirmed raw and packing material requirements released to SAP."],
        ["Procurement conversion", "Continuous", "Purchase requisition arrival in SAP",
         "Purchase orders placed inside the agreed short-term window."],
    ],
    [16, 20, 26, 38], size=8.5)

D.h3("Indicative weekly calendar")
D.table(
    ["Day", "Activity", "Owner"],
    [
        ["Monday", "Forecast refresh and validation; forecast version locked.", "Demand Planner"],
        ["Monday", "Master data, inventory and open supply synchronised from SAP.", "IT / automated"],
        ["Tuesday", "Unconstrained MPS run; constrained optimization run; exception review.", "MPS Planner"],
        ["Wednesday", "Plan adjustment, scenario comparison, capacity confirmation with Operations.", "MPS Planner / Plant Operations"],
        ["Wednesday", "MPS approved and frozen.", "MPS Planner"],
        ["Thursday", "MRP explosion and netting; material exception review.", "Material Planner"],
        ["Thursday", "MRP confirmed and released; Planned Independent Requirements transmitted to SAP.", "Material Planner / IT"],
        ["Friday", "SAP MRP converts requirements to purchase requisitions; buyer conversion begins.", "IT / Buyer"],
        ["Friday", "Reconciliation report reviewed; variances cleared.", "IT / Material Planner"],
    ],
    [12, 62, 26], size=8.5)

# ==========================================================================
D.pagebreak()
D.h1("8.  End-to-end process")
D.h2("8.1  Process overview")
D.p("Seven stages, two mandatory approval gates. The gates are the structural correction to the "
    "vendor scope document, which runs the whole chain automatically from a single upload.")

rows = []
for s in C.STAGES:
    gate = "GATE" if "MANDATORY" in s["gate"] else ""
    rows.append([s["id"], s["name"], s["system"], s["owner"], gate])
D.table(["Stage", "Name", "System", "Primary owner", ""], rows, [8, 38, 20, 26, 8],
        size=8.5, aligns=[CEN, None, None, None, CEN])
D.caption("Figure 2. Process overview. Stages S4 and S6 are mandatory approval gates: no MRP without an "
          "approved MPS, and no transmission to SAP without a confirmed MRP.")

D.callout(
    "The defect this process corrects",
    "In the vendor scope document, a single upload triggers Planned Independent Requirement creation "
    "and then immediately triggers the SAP MRP run. Master scheduling and material planning become one "
    "automated event. That is the issue already raised in review comments on that document: MPS must "
    "run first, for all SKUs, against supply constraints, and be finalised by the Production Planner. "
    "Only then does MRP explode the confirmed plan into material requirements. Two different decisions, "
    "taken by two different roles, at two different times.",
    "FEF3E2", C.AMBER)

# stage detail
for s in C.STAGES:
    D.pagebreak()
    D.h2(f"8.{C.STAGES.index(s) + 2}  {s['id']}  {s['name']}")
    D.table(["", ""],
            [["System", s["system"]], ["Primary owner", s["owner"]], ["Trigger", s["trigger"]]],
            [16, 84], size=8.5, zebra=False, bold_col0=True)
    D.h3("Purpose")
    D.p(s["purpose"], size=9.5)
    D.h3("Inputs")
    for i in s["inputs"]:
        D.bullet(i)
    D.h3("Processing logic")
    for i in s["logic"]:
        D.bullet(i)
    D.h3("Outputs")
    for i in s["outputs"]:
        D.bullet(i)
    D.h3("Exit condition")
    if "MANDATORY" in s["gate"]:
        D.callout("Mandatory approval gate", s["gate"], "ECFDF3", C.GREEN)
    else:
        D.p(s["gate"], size=9.5, italic=True)

# ==========================================================================
D.pagebreak()
D.h1("9.  Calculation logic specification")
D.p("This section is written for the build team. It defines the arithmetic precisely enough to be "
    "implemented and tested without further interpretation. Where a formula is given, user acceptance "
    "testing will verify it by hand calculation.")

D.h2("9.1  Notation")
D.table(
    ["Symbol", "Meaning"],
    [
        ["i", "Finished goods item"],
        ["c", "Component: raw or packing material"],
        ["t", "Time bucket (week inside the tactical window, month beyond it)"],
        ["l", "Production line or work centre"],
        ["D(i,t)", "Gross demand for item i in bucket t, from the locked forecast"],
        ["I(i,t)", "Projected closing inventory of item i at the end of bucket t"],
        ["I0(i)", "Opening on-hand inventory of item i, net of quality-hold and expired stock"],
        ["SR(i,t)", "Scheduled receipts for item i in bucket t: confirmed production or purchase orders"],
        ["SS(i)", "Stock norm, or target safety stock, for item i"],
        ["N(i,t)", "Net requirement for item i in bucket t"],
        ["P(i,t)", "Planned production quantity for item i in bucket t"],
        ["q(c,i)", "Component quantity of c per unit of i, from the BOM, including scrap"],
        ["LT(c)", "Planned delivery time plus goods receipt processing time for component c"],
        ["MOQ(c)", "Minimum order quantity for component c"],
        ["RND(c)", "Rounding value for component c"],
        ["Cap(l,t)", "Available capacity of line l in bucket t, after shift calendar, maintenance and efficiency"],
        ["rate(i,l)", "Production rate of item i on line l"],
        ["CO(i,j,l)", "Changeover time and cost from item or family i to j on line l"],
        ["U(i,t)", "Unmet or late demand for item i in bucket t"],
        ["w(i)", "Service priority weight for item i"],
    ],
    [16, 84], size=8.5)

D.h2("9.2  Stock norm")
D.p("Three policies must be supported, selectable per item or item class:")
D.bullet("Days of cover:  SS(i) = DOC(i) x average daily demand over a configurable forward window.",
         bold_lead="Policy 1  ")
D.bullet("Fixed quantity:  SS(i) = a maintained constant.", bold_lead="Policy 2  ")
D.bullet("Statistical safety stock:  SS(i) = z(service level) x standard deviation of demand over lead "
         "time, computed from demand history and lead-time variability.", bold_lead="Policy 3  ")
D.p("The active policy, its parameters and its change history are held in EZ-Commerce under change "
    "control. SAP safety stock is set to zero for in-scope materials so the norm is applied exactly "
    "once. See Decision D-01.", size=9, italic=True)

D.h2("9.3  Unconstrained MPS heuristic")
D.p("Executed per item across the 12-month horizon, bucket by bucket in chronological order.")
D.table(
    ["Step", "Logic"],
    [
        ["1", "Initialise projected inventory: I(i,0) = I0(i), taken from the SAP inventory snapshot, "
              "excluding quality-hold, blocked and expired stock."],
        ["2", "For each bucket t in chronological order, compute the projected position before production:\n"
              "    available = I(i,t-1) + SR(i,t) - D(i,t)"],
        ["3", "Compute net requirement against the stock norm:\n"
              "    N(i,t) = max( 0 , SS(i) - available )"],
        ["4", "If bucket t falls inside the frozen horizon, do not re-plan. Set P(i,t) to the previously "
              "approved quantity and continue."],
        ["5", "Apply the lot-sizing policy to convert net requirement into a planned quantity:\n"
              "    lot-for-lot:      P(i,t) = N(i,t)\n"
              "    fixed lot:        P(i,t) = ceiling( N(i,t) / L(i) ) x L(i)\n"
              "    minimum batch:    P(i,t) = max( N(i,t) , B(i) ) when N(i,t) > 0\n"
              "    period of supply: accumulate demand over the coverage period, then produce once"],
        ["6", "Roll the inventory forward:\n"
              "    I(i,t) = I(i,t-1) + SR(i,t) + P(i,t) - D(i,t)"],
        ["7", "Raise an exception where I(i,t) falls below SS(i), and where the implied production "
              "exceeds nominal line capacity for the bucket."],
    ],
    [7, 93], size=8.5)

D.h2("9.4  Constrained optimization model")
D.p("A mixed-integer program solved over weekly buckets across the tactical window. This is the "
    "capability entirely absent from the vendor scope document, and it is the reason the calculation "
    "cannot be delegated to SAP: standard SAP MPS and MRP plan at infinite capacity.")

D.h3("Decision variables")
D.bullet("P(i,t) - quantity of item i produced in bucket t, continuous and non-negative.")
D.bullet("y(i,t) - binary, 1 if item i is produced at all in bucket t, used for minimum batch and changeover.")
D.bullet("z(i,l,t) - binary, assignment of item i to line l in bucket t, where an item may run on several lines.")
D.bullet("I(i,t) - projected closing inventory, non-negative.")
D.bullet("U(i,t) - unmet or late demand, non-negative.")
D.bullet("O(l,t) - overtime hours used on line l in bucket t, non-negative and bounded.")

D.h3("Constraints")
D.table(
    ["Ref", "Constraint", "Formulation"],
    [
        ["K1", "Inventory balance", "I(i,t) = I(i,t-1) + P(i,t) + SR(i,t) - D(i,t) + U(i,t)   for all i, t"],
        ["K2", "Finite capacity", "sum over i of [ P(i,t) / rate(i,l) ] + changeover time on line l in bucket t\n"
                                  "        <= Cap(l,t) + O(l,t)   for all l, t"],
        ["K3", "Overtime bound", "O(l,t) <= maximum permitted overtime for line l in bucket t"],
        ["K4", "Material availability", "sum over i of [ q(c,i) x P(i,t) ] <= available supply of component c in bucket t,\n"
                                        "        applied only to constrained or allocated components"],
        ["K5", "Minimum batch", "P(i,t) >= B(i) x y(i,t)   and   P(i,t) <= M x y(i,t)"],
        ["K6", "Lot size multiple", "P(i,t) is an integer multiple of L(i) where a fixed lot policy applies"],
        ["K7", "Frozen time fence", "P(i,t) = approved quantity, fixed, for every bucket t inside the frozen horizon"],
        ["K8", "Safety stock target", "I(i,t) >= SS(i) - v(i,t), where v(i,t) is a penalised soft violation, "
                                      "so the model degrades gracefully rather than becoming infeasible"],
        ["K9", "Campaign grouping", "Items within a defined family are constrained to share production windows, "
                                    "so that changeover between families is incurred at most once per window"],
        ["K10", "Line eligibility", "z(i,l,t) = 0 where item i cannot run on line l"],
    ],
    [7, 20, 73], size=8.5)

D.h3("Objective function")
D.p("Applied lexicographically. The second term is optimised only among solutions that are already "
    "optimal for the first. Service is protected before cost is considered.")
D.table(
    ["Priority", "Objective", "Expression"],
    [
        ["1", "Minimise weighted unmet demand", "minimise  sum over i,t of [ w(i) x U(i,t) ]"],
        ["2", "Minimise total cost", "minimise  sum of changeover cost + overtime cost + inventory holding cost\n"
                                     "        + expediting cost + penalised safety stock violation"],
    ],
    [10, 30, 60], size=8.5)

D.h3("Solver requirements")
D.bullet("Must return the best feasible solution found when the configured time limit is reached, "
         "together with the optimality gap. It must never return nothing.")
D.bullet("Must report the binding constraint for every quantity of unmet demand, so that the planner "
         "can see whether the limit was capacity, material or a lot-sizing rule.")
D.bullet("Must support decomposition by line and by product family, so that run time scales at the "
         "target portfolio of 800 finished goods. See risk R-05 and NFR-02.")
D.bullet("Must log every run: input version, parameter set, solver status, objective value, run time.")

D.h2("9.5  MRP explosion and netting")
D.p("Executed against the approved MPS version only.")
D.table(
    ["Step", "Logic"],
    [
        ["1", "Gross requirement by explosion, honouring BOM validity dates and component scrap:\n"
              "    G(c,t) = sum over i of [ q(c,i) x P(i,t) ]"],
        ["2", "Lead-time offset to derive the required order date:\n"
              "    required order bucket = t - LT(c), where LT(c) = planned delivery time + goods receipt processing time"],
        ["3", "Net against projected available stock, excluding quality-hold, blocked and expired batches, "
              "then against open purchase orders, open purchase requisitions and goods in transit at their "
              "confirmed dates:\n"
              "    A(c,t) = I0(c) + sum of open supply due on or before t - sum of G(c,s) for s <= t"],
        ["4", "Net requirement against the material stock norm:\n"
              "    N(c,t) = max( 0 , G(c,t) + SS(c) - A(c,t) )"],
        ["5", "Apply lot sizing, minimum order quantity and rounding:\n"
              "    Q(c,t) = 0 if N(c,t) = 0\n"
              "    otherwise Q(c,t) = ceiling( max( N(c,t) , MOQ(c) ) / RND(c) ) x RND(c)"],
        ["6", "Raise exceptions: requirement falling inside lead time; batch expiring before planned "
              "consumption; MOQ forcing coverage beyond a configured threshold; component with no valid "
              "source of supply; component blocked."],
        ["7", "Q(c,t) is the quantity transmitted to SAP as a Planned Independent Requirement, after "
              "planner confirmation at gate S6. It is a net quantity and SAP must not net it again."],
    ],
    [7, 93], size=8.5)

D.h2("9.6  Worked example")
D.p("A single component across three weeks, to make the netting sequence unambiguous for testing.")
D.table(
    ["Line", "Item", "W1", "W2", "W3", "Note"],
    [
        ["a", "Gross requirement from BOM explosion", "1,000", "1,200", "800", "G(c,t)"],
        ["b", "Opening stock, unrestricted only", "1,500", "-", "-", "Expired and quality-hold excluded"],
        ["c", "Open purchase order, confirmed", "0", "600", "0", "Netted at confirmed date"],
        ["d", "Projected available before norm", "500", "-100", "-900", "b + c - cumulative a"],
        ["e", "Stock norm", "400", "400", "400", "SS(c), held in EZ-Commerce, not SAP"],
        ["f", "Net requirement", "0", "500", "800", "max(0, a + e - available)"],
        ["g", "MOQ 1,000, rounding 500", "0", "1,000", "1,000", "Q(c,t) after lot sizing"],
        ["h", "Transmitted to SAP as PIR", "0", "1,000", "1,000", "Net. SAP must not deduct b or c again."],
    ],
    [6, 40, 12, 12, 12, 18], size=8.5,
    aligns=[CEN, None, CEN, CEN, CEN, None])
D.callout(
    "Why line h is the whole argument for Decision D-01",
    "If SAP MRP nets the transmitted 1,000 in week 2 against the same 1,500 opening stock and the same "
    "600 open purchase order that EZ-Commerce has already deducted, SAP will create a purchase "
    "requisition for nothing at all. Both systems will show a correct-looking plan. The shortage will "
    "appear on the line in week 3. This is why SAP-side netting must be neutralised for in-scope "
    "materials and why control C-05 reconciles the two daily.",
    "FDF2F4", C.RED)

# ==========================================================================
D.pagebreak()
D.h1("10.  Data and master data model")
D.h2("10.1  Ownership")
D.p("Decision D-03. A single owner per object. Where an object is owned by SAP it is synchronised into "
    "EZ-Commerce read-only; where it is owned by EZ-Commerce it is not maintained in SAP at all for "
    "in-scope materials.")
D.table(
    ["Object", "System of record", "Maintained by", "Sync into EZ-Commerce"],
    [
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
    ],
    [30, 16, 26, 28], size=8.5)

D.h2("10.2  Parameter governance")
D.p("Planning parameters change planning outcomes directly, so they are governed as configuration, not "
    "as free-text fields.")
D.bullet("Every parameter change follows maker-checker approval inside EZ-Commerce.")
D.bullet("Full history retained: who changed what, from what to what, when, and why.")
D.bullet("Parameter changes are versioned with the plan, so any historic plan can be reproduced exactly.")
D.bullet("Control C-06 verifies weekly that SAP-side parameters for in-scope materials remain at their "
         "neutralised values.")

D.h2("10.3  Data quality preconditions")
D.p("Planning quality cannot exceed data quality. These are go-live gates, not aspirations. Risk R-04 "
    "records the exposure; control C-02 monitors it.")
D.bullet("Every in-scope finished good has a valid, in-date, released BOM.")
D.bullet("Every component has a valid source of supply, a planned delivery time and a maintained MOQ "
         "and rounding value.")
D.bullet("Every in-scope material is extended to the plant with a consistent unit of measure and "
         "conversion factor.")
D.bullet("Routing or a maintained nominal line rate exists for every finished good.")

# ==========================================================================
D.section(landscape=True)
D.h1("11.  Integration architecture and interface register")
D.h2("11.1  Integration principles")
D.bullet("Idempotency. Every outbound message is keyed on planning version, material, plant and bucket, "
         "so that a replay corrects rather than duplicates. Verified by UAT-13.")
D.bullet("No silent failure. Every interface failure alerts a named support group. A planner must never "
         "believe a release succeeded when it did not.")
D.bullet("Partial failure isolation. Failed records are quarantined and reported; successful records "
         "stand; replay is targeted at the failed subset only.")
D.bullet("Full payload audit. Request and response retained per record, for 24 months, traceable back "
         "to the approved plan version.")
D.bullet("Graceful degradation. If SAP is unavailable, planning continues against the last good "
         "snapshot, the snapshot age is displayed to the planner, and release is blocked.")
D.bullet("Freshness enforcement. Inventory and open supply are refreshed on demand immediately before "
         "an MRP run; the run is blocked if the snapshot exceeds its configured age.")

D.h2("11.2  Interface register")
rows = [[i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8]] for i in C.INTERFACES]
D.table(
    ["Ref", "Interface", "Direction", "Type", "Object", "Mechanism", "Frequency", "Volume", "Error handling"],
    rows, [4, 12, 11, 5, 13, 18, 9, 12, 16], size=7.5)

D.h2("11.3  Key and identifier strategy")
D.table(
    ["Concern", "Approach"],
    [
        ["Natural key for requirements", "Planning version + material + plant + bucket start date. This key is the basis of idempotency."],
        ["Traceability", "Every transmitted record carries the MRP run identifier, the approved MPS version and the locked forecast version, so any quantity in SAP can be traced back to the forecast it came from."],
        ["SAP-side identification", "Dedicated requirement type for Planned Independent Requirements and a dedicated purchase requisition document type, so EZ-Commerce-originated records are always separable from manual ones."],
        ["Reconciliation key", "The same natural key is used by control C-05 to compare requirement released against requirement present in SAP."],
        ["Orphan detection", "Purchase requisitions of the dedicated document type with no matching EZ-Commerce requirement are reported by control C-07."],
    ],
    [18, 82], size=8.5)

# ==========================================================================
D.section(landscape=False)
D.h1("12.  Design decisions")
for dec in C.DECISIONS:
    D.h2(f"{dec['id']}  {dec['title']}")
    fill, accent = ((C.LIGHT, C.BLUE) if dec["status"].startswith("DECIDED")
                    else ("FEF3E2", C.AMBER))
    D.callout("Status: " + dec["status"], dec["problem"], fill, accent)
    if dec["options"]:
        D.h3("Options considered")
        D.table(["", "Option", "Description", "For", "Against"],
                [[o[0], o[1], o[2], o[3], o[4]] for o in dec["options"]],
                [4, 18, 28, 24, 26], size=8)
    D.h3("Decision")
    D.p(dec["decision"], size=9.5)
    if dec["implementation"]:
        D.h3("Implementation requirements")
        for x in dec["implementation"]:
            D.bullet(x)
    D.h3("Consequence")
    D.p(dec["consequence"], size=9.5, italic=True)
    if dec is not C.DECISIONS[-1]:
        D.pagebreak()

# ==========================================================================
D.section(landscape=True)
D.h1("13.  RACI model")
D.h2("13.1  Role definitions")
D.table(["Code", "Role", "Accountability"],
        [[r[0], r[1], r[2]] for r in C.ROLES], [5, 18, 77], size=8.5)

D.h2("13.2  RACI matrix")
D.p("R responsible, A accountable, C consulted, I informed. Exactly one accountable role per step. "
    "Where a single role is both, it is shown as A/R.", size=9, italic=True)
rows = []
for step_id, stage, name, assign in C.RACI:
    rows.append([step_id, stage, name] + [assign.get(rc, "") for rc in C.ROLE_CODES])
D.table(["Step", "Stage", "Activity"] + C.ROLE_CODES, rows,
        [5, 5, 46] + [6] * 8, size=8,
        aligns=[CEN, CEN, None] + [CEN] * 8)

D.section(landscape=False)
D.h2("13.3  Decision rights")
D.table(
    ["Decision", "Authority", "Escalation"],
    [
        ["Lock the demand forecast version", "Demand Planner, accountable to S&OP Manager", "S&OP Manager"],
        ["Change a finished goods stock norm", "MPS Planner, approved by S&OP Manager", "Supply Chain leadership"],
        ["Approve and freeze the MPS", "MPS Planner", "S&OP Manager"],
        ["Change the plan inside the frozen zone", "MPS Planner with S&OP Manager approval", "Supply Chain leadership"],
        ["Accept unmet demand in the plan", "S&OP Manager, with commercial input", "Supply Chain leadership"],
        ["Confirm and release material requirements", "Material Planner", "MPS Planner, then S&OP Manager"],
        ["Change a material stock norm, MOQ or lot-sizing policy", "Material Planner, approved by MPS Planner", "S&OP Manager"],
        ["Convert a purchase requisition to a purchase order", "Procurement Buyer", "Procurement lead"],
        ["Change SAP MRP configuration for in-scope materials", "Master Data Steward, only through planning change control", "IT Integration Lead"],
        ["Suspend an interface or re-run a transmission", "IT Integration Lead", "IT lead, with Material Planner informed"],
    ],
    [34, 40, 26], size=8.5)

# ==========================================================================
D.section(landscape=True)
D.h1("14.  Controls, exceptions and reconciliation")
D.p("These controls exist because the architecture deliberately splits calculation from execution. "
    "Splitting them creates the possibility of divergence, so divergence must be detected "
    "systematically rather than discovered on the production line.")
D.table(["Ref", "Control", "Test", "Owner", "Frequency"],
        [[c[0], c[1], c[2], c[3], c[4]] for c in C.CONTROLS],
        [5, 18, 53, 14, 10], size=8.5)

D.h2("14.1  Exception taxonomy")
D.table(
    ["Exception", "Raised at", "Meaning", "Required action"],
    [
        ["Master data rejection", "S1", "Material inactive, not extended to plant, or unit of measure missing.", "Master Data Steward corrects in SAP; record reloaded."],
        ["Forecast variance", "S1", "SKU moved beyond the configured tolerance versus the prior locked version.", "Demand Planner confirms the movement is intended."],
        ["Coverage breach", "S2", "Projected inventory falls below the stock norm.", "MPS Planner reviews; may be resolved by S3."],
        ["Unmet demand", "S3", "The optimizer could not meet demand within the constraints.", "MPS Planner reviews binding constraint; escalates to S&OP if unresolved."],
        ["Capacity breach", "S3", "Required production exceeds available capacity including overtime.", "Plant Operations confirms whether capacity can be extended."],
        ["Time fence conflict", "S4", "An edit would change a frozen bucket.", "Blocked, or approved through the exception path with reason code."],
        ["Shortage inside lead time", "S5", "A requirement falls inside the material's lead time and cannot be sourced normally.", "Material Planner expedites or escalates to Procurement."],
        ["Expiry before consumption", "S5", "A batch will expire before the plan consumes it.", "Material Planner reviews with Quality and Operations."],
        ["MOQ excess coverage", "S5", "The minimum order quantity forces coverage beyond the configured threshold.", "Material Planner accepts or renegotiates with the supplier."],
        ["No valid source of supply", "S5", "The component has no source list or purchasing info record.", "Blocks release. Procurement and Master Data Steward resolve."],
        ["Transmission failure", "S7", "One or more records failed to reach SAP.", "IT investigates; targeted replay of the failed subset."],
        ["Reconciliation variance", "S7", "Requirement in SAP differs from requirement released.", "IT and Material Planner investigate; control C-05."],
        ["Orphan requisition", "S7", "A purchase requisition of the dedicated type has no matching requirement.", "Material Planner clears; control C-07."],
        ["Configuration drift", "n/a", "An in-scope material no longer carries the neutralised SAP settings.", "Master Data Steward restores; control C-06."],
    ],
    [15, 7, 40, 38], size=8)

# ==========================================================================
D.section(landscape=True)
D.h1("15.  Requirement register")
D.p("Numbered, traceable and estimable. This register, not the narrative, is the contractual statement "
    "of requirement. Priorities follow MoSCoW: Must, Should, Could.")
groups = []
for r in C.REQUIREMENTS:
    if r[1] not in groups:
        groups.append(r[1])
rows = [[r[0], r[1], r[2], r[3]] for r in C.REQUIREMENTS]
D.table(["Ref", "Group", "Requirement", "Priority"], rows, [6, 9, 77, 8], size=8,
        aligns=[None, None, None, CEN])

D.section(landscape=False)
D.h2("15.1  Requirement summary by group")
counts = {}
for r in C.REQUIREMENTS:
    counts.setdefault(r[1], {"Must": 0, "Should": 0, "Could": 0})
    counts[r[1]][r[3]] += 1
rows = [[g, counts[g]["Must"], counts[g]["Should"], counts[g]["Could"],
         sum(counts[g].values())] for g in groups]
rows.append(["Total",
             sum(c["Must"] for c in counts.values()),
             sum(c["Should"] for c in counts.values()),
             sum(c["Could"] for c in counts.values()),
             len(C.REQUIREMENTS)])
D.table(["Group", "Must", "Should", "Could", "Total"], rows, [40, 15, 15, 15, 15],
        size=9, aligns=[None, CEN, CEN, CEN, CEN])

# ==========================================================================
D.pagebreak()
D.h1("16.  Non-functional requirements")
D.p("Sized against the confirmed phase 1 portfolio: a single plant, 300 to 800 finished goods and "
    "1,500 to 4,000 raw and packing materials. Run time is a functional constraint, not a technical "
    "nicety: an optimizer that does not finish inside the weekly planning window is unusable however "
    "correct its answer.")
D.table(["Ref", "Area", "Requirement"], [[n[0], n[1], n[2]] for n in C.NFRS],
        [6, 20, 74], size=8.5)

# ==========================================================================
D.section(landscape=True)
D.h1("17.  Acceptance criteria and test scenarios")
D.p("These scenarios are the acceptance basis. UAT-12 in particular must pass before go-live: it is "
    "the direct test of the double-netting defect described in Decision D-01.")
D.table(["Ref", "Scenario", "Test", "Expected result"],
        [[u[0], u[1], u[2], u[3]] for u in C.UAT], [5, 18, 38, 39], size=8)

# ==========================================================================
D.section(landscape=False)
D.h1("18.  Implementation roadmap")
D.p("Sequenced so that each phase delivers something a planner can use, and so that the highest-risk "
    "unknowns - master data readiness and optimizer run time - are tested early rather than at user "
    "acceptance testing.")
for name, title, dur, items in C.ROADMAP:
    D.h2(f"{name}  -  {title}   ({dur})")
    for i in items:
        D.bullet(i)

D.h2("18.1  Sequencing rationale")
D.bullet("Phase 0 exists because two things can invalidate the plan and both are knowable early: "
         "master data completeness, and whether the optimizer solves at full volume inside the weekly "
         "window. Both are tested before the build is committed.")
D.bullet("Phase 1a delivers visible value on its own. A validated forecast and an unconstrained "
         "12-month plan with projected coverage is already better than the current spreadsheet.")
D.bullet("Phase 1b carries the most technical risk and the most business value. It is separated so "
         "that it can slip without stopping 1a and 1c.")
D.bullet("Phase 1c is the only phase that writes to SAP. It is last, and it is preceded by the "
         "reconciliation controls, not followed by them.")
D.bullet("A pilot on a limited product family precedes full cutover, so that the double-netting "
         "guardrail is proven on real data at small scale first.")

# ==========================================================================
D.section(landscape=True)
D.h1("19.  Risks and mitigations")
D.table(["Ref", "Risk", "Likelihood", "Impact", "Description", "Mitigation"],
        [[r[0], r[1], r[2], r[3], r[4], r[5]] for r in C.RISKS],
        [4, 14, 7, 6, 36, 33], size=8,
        aligns=[None, None, CEN, CEN, None, None])

# ==========================================================================
D.section(landscape=True)
D.h1("Annex A.  Gap analysis against the vendor scope document")
D.p("Assessed against the vendor scope document version 1.0 (SCOPE-MARICO-EZ-SAP-v1.0). The document "
    "is a competent description of an upload-and-trigger integration. It is not a specification for a "
    "planning system, and the gap between those two things is where the cost and the value of this "
    "programme sit. Each gap below is stated with the correction required and the requirement that "
    "closes it.")
D.table(["Ref", "Where", "What the document says", "Why it is a problem", "Correction required", "Requirement"],
        [[g[0], g[1], g[2], g[3], g[4], g[5]] for g in C.GAPS],
        [4, 9, 24, 26, 27, 10], size=7.5)

D.section(landscape=False)
D.h2("A.1  Summary")
D.p("Of the fifteen gaps, four change cost and timeline materially and must be resolved before the "
    "build is estimated:")
D.bullet("G-02 and G-04: the master scheduling logic and the constrained optimizer are the two "
         "components carrying the business value, and neither is specified in the current scope. They "
         "are therefore not priced and not scheduled.")
D.bullet("G-03: the assumption that SAP can perform constrained planning is factually wrong and will "
         "surface as a defect during testing, at the worst possible moment.")
D.bullet("G-08: the netting responsibility is assigned to SAP, which both contradicts the agreed "
         "architecture and creates the double-netting defect.")
D.p("The remaining eleven are corrections of substance but not of architecture, and can be absorbed "
    "into the design phase provided they are accepted now rather than discovered later.")

# ==========================================================================
D.pagebreak()
D.h1("Annex B.  Glossary and terminology")
D.p("Terminology in the current documentation is inconsistent in ways that lead directly to incorrect "
    "interface design. The definitions below are binding for all design documents in this programme.")
D.table(["Term", "Definition"], [[g[0], g[1]] for g in C.GLOSSARY], [24, 76], size=8.5)

# ==========================================================================
D.section(landscape=True)
D.h1("Annex C.  Open questions for the design workshop")
D.table(["Ref", "Question", "Owner", "What it blocks"],
        [[q[0], q[1], q[2], q[3]] for q in C.OPEN_QUESTIONS],
        [5, 52, 21, 22], size=8.5)

D.section(landscape=False)
D.h2("C.1  Accompanying documents")
D.table(
    ["Document", "Format", "Purpose"],
    [
        ["Marico_MPS_MRP_Business_Requirements_Brief_v1.0", "Word (.docx)", "This document. The statement of business requirement."],
        ["Marico_MPS_MRP_Process_Infographic_v1.0", "PowerPoint (.pptx)", "Editable process flow, system map, planning calendar, RACI summary and the before-and-after comparison against the vendor scope. Fully editable shapes."],
        ["Marico_MPS_MRP_RACI_and_Registers_v1.0", "Excel (.xlsx)", "RACI matrix, interface register, requirement register, master data ownership, controls, risks, gap analysis and open decisions, in filterable form for the build team."],
    ],
    [38, 14, 48], size=9)

D.d.add_paragraph()
p = D.p("End of document", size=9, italic=True, color=C.GREY, align=CEN)

d.save(os.path.abspath(OUT))
print("Wrote", os.path.abspath(OUT))
