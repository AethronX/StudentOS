# Student OS Pro

A connected Notion system for student life — courses, grades, assignments, exams, work, money, and everything outside of class.

The product itself lives in Notion. This repository documents its architecture so the build is reproducible and the upcoming sales site has a reference.

---

## What it is

Most student templates are a prettier to-do list. This one is a relational system: courses feed assignments, assignments feed tasks, grades feed GPA automatically.

- **24 connected databases**
- **42 pre-built views** (tables, boards, calendars, timeline, galleries, lists, 7 charts, a form)
- **Automatic GPA** from letter grades and credit hours
- **Self-updating urgency** — everything with a date tags itself Overdue / Today / This week
- Mobile-first: every view capped at three visible columns with the title frozen
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
| Flashcards | Question, Answer, Deck, Last Reviewed, Reps, Ease, Retired | Courses |
| Study Sessions | Session, Date, Minutes, Technique, Focus, What I covered | Courses |
| Tasks | Task, Due Date, Status, Priority, Category | Assignments, Projects, Skills |
| Skills To Learn | Skill, Status, Resources | Tasks |

### Work and money

| Database | Key fields | Connects to |
| --- | --- | --- |
| Jobs & Internships | Position, Company, Type, Status, Pay Rate, Applied Date | Work Shifts |
| Work Shifts | Shift, Date, Hours, Rate | Jobs |
| Finance Transactions | Description, Type, Category, Amount, Date | Budgets |
| Budgets | Budget, Month, Category, Limit | Finance Transactions |

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

**Urgency engine** — the reason the system tells you what matters instead of just storing it:

```
Tasks.Due Status  = ifs(Status == "Done",          "5 · Done",
                        empty(Due Date),            "6 · No date",
                        daysUntil(Due Date) <  0,   "1 · Overdue",
                        daysUntil(Due Date) == 0,   "2 · Today",
                        daysUntil(Due Date) <= 7,   "3 · This week",
                        true,                       "4 · Later")
```

Assignments carry the same field; Exams carry `Countdown` (Today / This week /
This month / Later / Past). The numeric prefixes exist so that a plain
ascending sort puts overdue work first — Notion's API cannot create relative
date filters ("due today"), and silently drops `GROUP BY` on a formula
property, but it *does* sort by one. Because the formula reads `now()`, the
ordering re-evaluates every day and never goes stale.

| Field | Definition |
| --- | --- |
| `Assignments.Days Remaining` | `dateBetween(Due, now(), "days")` |
| `Assignments.Progress Bar` | `repeat("█", Progress/10) + repeat("░", 10 - Progress/10)` |
| `Finance.Signed Amount` | Income → `+Amount`, Expense → `-Amount` (so the column sums to a real balance) |
| `Work Shifts.Pay` | `Hours × Rate` |
| `Jobs.Total Earned` | `rollup(Shifts → Pay, sum)` |
| `Habits.Completion Rate` | `rollup(Log → Done, average)` |
| `Habits.Success Rate %` | `round(Completion Rate × 100)` |
| `Courses.Study Minutes` | `rollup(Study Sessions → Minutes, sum)` |
| `Budgets.Spent` | `rollup(Transactions → Amount, sum)` |
| `Budgets.Status` | 🟢 on track · 🟡 past 80% of limit · 🔴 over |
| `Books.Progress` | bar + percentage from Current Page ÷ Pages |

**Spaced repetition** — the flashcard scheduler:

```
Interval      = Again → 1 day
                Hard  → max(1, Reps × 1.2)
                Good  → max(2, Reps × 2.5)
                Easy  → max(4, Reps × 4)

Next Review   = Last Reviewed + Interval days
Review Status = New / Due now / Soon / Scheduled / Retired
```

The student rates a card and increments Reps; the schedule follows. Notion has
no way to mutate a property from a formula, so the interval is derived from
`Reps × Ease` rather than compounding a stored value — the practical behaviour
matches SM-2 closely enough while staying entirely declarative.

Note: Notion's API does not serialize computed formula/rollup *results* — it returns opaque references. These were validated structurally (Notion rejects malformed formulas at write time) but the rendered values should be confirmed visually in the Notion UI.

---

## Page map

