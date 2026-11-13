# House Style

The shared look for every template in this library. Company-specific values (name, letterhead, brand colors, font) come from your company config (`company.example.json` or the file you pass with `--company`). The neutral grays and fills below are fixed in the scripts.

There are THREE style families. Use the one the template's TEMPLATE.md declares; do not mix them.

## 1. Branded field documents (daily reports, project binder)

- Brand accent color `brand.accent_color` for the wordmark, rules and section headers (a darker shade of it for emphasis)
- Neutral palette: ink `#1A1A1A`, gray `#595959`, light gray `#BFBFBF`, faint fill `#F2F5EF`, row stripe `#F7F7F5`, alert red `#B23A2F`, amber `#B07A1E`
- Font `brand.font` (Helvetica by default in reportlab), letter portrait

## 2. Form documents (minutes, trackers, transmittals, cut lists, correspondence)

- Brand primary color `brand.primary_color` for titles, section headings and table header rows (white header text) and transmittal banners
- Light fills: `#E8EBF2` / `#DEEAF1` header rows, `#F4F6FA` row stripes; border `#B8C5D6`; gray `#595959`; red `#B00020`
- Arial in docx, Helvetica in reportlab PDFs

## 3. Grayscale signature documents (PCO, RFI, certified-mail notices)

- Deliberately grayscale Helvetica: black ink, gray `#999999` rules and labels, `#F3F3F3` fills
- These are signed or legal documents; do NOT add brand color bars or branding

## Special case: duct shop tickets

Warm gray-beige isometric palette (see templates/duct-shop-ticket/TEMPLATE.md). Duct fabrication releases always use the isometric shop-ticket style, not a full-size title-block drawing sheet.

## Universal rules

- NO EM DASHES OR EN DASHES anywhere: documents, file names, data files, emails. Use commas, periods or hyphens. Shop tickets use the middle dot (·) and multiplication sign (×) as separators.
- Letterhead, from the company config:
  ```
  [Company Legal Name]            (legal_name)
  [Address Line 1]                (address_line1)
  [City, State ZIP]               (city_state_zip)
  [Phone]  |  [Website]           (phone, website)
  ```
  Logo from `logo_path`; when it is `null`, the letterhead prints text only.
- Signature block, from the company config:
  ```
  [PM Name]                       (pm_name)
  [PM Title]                      (pm_title)
  [Company Legal Name]            (legal_name)
  [PM Phone]  |  [PM Email]       (pm_phone, pm_email)
  ```
  Signature image from `signature_path`; when it is `null`, leave a blank line to sign by hand.
- Dates: long form in letters ("June 24, 2026"), short form in form fields ("3/20/2026"), ISO in file names ("2026-06-15").
- Warranty closeout letters use Times New Roman 10 (the one non-Arial, non-Helvetica family).

## File naming patterns

Examples use the fictional job "Sample ES" (Sample Elementary School HVAC Replacement).

- `{Job}_{Doc}-{NNN}_{Slug}.pdf`, for example `Sample_ES_PCO-001_Room_101_Ductwork.pdf`, `Sample_ES_RFI-001_RTU-1_Curb_Out_Of_Level.pdf`
- `YYYY-MM-DD {Doc} NN - {Job short}.pdf`, for example `2026-06-11 Daily Report 01 - Sample ES.pdf`, `2026-06-17 Action Items - Sample ES.docx`
- `{Job}_{Doc}_{Party}_{Subject}.docx`, for example `Sample_ES_Transmittal_Sample_Supply_RTU_Submittal.docx`
- `{Job}_{FileRef}_Notice_of_Concealed_Condition_{Recipient}.pdf`
- `Warranty Close Out Letter - {Property}.docx`
