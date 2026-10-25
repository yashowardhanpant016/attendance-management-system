# Review 3: FMEA Risk Audit, SIPOC & CTQ Tree

## 1. SIPOC Process Map
| Supplier | Input | Process Step | Output | Customer |
| :--- | :--- | :--- | :--- | :--- |
| Faculty / Student | User credentials, UI preferences | 1. Configure Theme / Font | Accessible UI rendered | Faculty / Invigilator |
| SQLite Database | Student records, session date | 2. Query roster into minimalist view | Tabular student grid | Faculty |
| Keyboard / Input Device | Keypress events (`Tab`, `Space`, `Enter`) | 3. Record attendance status | Status tag (`P`/`A`/`L`) | Academic Administration |
| Business Logic Engine | Attendance matrix | 4. Validate constraints (no duplicate) | Validated transaction | Quality / Audit Team |
| SQLite Storage | Commit payload | 5. Persist attendance record | Updated database & summary | Student & Department |

## 2. Critical to Quality (CTQ) Tree
- **Customer Need:** Fast, error-free attendance logging accessible to individuals with visual or motor impairments.
  - **Quality Driver 1: Visual Accessibility**
    - *CTQ Metric:* WCAG Contrast ratio $\ge 7:1$ in High Contrast mode. Zero unreadable elements.
  - **Quality Driver 2: Operational Independence (Non-mouse)**
    - *CTQ Metric:* 100% CRUD tasks executable via keyboard. Max 3 keystrokes to primary actions.
  - **Quality Driver 3: Cognitive Simplicity**
    - *CTQ Metric:* UI element density $\le 7$ interactive elements in Minimalist layout.

## 3. Failure Mode and Effects Analysis (FMEA) Matrix
RPN = Severity ($S$) $	imes$ Occurrence ($O$) $	imes$ Detection ($D$)

| Failure Mode | Failure Cause | Effect | S | O | D | Pre RPN | Mitigation Strategy | Post S | Post O | Post D | Post RPN |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: |
| Low contrast illegibility | Incompatible color palette | Inaccurate attendance logging | 7 | 6 | 4 | **168** | Dedicated High Contrast toggle (`#000` & `#FF0`) | 7 | 1 | 2 | **14** |
| Font clipping on resize | Fixed frame widths | Truncated roll numbers / names | 6 | 7 | 3 | **126** | Responsive auto-expanding grid geometry | 6 | 2 | 2 | **24** |
| Lost keyboard focus | Missing focus bindings | Non-mouse users blocked | 8 | 5 | 5 | **200** | Strict traversal (`takefocus=True`) & visual rings | 8 | 1 | 2 | **16** |
| Duplicate student entry | Rapid multiple clicks | Skewed attendance counts | 5 | 6 | 3 | **90** | Database `UNIQUE` constraint & alert modals | 5 | 1 | 2 | **10** |
| Screen glare eye strain | High-luminance white screen | User fatigue and slow entry | 4 | 8 | 4 | **128** | Low-strain Dark Mode (`#1E1E1E` background) | 4 | 2 | 2 | **16** |
