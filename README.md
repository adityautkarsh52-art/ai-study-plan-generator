# 🎓 AI Study Plan Generator

An intelligent, customizable timetable planner that generates realistic, day-by-day study schedules with Pomodoro intervals and active recall techniques.

---

## ✨ Features

- **Custom Study Timing:** Input any custom study duration (e.g., 2 hours, 6 hours, 8 hours) — the algorithm schedules 100% of your allocated study time.
- **Optional Breaks & Sessions:** Customize session lengths (30, 45, 50, or 60 minutes) and enable/disable optional breaks (5 to 30 minutes).
- **Difficulty-Weighted Allocation:** Automatically calculates the optimal study time per subject based on individual difficulty ratings (1–5).
- **Active Recall Integration:** Integrates proven active learning methods (Feynman technique, blurting, practice sets, spaced repetition) instead of passive reading.
- **Dedicated Revision Buffer:** Optional 20% daily time reservation for self-testing and review.
- **Export & Download:** Save and download your generated study plan as a `.txt` file with one click.

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/YourUsername/ai-study-plan-generator.git
cd ai-study-plan-generator
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
python app.py
```

Open your browser and navigate to `http://127.0.0.1:7860`.

---

## 📦 Project Structure

```text
ai-study-plan-generator/
│
├── app.py              # Main Gradio application & scheduling engine
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Gradio** (Modern interactive web interface)
- **Constraint Satisfaction & Scheduling Algorithms**
