# Duct Transition Shop Ticket

## Purpose and when to use
Fabrication shop ticket for RTU duct transitions, drops, and flex connections. Sent to the sheet metal shop (with your own RFQ or cut list) so fittings can be built from field measurements before the unit set. One schedule page listing every fitting, then ONE FITTING PER PAGE with a 3D isometric drawing, dimension callouts, and a spec box.

Style note: use this format (schedule page plus one isometric per fitting on a small landscape page) for duct shop tickets, rather than a large title-block drawing sheet. It reads well on a phone and prints cleanly in the shop.

## Output spec
- Format: PDF (reportlab, invariant=1, byte-deterministic), page size 510 x 358.5 pt landscape
- Font: Helvetica. Schedule title 16 bold; schedule rows 9.8 bold tag + 9.4 regular; callout labels 10.5 bold; callout values and spec lines 9.0; S/drive marks 8.2 bold
- Ink colors: #2B2A27 bold text, #444441 body, #5F5E5A grey values/footers, #D9D7CD rules and spec-box border
- Drawing palette (warm greys): flange ring 0.94/0.93/0.90, flange plate 0.81/0.78/0.71, top faces 0.753/0.745/0.706, front faces 0.839/0.831/0.792, side faces 0.663/0.655/0.616, bottom rims 0.612/0.604/0.573, outlines 0.431/0.427/0.408, dashed leaders 0.612/0.604/0.573 (dash 3/2.25), spec box fill 0.96/0.95/0.93
- Projection: classic isometric, width axis 30 deg down-right, depth axis 30 deg down-left with 0.925 foreshortening, height straight down; assembly auto-scales to the drawing region (x 80-345, y 52-262)
- PDF author: the company `legal_name` from the company config. No logo, no images.

## Company config
Company fields come from `template-library/company.example.json` (or the file you pass with `--company`). Copy it, fill in your own company, and point `--company` at your copy.

Any string in the data file may contain `{{company.KEY}}`; the script replaces it with that key from the company config before building. The sample subtitle uses `{{company.dba}}` and `{{company.pm_name}}`. An unknown token stops the build with an error.

## Layout walkthrough
Page 1 (schedule): bold title; grey subtitle (project, company, who took the field sketches); thin rule; bold "Fittings (one per page following):"; one row per fitting (bold tag column + description line using the middle-dot separator, e.g. "Supply · 60×24 to 40×20 · 18" tall · sep flex 40×20"); thin rule near the bottom; up to two grey footer notes (fab spec that applies to every drop, flex/sq-to-round note).
Pages 2+ (one per fitting): isometric assembly on the left: flange ring + tan plate band + black screw dots at the curb top, top opening face, tapered transition body (light front wall, dark side wall, dark drop-bottom slab), exploded gap, separate flex piece drawn as a hatched box with bold "S" and "drive" joint marks, and for 3-piece drops an exploded square-to-round frustum ending in an ellipse. Right column: up to 6 callouts (bold label + grey value) connected by dashed leader lines with an anchor dot: 1" flange (4 sides)/screw to curb, Top opening WxD, 1.5" duct liner/internal (when lined), Drop bottom WxD, Flex (separate) WxD, Square-to-round note. Bottom: rounded spec box (30,279)-(480,345) with a bold summary line "{tag} · {service} · {piece} · Qty {n}" and up to 3 grey detail lines.

## Placeholders
All example values are fake.

| JSON key | type | required | example value | notes |
|---|---|---|---|---|
| output_filename | string | yes | "Sample_Elementary_Duct_Transition_ShopTicket.pdf" | pattern: {Job}_Duct_Transition_ShopTicket.pdf |
| output_dir | string | no | path | default _sample_output next to the script |
| pdf_title | string | no | "Sample Elementary Duct Transition Shop Ticket" | PDF metadata |
| schedule_title | string | yes | "Sample Elementary RTU Duct Transition Schedule" | |
| schedule_subtitle | string | yes | "Sample ISD, Sample Elementary School · {{company.dba}} · field sketches by {{company.pm_name}}" | middle dots, not dashes |
| footer_notes | string[] | no | see sample | max 2 lines on the schedule page; keep each under about 105 characters |
| fittings[].tag | string | yes | "RTU-1", "Room 101" | room/unit tag |
| fittings[].service | string | yes (may be "") | "Supply" | empty string drops it from the spec title |
| fittings[].piece | string | yes | "transition + separate flex" | |
| fittings[].qty | int | no | 1 | |
| fittings[].top_w, top_d | number | yes | 60, 24 | curb-top opening, inches |
| fittings[].bot_w, bot_d | number | yes | 40, 20 | drop bottom, inches |
| fittings[].height_in | number | yes | 18 | transition/drop height |
| fittings[].taper | string | no | "flush_left" | concentric (default), flush_left, flush_right |
| fittings[].liner_note | string | no | "1.5\" duct liner" | omit to skip the liner callout (3-piece drop style) |
| fittings[].liner_sub | string | no | "internal" | |
| fittings[].flange_note | string | no | "1\" flange (4 sides)" | default fixed wording |
| fittings[].flange_sub | string | no | "screw to curb" | |
| fittings[].flex | object | no | {"w":40,"d":20,"height_in":16} | separate flex piece; omit if none |
| fittings[].square_to_round | object | no | {"dia":10,"height_in":10,"note":"separate, to 10\"ø"} | 3-piece drops only |
| fittings[].schedule_line | string | yes | "Supply · 60×24 to 40×20 · 18\" tall · sep flex 40×20" | exact schedule-page wording |
| fittings[].spec_lines | string[] | yes | 3 lines, see sample | exact spec-box wording: dims line, alignment line, joints line |

## Fixed wording
- "Fittings (one per page following):"
- Callout labels: "1\" flange (4 sides)" / "screw to curb", "Top opening", "1.5\" duct liner" / "internal", "Drop bottom", "Flex (separate)", "Square-to-round"
- Joint marks "S" and "drive" on the flex piece
- Standard joints line: "Joints: S-cleat + drive (1\" flange at curb top only)"
- Separators are the middle dot (·) and the multiplication sign (×), never hyphens or dashes

## How to build
```
cd template-library/templates/duct-shop-ticket
py -3 build_duct_shop_ticket.py                                  (sample_data.json + company.example.json)
py -3 build_duct_shop_ticket.py mydata.json --company my_company.json
```
Output: `{output_dir}/{output_filename}` (multi-page PDF, 1 + number of fittings).

Requires: Python 3 with reportlab.

## Known variations
- 2-piece fittings (transition + flex) get 5 callouts; 3-piece drops (drop + flex + square-to-round) get 6 and no liner callout.
- The isometric is computed from the dimensions, so proportions track each fitting.
- Straight drops (top = bottom size) render as plain boxes; set taper "concentric".
- Pair the ticket with your own RFQ or cut list table when sending to the shop.
