"""Simple .docx reader: extract readable text from Word .docx files.

This module provides a small helper to extract paragraphs/text from the
`word/document.xml` part of a .docx archive. It avoids heavy dependencies
and should work for common documents produced by MS Word and LibreOffice.
"""
from pathlib import Path
import zipfile
from xml.etree import ElementTree as ET


def read_docx(path: Path) -> str:
    """Return extracted plain text from a .docx file.

    Args:
        path: Path to the .docx file on disk.

    Returns:
        A string with paragraph-separated text. On error returns an empty string.
    """
    path = Path(path)
    if not path.exists():
        return ""
    try:
        with zipfile.ZipFile(path, "r") as z:
            # Most docx files contain word/document.xml
            with z.open("word/document.xml") as docxml:
                xml = docxml.read()
    except Exception:
        return ""

    try:
        tree = ET.fromstring(xml)
    except Exception:
        return ""

    # WordprocessingML uses namespaces; find the w namespace from the root
    ns = {}
    if tree.tag.startswith("{"):
        uri = tree.tag.split("}")[0].strip("{")
        ns["w"] = uri
    else:
        ns["w"] = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

    paragraphs = []
    # Iterate over paragraph elements and extract all <w:t> text children
    for p in tree.findall('.//w:p', ns):
        texts = []
        for t in p.findall('.//w:t', ns):
            if t.text:
                texts.append(t.text)
        if texts:
            paragraphs.append(''.join(texts))

    return '\n'.join(paragraphs)