```
Student OS Pro
├── 🚀 Start Here            — onboarding, setup, FAQ
├── 🔁 Weekly Review         — the 10-minute ritual that keeps it alive
├── 🏠 Dashboard             — navigation hub + GPA Overview
│   ├── ⚡ Quick Actions     — capture a task, note, assignment, exam, material
│   ├── 🎓 Student Area      — Courses, Schedule, Goals, Exams, Materials,
│   │                          Notes, Projects, Agenda, Tasks, Skills
│   ├── 🧠 Study Hub         — self-scheduling flashcards, session log, chart
│   ├── 💼 Jobs Area         — Part-time Job, Internships & Jobs
│   ├── 💳 Finance Manager   — Finance OS Pro
│   └── 🧬 Personal Area     — Fitness, Meals, Journal, Books, Habits, Contacts
├── Work Flow                — quick-action navigation
└── ⚙️ System Databases      — all 20 databases (hidden from navigation)
```

---

## Competitive positioning

Surveyed against the established Notion student templates (Student OS by
heyismail, Notion x Students, University Hub, Janice Studies' dashboard, and
the spaced-repetition flashcard templates on Notion's marketplace). Four gaps
recur across the category, and each maps to a specific decision here:

**1. "Templates stop at planning."** The most common criticism of the category
is that deadlines get stored and then sit buried inside a page — nothing tells
you what matters today. Answered by the urgency engine: every dated item tags
itself and views sort on it, so the front of every list is the work that is
actually urgent.

**2. Flashcards in Notion are usually fake.** Nearly every "spaced repetition"
template is a toggle that hides an answer. That is active recall, but with no
scheduling it is only half the method — you re-review what you already know.
Ours computes an interval and a next-review date from your own rating. This is
the sharpest differentiator, because it is the feature most often claimed and
least often actually implemented.

**3. Templates get abandoned around week three.** A 23-database workspace
handed over all at once is a reliable way to make someone quit. Start Here
therefore prescribes three pages for week one and explicitly tells the user to
ignore and delete the rest. No competitor does this; they showcase everything,
which is good for a sales page and bad for retention.

**4. "More clicks to track an assignment than to do it."** Capture friction
kills systems. Answered with a form view for one-tap mobile capture and Quick
Action pages that open straight into the right database.

Where the category is already strong — grade calculators, assignment trackers,
reading lists — this matches rather than reinvents.

**Feedback, not just storage.** Seven chart views turn logged data back into
something you can act on: where study hours actually went, where the money
went, how the term actually felt, which courses are being avoided, and how
credits are distributed across grades. Most templates in this category store
data and never show it back.

---

## Design decisions

**One database, many views.** Rather than duplicating data per page, each page renders a filtered view of a shared database. Adding an assignment anywhere makes it appear everywhere it's relevant.

**Two-way relations throughout.** Linking an assignment to a course automatically populates that course's Assignments field. Opening a course shows its complete picture with no manual upkeep.

**Log-based habit tracking.** Habits use a separate daily log table rather than weekday checkbox columns, so history is preserved and success rate is computed rather than eyeballed.

**Unified Jobs table.** Part-time work and internship applications share one database with a `Type` discriminator, filtered into separate views. A part-time job and a job application are the same object at different lifecycle stages.

**Sample data ships with the product.** An empty template forces a buyer to imagine how it works. Seeded courses, assignments, transactions, and habits let the system demonstrate itself, and the onboarding page tells users to clear it.

**Mobile is a constraint, not a feature.** Notion tables scroll sideways forever on a phone, which is where students actually check their work. Every view is capped at three visible properties with the title frozen, and boards and calendars are chosen over tables wherever the data suits them.

**Emoji icons over Notion's built-in icon set.** Setting a built-in icon through the API converts it to an external URL reference; emoji are native, render identically on every platform, and cannot break.

---

## Repository layout

```
README.md      — this document
assets/covers  — cover art as PNG, for setting Notion page covers by hand
site/          — bilingual sales page (built, then paused at the owner's
                 request; not deployed, no checkout connected)
marketing/     — Instagram carousel generator (paused with the site)
```

---

## Known limitations

- **Page covers must be set by hand.** Notion's API accepts only external HTTPS
  URLs for covers — it rejects uploaded files — so the generated PNGs in
  `assets/covers/` have to be applied through the Notion UI.
- **Formula and rollup *results* are not readable through the API.** It returns
  opaque references, so computed values (GPA, urgency tags) were verified
  structurally rather than by reading them back. Confirm them visually in Notion.
- **Database templates cannot be created via the API**, so a new course page
  opens blank rather than pre-structured.
- **Button blocks cannot be created via the API** either — they read back as an
  unknown block type. One-tap "review this card" grading would otherwise be a
  button; today it is two field edits.
- **`GROUP BY` on a formula property is silently dropped.** The API accepts the
  request and returns a view with no grouping. Sorting on a formula does work,
  which is why the status labels carry numeric prefixes.
