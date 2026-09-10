# Student OS Pro

A connected Notion system for student life — courses, grades, assignments, exams, work, money, and everything outside of class.

The product itself lives in Notion. This repository documents its architecture so the build is reproducible and the upcoming sales site has a reference.

---

## What it is

Most student templates are a prettier to-do list. This one is a relational system: courses feed assignments, assignments feed tasks, grades feed GPA automatically.

- **25 connected databases**
- **Every view pre-built** — tables, boards, calendars, timelines, galleries, lists, 7 charts and a form
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
| Class Sessions | Session, Day, Time, Type, Location, Instructor | Courses |
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
│   ├── 💼 Jobs Area         — Part-time Job, Internships & Applications
│   ├── 💳 Finance Manager   — one ledger, plus budgets that warn at 80%
│   └── 🧬 Personal Area     — Fitness, Meals, Journal, Books, Habits, Contacts
└── ⚙️ System Databases      — 24 of the 25 databases (Assignments lives
                             under Student Area)
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

## Visual design system

Researched against the templates the category actually rewards. The recurring
advice from designers who build these for a living is blunt: *single-column
pages read like notes, multi-column pages read like systems*, and repeating one
callout style across a page is what makes a layout look designed rather than
typed. Both are applied here.

**Every page opens with one hero callout** — a coloured card carrying the
page's promise in a sentence, never a bare heading.

**Colour is assigned by area, not by mood**, so the palette reads as one system:

| Area | Colour |
| --- | --- |
| Academic — courses, notes, materials, projects | blue |
| Urgency — agenda, tasks, exams, habits | red / orange |
| Study Hub, journal, skills, jobs | purple |
| Finance, goals | green |
| Personal — fitness, meals, books | pink / brown |

**Navigation is a card grid, not a list.** The Dashboard and the front page
both open with two rows of three linked cards, each stating what the
destination is *for* rather than only naming it.

**Icons are emoji**, one per page, never repeated across two pages in the same
area. Notion's built-in icon set is avoided: setting one through the API
converts it into an external URL reference that cannot be verified.

**Covers** exist for all 26 pages but are deliberately not applied. Each shares
one ground — deep navy, colour blooms in screen blend, a faint grid, vignette,
grain — with the hue family carrying the area and a thin-line motif carrying the
page: a timetable grid for Class Schedule, a funnel for the internship pipeline,
a bar breaking a dashed limit line for Finance, the forgetting curve interrupted
by reviews for Study Hub. Motifs sit right of centre and inside the middle band,
because Notion crops a cover to roughly that band and draws the page icon and
title over its lower left. Regenerate with `python3 tools/gen_covers.py`.

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
assets/covers  — one cover per page: editable SVG source + rendered JPEG
tools/         — gen_covers.py, which draws and encodes them
site/          — bilingual sales page (built, then paused at the owner's
                 request; not deployed, no checkout connected)
marketing/     — Instagram carousel generator (paused with the site)
```

---

## Known limitations

- **Page covers take a URL, not an upload.** The API rejects `file-upload://`
  for a cover, but it accepts any external HTTPS URL, so covers *can* be set
  programmatically — an earlier note in this file said otherwise and was wrong.
  The art in `assets/covers/` is committed and served from raw.githubusercontent
  at a pinned commit SHA (immutable, so a renamed branch can never break a
  buyer's covers). Applying them is a per-page call; today none are applied
  except the root page's original Unsplash cover, at the owner's request.
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
- **Views cannot be deleted via the API.** There is no delete-view operation, so
  a junk view can only be renamed and reconfigured into something useful, or
  removed by hand in the Notion UI.
- **An orphaned data source can become unreachable.** The Assignments database
  carries a second, empty data source left over from the original workspace.
  Both `in_trash` and `title` updates against it return `404 object_not_found`,
  so it can only be removed through the Notion UI. The database's own title was
  set explicitly to stop it rendering as *"Assignments and New data source"*.

---

## Pre-launch audit

A full page-by-page verification pass was run before launch. Every buyer-facing
claim was checked against the actual schema — each property, view and status
option named in the copy was confirmed to exist. Defects found and fixed:

| Class | Instances | Examples |
| --- | --- | --- |
| Copy contradicted layout | 3 | Agenda promised ⭐ Focus was "the last board" when it was 4th of 6; Weekly Review named a view *Focus — by urgency* that does not exist |
| Leftover content from the original workspace | 4 | A page titled **WORK** containing one pasted image, sitting between Agenda's boards; stray `📘 Book Overview` and `🔥 Habit Overview` text above hero callouts; an empty list bullet opening Part-time Job |
| Unfinished wireframe text | 1 | Books Library ended on a dangling `📊 Rating:` label |
| False statement to the buyer | 1 | System Databases claimed to be "intentionally hidden from the main navigation" while listed on the root page |
| Duplicated copy | 3 | Dashboard Quick Actions listed all five actions twice; Study Notes and Academic Goals restated their own hero callouts |
| Flat pages off the design system | 5 | Finance Manager, Part-time Job, Internships, Fitness, Habit Tracker, Contacts used plain emoji-prefixed text where every other page uses callout columns |
| Cosmetic cruft | 12 | Stray `<empty-block/>` filler; a doubled ⚙️ in the admin page title; 🧠 used by two sibling pages |

**Deleted as neither important nor useful:**

- **Work Flow** — a 25-button launcher whose own copy admitted it "mirrors the
  Dashboard exactly" and warned buyers that its buttons might not "jump where
  you expect". The buttons were unreadable through the API and therefore
  unverifiable; shipping a page that tells a paying customer its links may be
  broken is worse than not shipping it.
- **WORK** — a leftover page holding a single pasted image.

**Left in place deliberately:** *Basic Student OS*, a separate half-built product
in the same workspace. It is out of scope for Student OS Pro and is the owner's
to keep or delete — not something to remove during a cleanup of a different
product.

### Requires the Notion UI (the API cannot do these)

1. Delete the two remaining junk views on the **Assignments** database: an
   unnamed empty `dashboard` view, and an unnamed table bound to the orphaned
   data source.
2. Delete the orphaned **"New data source"** on that same database.
3. Decide on covers. The art exists and the URLs resolve; nothing is applied.
4. Confirm the GPA renders as expected — the API cannot read computed values.
