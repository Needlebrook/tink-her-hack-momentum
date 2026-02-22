<p align="center">
  <img src="./img.png" alt="Project Banner" width="100%">
</p>

# Momentum 🎯

## Basic Details

### Team Name: Zivora

### Team Members
- Member 1: Celia Victor - Toc H Institute of Science And Technology
- Member 2: Navomi Jisha Sajie - Toc H Institute of Science And Technology

### Hosted Project Link
https://tink-her-hack-momentum.onrender.com/

### Project Description
Momentum is a structured self-assessment app that helps women measure and rebalance their daily workload across paid work, domestic labor, childcare, rest, and personal time. Through gentle, encouraging questions and visual metrics, it makes invisible cognitive labor visible.

### The Problem statement
Women often manage both professional and household responsibilities, but there is rarely a clear way to quantify that load or reflect on how it impacts long-term well-being. The invisible mental load of tracking schedules, emotions, and household needs goes unrecognized, leading to burnout.

### The Solution
Momentum guides users through lifestyle questions using buttons and sliders, then calculates four measurable indicators: Burnout Risk, Work-Life Balance, Mental Load Distribution, and Recovery Index. Each metric generates targeted, practical suggestions, making sustainable balance visible through compassionate feedback.

---

## Technical Details

### Technologies/Components Used

**For Software:**
- Languages used:  Python, HTML, CSS, JavaScript
- Frameworks used: Flask (backend), Bootstrap 5 (frontend)
- Libraries used: sqlite3 (database), uuid (session management), random (comment selection)
- Tools used: VS Code, Git, GitHub, Render (deployment)

**For Hardware:**
Not Applicable Here

## Features

List the key features of your project:
- Feature 1: 🔥 Burnout Risk Meter: Calculates physical and emotional strain based on sleep, work hours, and mental load
- Feature 2: Measures time distribution fairness between personal time, work, and domestic tasks
- Feature 3: Visualizes who carries the cognitive labor (planning, emotions, household tracking)
- Feature 4: Evaluates rest sustainability based on me-time quality and overload days

---

## Implementation

### For Software:

#### Installation
```bash
pip install -r requirements.txt
```

#### Run
```bash
python app.py 
```
or
```bash
flask run
```

## Project Documentation

### For Software:

#### Screenshots (Add at least 3)

<img width="629" height="514" alt="Screenshot 2026-02-22 040204" src="https://github.com/user-attachments/assets/24b252fc-5f55-4122-811c-51bb0c31e489" />
*Landing Page*

<img width="806" height="842" alt="Screenshot 2026-02-22 031922" src="https://github.com/user-attachments/assets/8b047784-5726-4ced-899b-ba5ea938df42" />
*questions*

<img width="1462" height="670" alt="Screenshot 2026-02-22 031749" src="https://github.com/user-attachments/assets/a803a4e5-2a3e-46ad-bc5c-08684c86df27" />
*Dashboard - I*

<img width="1445" height="615" alt="Screenshot 2026-02-22 031849" src="https://github.com/user-attachments/assets/a151fd1f-de42-4662-a4c4-aedcccf4d1ce" />
*Dashboard - II*

#### Diagrams

**System Architecture:**

<img width="569" height="300" alt="Screenshot 2026-02-22 041733" src="https://github.com/user-attachments/assets/18d14774-f961-4111-b834-912c7342b61f" />

*Flask handles routing and business logic, SQLite stores user responses, and the metrics engine calculates scores deterministically.*

**Application Workflow:**

<img width="422" height="559" alt="Screenshot 2026-02-22 041928" src="https://github.com/user-attachments/assets/6c446fb7-9ec9-4da5-822a-664c45260aea" />

---


#### Build Photos

![Team](Add photo of your team here)

![Components](Add photo of your components here)
*List out all components shown*

![Build](Add photos of build process here)
*Explain the build steps*

![Final](Add photo of final product here)
*Explain the final build*

---

## Additional Documentation

### For Web Projects with Backend:

#### API Documentation

**Base URL:** `https://momentum-t3c2.onrender.com` or `localhost:5000`

##### Endpoints

**GET /**
- **Description:** Landing Page
- **Response:**
Renders index.html

**POST /login**
- **Description:** Authenticates user (email-only for hackathon)
- **Request Body:**
```json
{
  "email": "user@example.com"
}
```
- **Response:**
Redirects to /questions (new user) or /dashboard (existing)

**POST /save_response**
- **Description:** Saves user's answer to a question
- **Request Body:**
```json
{
  "question_id": 1,
  "answer_option_id": 3,
  "answer_value": 5
}
```
- **Response:**
```json
{
  "success": true,
  "comment": "Great answer! You're doing well.",
  "session_complete": false,
  "answered_count": 2,
  "total_expected": 5
}
```

**GET /api/metrics/latest**
- **Description:** Gets user's most recent metrics
- **Response:**
```json
{
  "burnout": 42,
  "balance": 68,
  "mental_you": 75,
  "mental_partner": 25,
  "recovery": "Moderate"
}
```
- **Response:**
```json
{
  "status": "success",
  "message": "Operation completed"
}
```
---

## Project Demo

### Video
[https://youtu.be/pvjXJ85yUEI]

*Explain what the video demonstrates - key features, user flow, technical highlights*

---

## AI Tools Used (Optional - For Transparency Bonus)

If you used AI tools during development, document them here for transparency:

**Tools Used:** DeepSeek, ChatGPT

**Purpose:**     
- Generated boilerplate Flask route structures

- Assisted with debugging SQLite integration

- Helped formulate metric calculation logic

**Key Prompts Used:**
- "Create a Flask route that handles POST requests for saving user responses"
- "How do I calculate the relevent metrics based on sleep, work hours, and mental load?"
- "Extensive Debugging"

**Percentage of AI-generated code:** [Approximately 45%]

**Human Contributions:**
- Overall architecture design and planning
Mental load distribution metric concept (unique differentiator)

- UI/UX design and writing comments

- Database schema design and relationships

- Testing and debugging deployment issues

*Note: Proper documentation of AI usage demonstrates transparency and earns bonus points in evaluation!*

---

## Team Contributions

- Celia Victor :  Frontend development, Database Design & Population, Documentation
- Navomi Jisha Sajie: Frontend development, UI/UX design

---

## License

This project is licensed under the [MIT License] License - see the [LICENSE](LICENSE) file for details.

