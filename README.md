# Student OS Pro

A connected Notion system for student life — courses, grades, assignments, exams, work, money, and everything outside of class.

The product itself lives in Notion. This repository documents its architecture so the build is reproducible and the upcoming sales site has a reference.

---

## What it is

Most student templates are a prettier to-do list. This one is a relational system: courses feed assignments, assignments feed tasks, grades feed GPA automatically.

- **20 connected databases**
- **25 pre-built views** (tables, boards, calendars, galleries, lists)
- **Automatic GPA** from letter grades and credit hours
- **Live deadline countdowns** and visual progress bars
- Ships with realistic sample data so it demos immediately

---

## Architecture

All databases live on a hidden `⚙️ System Databases` page. Every user-facing page shows a *linked view* of those databases rather than the databases themselves. This keeps the product pages clean and means a user can restructure their navigation without breaking the data layer.

### Academic core

| Database | Key fields | Connects to |
| --- | --- | --- |
| Courses | Course, Semester, Credits, Instructor, Schedule, Grade, Status | Assignments, Exams, Materials, Notes, Study Projects, Goals, Semesters |
| Semesters | Semester, Term, Year | Courses |
| Assignments | Assignment, Due, Status, Priority, Progress, Score | Courses, Tasks |
| Exams | Exam, Date, Type, Study Status, Weight %, Score | Courses |
| Study Materials | Material, Type, Link, Files | Courses |
| Study Notes | Note, Date, Tags | Courses |
| Study Projects | Project, Status, Deadline | Courses, Tasks |
| Academic Goals | Goal, Category, Target Date, Status, Progress, Why It Matters | Courses |
| Tasks | Task, Due Date, Status, Priority, Category | Assignments, Projects, Skills |
| Skills To Learn | Skill, Status, Resources | Tasks |

### Work and money

| Database | Key fields | Connects to |
| --- | --- | --- |
| Jobs & Internships | Position, Company, Type, Status, Pay Rate, Applied Date | Work Shifts |
| Work Shifts | Shift, Date, Hours, Rate | Jobs |
| Finance Transactions | Description, Type, Category, Amount, Date | — |

### Personal

| Database | Key fields |
| --- | --- |
| Fitness Workouts | Workout, Date, Type, Duration, Exercises, Completed |
| Meal Plan | Meal, Date, Type |
| Grocery List | Item, Category, Quantity, Bought |
| Daily Journal | Entry, Date, Mood, Energy, Highlights, Gratitude |
| Books Library | Title, Author, Status, Rating, Key Ideas |
| Habits | Habit, Category, Goal, Active |
| Habit Log | Log, Date, Done |
| Contacts | Name, Type, Phone, Email, Last Contacted, Follow Up |

---

## The calculated layer

These formulas and rollups are what make the system automatic rather than manual.

**GPA pipeline** — the headline feature:

```
Courses.Grade Points   = ifs(Grade == "A+", 4.0, Grade == "A", 4.0, Grade == "A-", 3.7,
                             Grade == "B+", 3.3, Grade == "B", 3.0, Grade == "B-", 2.7,
                             Grade == "C+", 2.3, Grade == "C", 2.0, Grade == "C-", 1.7,
                             Grade == "D",  1.0, true, 0.0)

Courses.Quality Points = Grade Points × Credits

Semesters.Total Quality Points = rollup(Courses → Quality Points, sum)
Semesters.Total Credits        = rollup(Courses → Credits, sum)
Semesters.GPA                  = Total Quality Points ÷ Total Credits   (rounded to 2dp)
```

**Other calculated fields:**

| Field | Definition |
| --- | --- |
| `Assignments.Days Remaining` | `dateBetween(Due, now(), "days")` |
| `Assignments.Progress Bar` | `repeat("█", Progress/10) + repeat("░", 10 - Progress/10)` |
| `Finance.Signed Amount` | Income → `+Amount`, Expense → `-Amount` (so the column sums to a real balance) |
| `Work Shifts.Pay` | `Hours × Rate` |
| `Jobs.Total Earned` | `rollup(Shifts → Pay, sum)` |
| `Habits.Completion Rate` | `rollup(Log → Done, average)` |
| `Habits.Success Rate %` | `round(Completion Rate × 100)` |

Note: Notion's API does not serialize computed formula/rollup *results* — it returns opaque references. These were validated structurally (Notion rejects malformed formulas at write time) but the rendered values should be confirmed visually in the Notion UI.

---

## Page map

```
Student OS Pro
├── 🚀 Start Here            — onboarding, setup, FAQ
├── Dashboards               — navigation hub + GPA Overview
│   ├── 🎓 Student Area      — Courses, Schedule, Goals, Exams, Materials,
│   │                          Notes, Projects, Agenda, Tasks, Skills
│   ├── 💼 Jobs Area         — Part-time Job, Internships & Jobs
│   ├── 💳 Finance Manager   — Finance OS Pro
│   └── 🧬 Personal Area     — Fitness, Meals, Journal, Books, Habits, Contacts
├── Work Flow                — quick-action navigation
└── ⚙️ System Databases      — all 20 databases (hidden from navigation)
```

---

## Design decisions

**One database, many views.** Rather than duplicating data per page, each page renders a filtered view of a shared database. Adding an assignment anywhere makes it appear everywhere it's relevant.

**Two-way relations throughout.** Linking an assignment to a course automatically populates that course's Assignments field. Opening a course shows its complete picture with no manual upkeep.

**Log-based habit tracking.** Habits use a separate daily log table rather than weekday checkbox columns, so history is preserved and success rate is computed rather than eyeballed.

**Unified Jobs table.** Part-time work and internship applications share one database with a `Type` discriminator, filtered into separate views. A part-time job and a job application are the same object at different lifecycle stages.

**Sample data ships with the product.** An empty template forces a buyer to imagine how it works. Seeded courses, assignments, transactions, and habits let the system demonstrate itself, and the onboarding page tells users to clear it.

---

## Roadmap

- [ ] Sales landing page with Stripe checkout
- [ ] Product screenshots for the listing
- [ ] Duplicate-ready public share link
