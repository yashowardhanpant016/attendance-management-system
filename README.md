# BBAT104: Fundamentals of TQM – Course Project
**Student Name:** Yashowardhan Pant  
**Section:** CSE-B  
**Baseline System:** Attendance Management System (Executive Pro Edition)  
**Assigned Quality Goal:** Q12 - Improve Accessibility  
**Target Assessment:** 70 Raw Marks (BTech Project Submission)

---

## 📌 Project Overview
This project delivers a specialized, enterprise-grade **Attendance Management System** engineered in **Python / Tkinter** and **SQLite3**, featuring an executive navigation dashboard and systematically augmented with five core accessibility features under **Q12: Improve Accessibility**:

1. **Modern Executive Dashboard UI:** Responsive left navigation sidebar with 5 integrated sections (Dashboard, Student Directory, Attendance Roll Call, Reports & Analytics, Settings & Backup).
2. **High Contrast Mode (WCAG 2.1 AAA Compliant):** Pure Black `#000000` & Electric Yellow `#FFFF00` with high-visibility neon status tags (>19:1 contrast ratio) and persistent 3px visual focus outlines.
3. **Dynamic Font Resizing Engine:** Synchronous font scaling (`Normal`, `Large`, `X-Large`) that auto-adjusts Treeview row heights (`30px` → `40px` → `50px`), heading sizes, and widget padding without text truncation.
4. **Full Keyboard Navigation & Hotkey Suite:** Complete single-key shortcuts (`Ctrl+1`..`Ctrl+5`, `Ctrl+A`, `Ctrl+M`, `Ctrl+Z`, `Ctrl+D`, `Ctrl+H`, `Ctrl+T`, `Ctrl+S`, `F1`) and seamless 8-element navigation focus rings.
5. **Poka-Yoke & Mistake-Proofing Operations:** Real-time field validation, duplicate roll prevention, confirmation modals, atomic database backups, and multi-level attendance **Undo (`Ctrl+Z`)**.
6. **Advanced Reports & Quality Analytics:** Daily, monthly, and individual student attendance ledgers, embedded Matplotlib trend charts, CSV import/export, and automated **PDF Analytics Report** generation.

---

## 🚀 Quick Start & Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/BBAT104_TQM_YashowardhanPant.git
cd BBAT104_TQM_YashowardhanPant

# 2. Activate Python Virtual Environment
source .venv/bin/activate

# 3. Install dependencies (Matplotlib for SQC & trend charts)
pip install -r requirements.txt

# 4. Launch the application
python app.py
```

---

## 🧪 Automated Test Suite

Run the comprehensive unit, integration, and responsive layout test suite (19 automated tests covering CRUD, attendance marking, historical logs, undo, CSV import/export, disaster recovery, and responsive geometry at all font scales):

```bash
# Run all automated tests
python -m unittest discover tests

# Or run specific test modules
python -m unittest tests/test_database.py
python -m unittest tests/test_full_app.py
python -m unittest tests/test_responsive_layout.py
```

---

## ⌨️ Global Keyboard Shortcuts & Accessibility Guide

| Shortcut | Action | TQM / Ergonomic Impact |
| :--- | :--- | :--- |
| `Ctrl + 1` | Switch to Operations Dashboard | Instant view of enrolled totals, today's rate, and trend preview |
| `Ctrl + 2` | Switch to Student Directory | Fast registration, search, and modal record editing |
| `Ctrl + 3` | Switch to Daily Attendance | Immediate roll call access with historical date navigation |
| `Ctrl + 4` | Switch to Reports & Analytics | Access daily/monthly breakdowns and CSV/PDF export |
| `Ctrl + 5` | Switch to Settings & Backup | Appearance preferences and disaster recovery tools |
| `Ctrl + H` | Toggle High Contrast Mode | WCAG 2.1 AAA contrast ratio (>19:1) for low vision & glare |
| `Ctrl + D` | Toggle Low-Strain Dark Mode | Ergonomic palette mitigating ocular fatigue during extended shifts |
| `Ctrl + T` | Cycle Font Scaling | Seamless `Normal` ➜ `Large` ➜ `X-Large` without clipping |
| `Ctrl + A` | Focus Add Student Form | Immediate keyboard data entry entry point |
| `Ctrl + M` | Quick Mark Present | One-key attendance marking for selected student row |
| `Ctrl + Z` | Undo Last Attendance Mark | Poka-Yoke error correction reverting accidental submissions |
| `Ctrl + S` | Focus Search / Filter Box | Rapid keyboard directory querying |
| `Space` | Quick Mark Absent | Rapid single-key absent toggle on table rows |
| `Tab / Shift+Tab` | Traverse Focus Loop | Unbroken keyboard navigation with 3px visible focus indicator |
| `F1` | Accessibility Cheat Sheet | On-screen assistive reference modal |

---

## 📊 TQM & SQC Deliverables
- **Review 1:** System Requirements Specification (`docs/SRS_Review1.md`)
- **Review 2:** Functional Base System with CRUD & 5 Accessibility Features (`app.py`, `db.py`, `views/`)
- **Review 3:** SIPOC Flow, CTQ Tree, and FMEA Matrix with RPN tracking (`docs/FMEA_Review3.md`)
- **Review 4:** Pareto 80/20 Chart (`pareto_analysis_q12.png`), Fishbone analysis, and PDCA Cycle (`docs/PDCA_Review4.md`)
- **Documentation & GitHub Health:** Commit strategy checklist (`docs/COMMIT_HISTORY.md`)

### Keyboard Shortcuts Specification
- : High Contrast
- : Light/Dark Mode
- : Font Size Cycling
- : Focus Search Bar
- : Accessibility Documentation
