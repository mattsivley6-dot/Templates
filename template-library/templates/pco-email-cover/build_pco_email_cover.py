# build_pco_email_cover.py
# PCO email cover note builder.
# Fills template_pco_email_cover.txt (or template_sub_backup_request.md) from a
# JSON data file and writes a ready-to-paste plain-text email body.
#
# Usage:  python build_pco_email_cover.py [data.json] [out_dir] [--company company.json]
#   data.json  defaults to sample_data.json next to this script
#   out_dir    defaults to _sample_output next to this script
#   --company  defaults to ../../company.example.json relative to this script
#
# Company tokens: any string in the data file may contain {legal_name}, {dba},
# {address_line1}, {city_state_zip}, {phone}, {email}, {website}, {license},
# {pm_name}, {pm_title}, {pm_phone} or {pm_email}; they are filled from the
# company config. If "signature" is left out of the data file, a default
# signature is built from the company config.
#
# Deterministic: no datetime, no random. Identical JSON in, identical bytes out.
# Stdlib only.

import argparse
import json
import re
import sys
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_COMPANY = HERE.parent.parent / "company.example.json"

TEMPLATES = {
    "pco_cover": HERE / "template_pco_email_cover.txt",
    "sub_backup_request": HERE / "template_sub_backup_request.md",
}

DEFAULT_WRAP = {"pco_cover": 83, "sub_backup_request": 0}

# House rule: never use em dashes (or en dashes) anywhere.
FORBIDDEN = {chr(0x2014): "em dash", chr(0x2013): "en dash"}

_TOKEN = re.compile(r"\{([a-z_0-9]+)\}")


def load_company(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def fill_tokens(obj, tokens):
    """Replace {company_key} tokens in every string of the data."""
    if isinstance(obj, str):
        return _TOKEN.sub(lambda m: tokens.get(m.group(1), m.group(0)), obj)
    if isinstance(obj, list):
        return [fill_tokens(x, tokens) for x in obj]
    if isinstance(obj, dict):
        return {k: fill_tokens(v, tokens) for k, v in obj.items()}
    return obj


def default_signature(variant, company):
    if variant == "sub_backup_request":
        lines = [company.get("pm_name"), company.get("dba")]
    else:
        lines = [company.get("pm_name"), company.get("pm_title"),
                 company.get("legal_name")]
    return [x for x in lines if x]


def check_dashes(text, where):
    for ch, name in FORBIDDEN.items():
        if ch in text:
            raise ValueError(
                "House-style violation: %s found in %s. Reword with a comma, "
                "period, or hyphen and rerun." % (name, where)
            )


def wrap_para(text, width, indent=""):
    """Wrap one paragraph. width <= 0 means leave it as a single line."""
    if width <= 0:
        return indent + text
    return textwrap.fill(
        text,
        width=width,
        initial_indent=indent,
        subsequent_indent=" " * len(indent),
        break_long_words=False,
        break_on_hyphens=False,
    )


def render_body(items, width):
    """Turn the JSON body list into blank-line-separated text blocks.

    Item shapes:
      "plain string"                          -> wrapped paragraph
      {"heading": str, "text": str}           -> heading line + paragraph, one block
      {"intro": str?, "numbered": [str, ...]} -> intro line + 1./2./3. items, one block
      {"intro": str?, "bullets":  [str, ...]} -> intro line + "- " items, one block
    """
    blocks = []
    for item in items:
        if isinstance(item, str):
            blocks.append(wrap_para(item, width))
        elif isinstance(item, dict) and "heading" in item:
            lines = [item["heading"]]
            if item.get("text"):
                lines.append(wrap_para(item["text"], width))
            blocks.append("\n".join(lines))
        elif isinstance(item, dict) and ("numbered" in item or "bullets" in item):
            lines = []
            if item.get("intro"):
                lines.append(wrap_para(item["intro"], width))
            if "numbered" in item:
                for n, entry in enumerate(item["numbered"], 1):
                    prefix = "%d. " % n
                    text = wrap_para(entry, width, indent=prefix)
                    # wrap_para indents the first line too; swap in the prefix
                    text = prefix + text[len(prefix):]
                    lines.append(text)
            else:
                for entry in item["bullets"]:
                    text = wrap_para(entry, width, indent="- ")
                    text = "- " + text[2:]
                    lines.append(text)
            blocks.append("\n".join(lines))
        else:
            raise ValueError("Unrecognized body item: %r" % (item,))
    return "\n\n".join(blocks)


def build(data_path, out_dir, company):
    data = json.loads(Path(data_path).read_text(encoding="utf-8"))
    tokens = {k: v for k, v in company.items() if isinstance(v, str)}
    data = fill_tokens(data, tokens)

    variant = data.get("variant", "pco_cover")
    if variant not in TEMPLATES:
        raise ValueError("variant must be one of %s" % sorted(TEMPLATES))

    width = data.get("wrap_width", DEFAULT_WRAP[variant])

    template = TEMPLATES[variant].read_text(encoding="utf-8")

    signature = data.get("signature") or default_signature(variant, company)

    fields = {
        "TO": "; ".join(data["to"]),
        "CC": "; ".join(data.get("cc", [])),
        "SUBJECT": data["subject"],
        "ATTACH": "; ".join(data.get("attach", [])),
        "GREETING": data["greeting"],
        "BODY": render_body(data["body"], width),
        "CLOSING": data["closing"],
        "SIGNATURE": "\n".join(signature),
        "DRAFT_TITLE": data.get("draft_title", ""),
    }

    out = template
    for key, value in fields.items():
        out = out.replace("{{%s}}" % key, value)

    # Drop header lines whose value came back empty (e.g. no CC, no ATTACH).
    kept = []
    for line in out.split("\n"):
        if line in ("CC:  ", "ATTACH:  ", "Cc: ", "# DRAFT EMAIL - "):
            continue
        kept.append(line)
    out = "\n".join(kept)

    check_dashes(out, "rendered email text")

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / data["output_filename"]
    # LF line endings, UTF-8 no BOM, single trailing newline.
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(out if out.endswith("\n") else out + "\n")
    return out_path


def main(argv):
    ap = argparse.ArgumentParser(description="Build a PCO email cover note.")
    ap.add_argument("data", nargs="?", default=str(HERE / "sample_data.json"),
                    help="email data JSON (default: sample_data.json here)")
    ap.add_argument("out_dir", nargs="?", default=str(HERE / "_sample_output"),
                    help="output folder (default: _sample_output here)")
    ap.add_argument("--company", default=str(DEFAULT_COMPANY),
                    help="company config JSON (default: "
                         "template-library/company.example.json)")
    args = ap.parse_args(argv[1:])
    company = load_company(args.company)
    out_path = build(args.data, args.out_dir, company)
    print("Wrote %s" % out_path)


if __name__ == "__main__":
    main(sys.argv)
