# 🎓 MHT-CET COLLEGE PREDICTOR

<p align="center">

### Discover. Compare. Shortlist.

A data-driven web application for exploring **MHT-CET engineering colleges and branches** using CAP cutoff data, placement information, recruiter data, and location.

<br>

[🚀 **LIVE DEMO**](https://mht-cet-predictor-zainul-aabdeen.vercel.app/)
[💻 **SOURCE CODE**](https://github.com/zainul-aabdeen/MHT-CET-PREDICTOR-zainul-aabdeen)

</p>

<p align="center">

![Next.js](https://img.shields.io/badge/Next.js-16-black?style=for-the-badge\&logo=next.js)
![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge\&logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=for-the-badge\&logo=typescript)
![FastAPI](https://img.shields.io/badge/FastAPI-0.138-009688?style=for-the-badge\&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge\&logo=python)
![Vercel](https://img.shields.io/badge/Frontend-Vercel-black?style=for-the-badge\&logo=vercel)
![Render](https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge\&logo=render)

</p>

---

## 📰 THE IDEA

MHT-CET counselling means dealing with a huge amount of cutoff data, branches, categories, CAP rounds, colleges, and other factors.

This project was built to make that process easier.

Instead of jumping between multiple cutoff PDFs and spreadsheets, the predictor brings the information into one interface where you can:

**Enter your percentile → Apply filters → Explore colleges → Compare the data → Shortlist options**

---

# ⚡ LIVE DEMO

### 👉 [Open the MHT-CET College Predictor](https://mht-cet-predictor-zainul-aabdeen.vercel.app/)

> **⚠️ Important loading note**
>
> The frontend is hosted on **Vercel**, while the backend API is hosted on **Render's free tier**.
>
> Render automatically spins down a free web service after **15 minutes of inactivity**. When someone uses the app again after that period, Render has to start the backend before the request can be processed.
>
> ### What this means:
>
> 🟢 **Backend recently active** → normal response time
> 🟡 **Backend idle for 15+ minutes** → first request can be noticeably slow
> 🔄 **Cold start** → Render wakes the backend up
> 🚀 **After startup** → requests return normally
>
> So if the first search seems slow, **the application is usually just waking the backend up**.

---

# ✨ FEATURES

## 🎯 Percentile-Based Search

Enter your MHT-CET percentile and search for college/branch combinations whose historical cutoff percentile falls within the selected range.

A configurable **percentile buffer** can also be applied when exploring nearby options.

---

## 🏫 CAP Round Data

The backend currently works with:

```text
CAP 1
CAP 2
CAP 3
```

The loaded CAP datasets are filtered for the **2025 academic year** when the academic-year field is available.

Each result can include:

* College code
* College name
* Branch code
* Branch name
* CAP round
* Category
* Seat scope
* Cutoff rank
* Cutoff percentile

---

## 🔎 Advanced Filters

Customize your search using filters for:

| Filter               | Available         |
| -------------------- | ----------------- |
| 🎯 Target Percentile | ✅                 |
| 📈 Percentile Buffer | ✅                 |
| 🏷️ Category         | ✅                 |
| 💻 Branch            | ✅                 |
| 🏛️ CAP Round        | ✅                 |
| 🪑 Seat Scope        | ✅                 |
| 📍 Region            | ✅                 |
| 🧭 Current Location  | ✅                 |
| 🧑‍💼 Recruiters     | Backend supported |
| ↕️ Sorting           | ✅                 |

### Supported regions

```text
Mumbai
Navi Mumbai
Pune
Others
```

---

# 📍 LOCATION-AWARE RESULTS

The application can request your browser location and calculate the approximate distance between you and available colleges.

This makes it possible to sort results by:

```text
Closest
Farthest
```

Distance calculations are performed using geographical coordinates associated with the college dataset.

> 🔐 Location access is optional. The browser only provides coordinates when you explicitly allow location access.

---

# 💼 PLACEMENT INFORMATION

Where data is available, college results can include:

```text
Highest Package
Average Package
Median Package
Placement Percentage
Top Recruiters
```

This allows you to look beyond cutoff numbers and investigate the broader picture of each college.

> ⚠️ Placement statistics are provided for reference. They should not be interpreted as guaranteed salary or placement outcomes.

---

# 🧠 RECOMMENDATION SCORE

The application also calculates a **Recommendation Score** to help rank results.

It combines three signals:

```text
50% → Average Placement Package
30% → Distance
20% → Cutoff Compatibility
```

The score is designed to help prioritize results based on a combination of **placement potential, location, and percentile compatibility**.

### Important

This is a **rule-based scoring system**, not a machine-learning model.

The score is therefore best treated as a **ranking aid**, not an admission probability.

---

# 📊 SORTING

Results can be sorted using:

```text
Default
Recommendation Score
Highest Cutoff
Lowest Cutoff
Closest
Highest Package
Highest Placement %
```

This lets you look at the same dataset from different perspectives.

---

# 📥 EXPORT RESULTS

Found something useful?

Export your current results directly as a CSV file.

The export contains information including:

```text
College Code
College Name
Branch Code
Branch Name
Region
Distance
Highest Package
Average Package
Median Package
Placement %
Top Recruiters
CAP Round
Category
Seat Scope
Cutoff Rank
Cutoff Percentile
Recommendation Score
```

This makes it easier to continue comparing colleges in Excel, Google Sheets, or other tools.

---

# 🧩 HOW IT WORKS

```text
                    ┌──────────────────────┐
                    │   MHT-CET Percentile │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Search Filters    │
                    │                      │
                    │ Category             │
                    │ Branch               │
                    │ CAP Round            │
                    │ Seat Scope           │
                    │ Region               │
                    │ Location             │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     FastAPI API      │
                    │                      │
                    │ /api/options         │
                    │ /api/search          │
                    └──────────┬───────────┘
                               │
                               ▼
                ┌──────────────────────────────┐
                │      CAP + College Data      │
                │                              │
                │ Cutoffs                      │
                │ Locations                    │
                │ Placement Data               │
                │ Recruiters                   │
                └──────────────┬───────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Recommendation     │
                    │       Scoring        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    College Results   │
                    └──────────────────────┘
```

---

# 🛠️ TECH STACK

### Frontend

* **Next.js**
* **React**
* **TypeScript**
* **Tailwind CSS**
* **Zustand**
* **Axios / Fetch**
* **Lucide React**

### Backend

* **Python**
* **FastAPI**
* **Pandas**
* **NumPy**
* **Pydantic**
* **GeoPy**
* **Uvicorn / Gunicorn**

### Deployment

```text
Frontend  → Vercel
Backend   → Render
```

---

# 📁 PROJECT STRUCTURE

```text
MHT-CET-PREDICTOR-zainul-aabdeen/
│
├── backend/
│   ├── data/
│   │   ├── mht_cet_cap1_clean.csv
│   │   ├── cap2_clean.csv
│   │   ├── cap3_clean.csv
│   │   ├── colleges_by_region.csv
│   │   └── college_packages.csv
│   │
│   ├── data_loader.py
│   ├── main.py
│   ├── models.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── store/
│   │
│   ├── package.json
│   ├── next.config.ts
│   └── ...
│
├── parser.py
├── clean_csv.py
├── agent_research.py
├── background_research_agent.py
├── google_research_agent.py
├── check_counts.py
├── requirements.txt
└── ...
```

---

# 🔌 API

The FastAPI backend exposes two main endpoints:

### `GET /api/options`

Returns available search options such as:

* Categories
* Branches
* Seat allocations
* Seat scopes
* CAP rounds
* Recruiters
* Regions

### `POST /api/search`

Accepts search parameters such as:

```json
{
  "percentile": 93.88,
  "percentile_buffer": 2,
  "categories": [],
  "branches": [],
  "seat_scopes": [],
  "rounds": [],
  "regions": [],
  "recruiters": [],
  "lat": null,
  "lng": null,
  "sort_by": "Recommendation Score"
}
```

and returns matching college/branch results with cutoff and placement information.

---

# 🚀 RUN LOCALLY

## 1. Clone the repository

```bash
git clone https://github.com/zainul-aabdeen/MHT-CET-PREDICTOR-zainul-aabdeen.git

cd MHT-CET-PREDICTOR-zainul-aabdeen
```

---

## 2. Run the backend

```bash
cd backend

pip install -r requirements.txt

python main.py
```

The FastAPI server runs locally on:

```text
http://localhost:8000
```

---

## 3. Run the frontend

Open another terminal:

```bash
cd frontend

npm install

npm run dev
```

Then open:

```text
http://localhost:3000
```

The Next.js configuration proxies `/api/*` requests to the deployed backend during the configured production setup.

---

# 📚 DATA

The project uses cleaned CAP cutoff datasets along with separate college location and placement datasets.

### Core cutoff data

```text
mht_cet_cap1_clean.csv
cap2_clean.csv
cap3_clean.csv
```

### Supporting data

```text
colleges_by_region.csv
college_packages.csv
```

The location dataset contains college coordinates and region classifications, while the package dataset contains placement-related information such as package values, placement percentage, and recruiters.

---

# ⚠️ DISCLAIMER

This project is an **exploration and decision-support tool**, not an official admission authority.

Historical cutoff data can help students understand previous trends, but **actual admission cutoffs can change from one CAP cycle to another**.

Admission depends on factors such as:

* Candidate category
* Seat type
* CAP round
* Choice filling
* Competition
* Vacancies
* Cutoff movement
* Official admission rules

### Always verify important information with the official MHT-CET / State CET Cell sources before making your final choice.

---

## 💼 PLACEMENT DATA DISCLAIMER

Placement information is collected and organized from available sources and may be incomplete, outdated, or inaccurate.

Package figures should therefore be treated as **reference information**, not guaranteed outcomes.

---

# 🧪 PROJECT STATUS

```text
🟢 Live
🟢 Deployed
🟢 Searchable
🟢 CAP 1 / CAP 2 / CAP 3
🟢 Location filtering
🟢 Placement data
🟢 Recommendation scoring
🟢 CSV export
```

---

# 🗺️ FUTURE IMPROVEMENTS

Ideas for future versions:

```text
□ More historical CAP years
□ Improved cutoff trend analysis
□ Better recommendation methodology
□ College comparison mode
□ Better mobile experience
□ More comprehensive placement datasets
□ Faster / always-on backend
□ More automated data collection
```

---

# 👨‍💻 AUTHOR

### Zainul Aabdeen

Built as a practical project to make the MHT-CET college-selection process less painful and more data-driven.

<p align="center">

**No magic. No fake AI claims. Just data, filters, and useful comparisons.**

<br><br>

⭐ **If this project helped you, consider starring the repository.**

</p>
