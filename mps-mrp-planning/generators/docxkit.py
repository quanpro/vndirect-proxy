# -*- coding: utf-8 -*-
"""Shared python-docx helpers: schema-safe property insertion, styled
tables, callouts and the Doc wrapper used by every Word deliverable."""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

import content as C

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
