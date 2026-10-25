# Review 1: System Requirements Specification (SRS) & Scope

## 1. System Scope & Objectives
The system addresses accessibility barriers in educational and enterprise attendance logging. It provides robust CRUD management and integrates universal design principles to ensure usability for individuals with visual impairments, motor challenges, and screen glare environments.

## 2. Functional Requirements
- **FR-01 (Create):** Register student with unique Roll No, Name, and Section. Poka-Yoke validation prevents blank or duplicate records.
- **FR-02 (Read):** Query and render attendance records in real time with dynamic search filtering.
- **FR-03 (Update):** Update attendance status (`Present`, `Absent`, `Late`) via mouse click or keyboard shortcuts.
- **FR-04 (Delete):** Safe record removal with confirmation dialog.
- **FR-05 (Accessibility):** Theme engine supporting Light, Dark, and High Contrast; dynamic font scaling across 3 preset tiers.

## 3. Non-Functional Requirements
- **NFR-01 (Accessibility Standard):** Conformance to WCAG 2.1 level AAA for High Contrast mode (contrast ratio $\ge 7:1$).
- **NFR-02 (Keyboard Traversal):** 100% of interactive components accessible without mouse input.
- **NFR-03 (Data Integrity):** SQLite schema constraints enforcing foreign keys and unique constraints per student per date.
