"""
AI Study Plan Generator
A customizable, intelligent study timetable generator with active recall optimization.
"""

import math
import re
import gradio as gr

# ==============================================================================
# CORE TIMETABLE SCHEDULING ALGORITHM
# ==============================================================================

def format_time_ampm(total_minutes):
    """Converts minutes from midnight to 12-hour AM/PM string."""
    h = (total_minutes // 60) % 24
    m = total_minutes % 60
    period = "AM" if (total_minutes // 60) % 24 < 12 else "PM"
    h12 = h if h <= 12 else h - 12
    if h12 == 0:
        h12 = 12
    return f"{h12:02d}:{m:02d} {period}"

def parse_start_time(start_str):
    """
    Parses any custom start time input by the user, such as:
    '09:30 AM', '9:30', '9 30', '10:30 AM', '10 30', '14:30', '2:15 PM', '9 AM', '9'
    """
    if not start_str or not str(start_str).strip():
        return 9 * 60  # Default 09:00 AM
    
    clean = str(start_str).strip().upper()
    
    # Check for AM / PM indicator
    period = None
    if "PM" in clean:
        period = "PM"
        clean = clean.replace("PM", "").strip()
    elif "AM" in clean:
        period = "AM"
        clean = clean.replace("AM", "").strip()
        
    # Match hours and optional minutes separated by space, colon, dot, or dash
    match = re.search(r'(\d{1,2})(?:[:\s\.\-](\d{1,2}))?', clean)
    if not match:
        return 9 * 60
        
    h = int(match.group(1))
    m = int(match.group(2)) if match.group(2) else 0
    
    # Handle 12-hour AM/PM conversion
    if period == "PM" and h < 12:
        h += 12
    elif period == "AM" and h == 12:
        h = 0
        
    # Bound to valid 24-hr day limits
    h = max(0, min(23, h))
    m = max(0, min(59, m))
    
    return h * 60 + m

def generate_study_plan(
    exam_goal,
    days_left,
    daily_hours,
    start_time_str,
    session_length_mins,
    include_breaks,
    break_length_mins,
    include_revision,
    subject_list,
    weak_areas,
    days_to_display
):
    daily_hours = float(daily_hours)
    days_left = int(days_left)
    days_to_display = int(days_to_display)
    session_length_mins = int(session_length_mins)
    break_length_mins = int(break_length_mins) if include_breaks else 0
    
    # Validation checks
    if daily_hours <= 0:
        return (
            "⚠️ **Input Error**: Daily study hours must be greater than 0.",
            "",
            "Daily study hours must be greater than 0.",
            None
        )
    
    if days_left <= 0:
        return (
            "⚠️ **Input Error**: Days remaining until exam must be at least 1.",
            "",
            "Days remaining must be at least 1.",
            None
        )

    # Clean and parse subjects
    raw_subjects = [s.strip() for s in subject_list.replace('\n', ',').split(',') if s.strip()]
    if not raw_subjects:
        raw_subjects = ["Core Subject (3)"]

    subjects_data = []
    for s in raw_subjects:
        match = re.search(r'\((\d+)\)', s)
        diff = int(match.group(1)) if match else 3
        clean_name = re.sub(r'\(\d+\)', '', s).strip()
        subjects_data.append({"name": clean_name, "difficulty": min(max(diff, 1), 5)})

    # Time budgeting calculations
    total_daily_study_mins = int(daily_hours * 60)
    rev_mins = int(total_daily_study_mins * 0.20) if include_revision else 0
    sub_study_mins = total_daily_study_mins - rev_mins
    
    total_weight = sum(s["difficulty"] for s in subjects_data)
    allocations = []
    accumulated_mins = 0
    for i, s in enumerate(subjects_data):
        if i == len(subjects_data) - 1:
            mins = sub_study_mins - accumulated_mins
        else:
            mins = int((s["difficulty"] / total_weight) * sub_study_mins)
            accumulated_mins += mins
        
        allocations.append({
            "name": s["name"],
            "difficulty": s["difficulty"],
            "daily_mins": mins
        })

    # Prepare Breakdown Table
    breakdown_md = f"### 📊 Daily Study Allocation Breakdown\n"
    breakdown_md += f"- **Target Goal:** {exam_goal}\n"
    breakdown_md += f"- **Total Daily Study Time:** **{daily_hours} Hours ({total_daily_study_mins} Minutes)**\n"
    breakdown_md += f"- **Total Window across {days_left} Days:** **{round(daily_hours * days_left, 1)} Hours**\n\n"
    breakdown_md += "| Subject | Difficulty | Allocated Time | % of Study Time | Focus Strategy |\n"
    breakdown_md += "| :--- | :---: | :---: | :---: | :--- |\n"
    
    for item in allocations:
        pct = round((item["daily_mins"] / total_daily_study_mins) * 100, 1)
        breakdown_md += f"| **{item['name']}** | {item['difficulty']}/5 | **{item['daily_mins']} mins** ({round(item['daily_mins']/60, 1)} hrs) | {pct}% | Active problem solving & concept maps |\n"
    
    if rev_mins > 0:
        rev_pct = round((rev_mins / total_daily_study_mins) * 100, 1)
        breakdown_md += f"| **Active Revision & Recall** | — | **{rev_mins} mins** ({round(rev_mins/60, 1)} hrs) | {rev_pct}% | Blurting, flashcards, and summary retrieval |\n"

    # Active recall methods bank
    hard_techniques = [
        "Feynman Technique (Teach the concept aloud without looking at notes)",
        "Deep Practice: Solve 5 high-difficulty previous year questions",
        "Derivation & Concept Mapping from memory",
        "Active Questioning: Answer end-of-chapter review problems"
    ]
    med_techniques = [
        "Flashcard Retrieval Practice & Formula Review",
        "Practice Problem Set: Complete standard numerical problems",
        "Blurting Method: Write down everything remembered on a blank sheet",
        "Summary condensation & identifying core rules"
    ]

    # Generate Schedule for each day
    schedule_md = f"### 🗓️ Complete Day-by-Day Study Timetable\n"
    schedule_md += f"*Custom Session Block: {session_length_mins} mins | Breaks: {'Enabled (' + str(break_length_mins) + ' mins)' if (include_breaks and break_length_mins > 0) else 'Disabled'}*\n\n"
    
    start_mins_base = parse_start_time(start_time_str)
    num_days = min(days_to_display, days_left)
    
    total_break_mins_daily = 0
    end_time_str_daily = ""

    full_text_export = f"AI STUDY PLAN FOR: {exam_goal}\n"
    full_text_export += f"Total Daily Study Hours: {daily_hours} hrs | Start Time: {start_time_str}\n"
    full_text_export += "="*70 + "\n\n"

    for day in range(1, num_days + 1):
        is_final_review = (day == days_left)
        day_title = f"Day {day} of {days_left}" + (" [Full Mock Test & Final Revision]" if is_final_review else "")
        schedule_md += f"#### 📅 {day_title}\n"
        schedule_md += "| Time Slot | Type | Subject / Activity | Specific Task & Method | Deliverable |\n"
        schedule_md += "| :--- | :---: | :--- | :--- | :--- |\n"
        
        full_text_export += f"--- {day_title} ---\n"
        
        curr_mins = start_mins_base
        daily_break_mins = 0
        
        # Build tasks queue for today
        today_tasks = []
        for item in allocations:
            remaining = item["daily_mins"]
            tech_idx = (day - 1) % len(hard_techniques) if item["difficulty"] >= 4 else (day - 1) % len(med_techniques)
            method = hard_techniques[tech_idx] if item["difficulty"] >= 4 else med_techniques[tech_idx]
            
            sub_part = 1
            while remaining > 0:
                block = min(remaining, session_length_mins)
                today_tasks.append({
                    "type": "Study",
                    "subject": item["name"],
                    "duration": block,
                    "method": f"{method} (Part {sub_part})" if remaining > session_length_mins else method,
                    "deliverable": f"Solve key problems / compile notes"
                })
                remaining -= block
                sub_part += 1
                if include_breaks and break_length_mins > 0:
                    today_tasks.append({
                        "type": "Break",
                        "subject": "Rest / Recharge",
                        "duration": break_length_mins,
                        "method": "Hydration, stretching, eye rest away from screens",
                        "deliverable": "Recharge focus"
                    })

        # Add revision block
        if rev_mins > 0:
            rem_rev = rev_mins
            rev_part = 1
            while rem_rev > 0:
                block = min(rem_rev, session_length_mins)
                today_tasks.append({
                    "type": "Revision",
                    "subject": "Active Recall & Revision",
                    "duration": block,
                    "method": f"Blurting method on today's topics (Focus on: {weak_areas if weak_areas else 'all topics'})",
                    "deliverable": "Completed 1-page summary sheet"
                })
                rem_rev -= block
                rev_part += 1
                if include_breaks and break_length_mins > 0:
                    today_tasks.append({
                        "type": "Break",
                        "subject": "Rest / Recharge",
                        "duration": break_length_mins,
                        "method": "Short break",
                        "deliverable": "Recharge"
                    })

        # Remove trailing break if present
        if today_tasks and today_tasks[-1]["type"] == "Break":
            today_tasks.pop()

        # Render tasks with clock timestamps
        for task in today_tasks:
            start_formatted = format_time_ampm(curr_mins)
            end_mins = curr_mins + task["duration"]
            end_formatted = format_time_ampm(end_mins)
            time_str = f"{start_formatted} - {end_formatted}"
            
            if task["type"] == "Break":
                schedule_md += f"| *{time_str}* | ☕ *Break* | *{task['subject']}* | *{task['method']}* | *{task['deliverable']}* |\n"
                full_text_export += f"  {time_str:<20} [BREAK] {task['subject']} ({task['duration']}m)\n"
                daily_break_mins += task["duration"]
            elif task["type"] == "Revision":
                schedule_md += f"| **{time_str}** | 🔄 **Recall** | **{task['subject']}** | {task['method']} | **{task['deliverable']}** |\n"
                full_text_export += f"  {time_str:<20} [REVISION] {task['subject']}: {task['method']}\n"
            else:
                schedule_md += f"| **{time_str}** | 📖 Study | **{task['subject']}** | {task['method']} | {task['deliverable']} |\n"
                full_text_export += f"  {time_str:<20} [STUDY] {task['subject']} ({task['duration']}m): {task['method']}\n"
            
            curr_mins = end_mins

        total_break_mins_daily = daily_break_mins
        end_time_str_daily = format_time_ampm(curr_mins)
        schedule_md += "\n"
        full_text_export += "\n"

    # Summary statistics card
    total_daily_window = total_daily_study_mins + total_break_mins_daily
    feasibility = "Balanced & Realistic" if daily_hours <= 6 else ("High Intensity / Tight" if daily_hours <= 9 else "Extreme Workload")
    start_time_display = format_time_ampm(start_mins_base)
    
    summary_md = f"""
### ⚡ Plan Overview & Timing Metrics
| Metric | Value |
| :--- | :--- |
| **Daily Study Time** | **{daily_hours} hrs ({total_daily_study_mins} mins)** (100% scheduled) |
| **Daily Break Time** | **{total_break_mins_daily} mins** ({'Enabled' if include_breaks else 'No breaks'}) |
| **Full Daily Schedule Window** | **{start_time_display} → {end_time_str_daily}** ({round(total_daily_window/60, 1)} hrs total span) |
| **Workload Feasibility** | **{feasibility}** |
"""

    # Save to export file for download
    export_filename = "study_plan.txt"
    with open(export_filename, "w", encoding="utf-8") as f:
        f.write(full_text_export)

    return summary_md, breakdown_md, schedule_md, export_filename

# ==============================================================================
# GRADIO UI SETUP
# ==============================================================================

def create_ui():
    custom_css = """
    .gradio-container { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 1250px; margin: auto; }
    .header-box { text-align: center; padding: 24px 10px; background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); color: white; border-radius: 12px; margin-bottom: 24px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    .header-box h1 { margin: 0; font-size: 28px; font-weight: 700; }
    .header-box p { margin: 8px 0 0 0; opacity: 0.95; font-size: 15px; }
    """

    with gr.Blocks(title="AI Study Plan Generator") as demo:
        gr.HTML("""
        <div class="header-box">
            <h1>🎓 AI Study Plan Generator</h1>
            <p>Customizable, intelligent timetable planner with active recall & Pomodoro breaks</p>
        </div>
        """)
        
        with gr.Row():
            # LEFT COLUMN: INPUTS & SETTINGS
            with gr.Column(scale=4):
                gr.Markdown("### ⚙️ Study Plan Inputs")
                
                exam_goal = gr.Textbox(
                    label="Exam / Target Goal",
                    value="Semester Final Exams",
                    placeholder="e.g. Midterm Exams, GATE 2027, Finals"
                )
                
                with gr.Row():
                    days_left = gr.Slider(label="Days Until Exam", minimum=1, maximum=60, step=1, value=7)
                    daily_hours = gr.Slider(label="Daily Study Hours Available", minimum=0.5, maximum=14.0, step=0.5, value=6.0)

                gr.Markdown("#### ⏰ Timing & Break Configuration")
                with gr.Row():
                    start_time = gr.Textbox(
                        label="Daily Start Time (e.g. 9:30 AM, 10:30, 9 30, 2:00 PM)",
                        value="09:30 AM",
                        placeholder="e.g. 09:30 AM, 10:30, 9 30"
                    )
                    session_length = gr.Dropdown(
                        label="Session Block Length (mins)",
                        choices=["30", "45", "50", "60"],
                        value="50"
                    )

                with gr.Row():
                    include_breaks = gr.Checkbox(label="Include Breaks between sessions", value=True)
                    break_length = gr.Slider(label="Break Length (mins)", minimum=5, maximum=30, step=5, value=10)

                include_revision = gr.Checkbox(
                    label="Include Dedicated 20% Active Recall / Revision Buffer",
                    value=True
                )

                gr.Markdown("#### 📚 Subjects & Topics")
                subject_list = gr.Textbox(
                    label="Subjects with Difficulty Rating (1-5)",
                    value="Data Structures (4), Database Systems (3), Computer Networks (3)",
                    placeholder="e.g. Data Structures (4), DBMS (3)"
                )
                
                weak_areas = gr.Textbox(
                    label="Weak Areas / Priority Topics",
                    value="Binary Search Trees, SQL Joins, Subnetting",
                    placeholder="e.g. Dynamic Programming, Normalization"
                )

                days_to_display = gr.Slider(
                    label="Number of Days to Display in Schedule",
                    minimum=1,
                    maximum=14,
                    step=1,
                    value=5
                )

                generate_btn = gr.Button("🚀 Generate Study Plan", variant="primary", size="lg")

            # RIGHT COLUMN: OUTPUTS
            with gr.Column(scale=6):
                summary_output = gr.Markdown()
                
                with gr.Tabs():
                    with gr.Tab("📅 Daily Timetable"):
                        schedule_output = gr.Markdown(value="*Click 'Generate Study Plan' to create your customized schedule.*")
                    
                    with gr.Tab("📊 Subject Allocation Breakdown"):
                        breakdown_output = gr.Markdown()
                
                download_btn = gr.DownloadButton("📥 Download Study Plan (.txt)", visible=True)

        # Event binding
        generate_btn.click(
            fn=generate_study_plan,
            inputs=[
                exam_goal,
                days_left,
                daily_hours,
                start_time,
                session_length,
                include_breaks,
                break_length,
                include_revision,
                subject_list,
                weak_areas,
                days_to_display
            ],
            outputs=[summary_output, breakdown_output, schedule_output, download_btn]
        )
    return demo

if __name__ == "__main__":
    app = create_ui()
    # Omit fixed server_port so Gradio automatically finds the first available open port
    app.launch(inbrowser=True)
