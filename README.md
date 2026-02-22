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

<img width="1919" height="901" alt="Screenshot 2026-02-22 102038" src="https://github.com/user-attachments/assets/bb625b80-3265-47a2-9edf-2d146d9b3176" />

<img width="893" height="841" alt="Screenshot 2026-02-22 102048" src="https://github.com/user-attachments/assets/3c060264-0d23-4a79-9955-fdc98357805c" />

<img width="1607" height="881" alt="Screenshot 2026-02-22 102117" src="https://github.com/user-attachments/assets/7bfc8d6c-c90b-4ead-a67b-a5ee32251c96" />

<img width="1581" height="628" alt="Screenshot 2026-02-22 102126" src="https://github.com/user-attachments/assets/5f0d917c-0307-4003-a6c1-74216a19c58e" />

<img width="1543" height="906" alt="Screenshot 2026-02-22 102204" src="https://github.com/user-attachments/assets/90964d3c-b301-42a8-bdbf-c11e1dbc3d5c" />

<img width="845" height="892" alt="Screenshot 2026-02-22 102333" src="https://github.com/user-attachments/assets/c9dc1b1a-f9ab-47e4-bf9f-5499179a8a80" />

<img width="955" height="890" alt="Screenshot 2026-02-22 102306" src="https://github.com/user-attachments/assets/c24a1685-10e3-48db-bca6-8d1e8bfb6c4c" />

<img width="894" height="861" alt="Screenshot 2026-02-22 102240" src="https://github.com/user-attachments/assets/07cdfed7-9082-4327-b7e9-a0d4879e2fa6" />

#### Diagrams

**System Architecture:**

<img width="569" height="300" alt="Screenshot 2026-02-22 041733" src="https://github.com/user-attachments/assets/18d14774-f961-4111-b834-912c7342b61f" />

*Flask handles routing and business logic, SQLite stores user responses, and the metrics engine calculates scores deterministically.*

**Application Workflow:**

<img width="422" height="559" alt="Screenshot 2026-02-22 041928" src="https://github.com/user-attachments/assets/6c446fb7-9ec9-4da5-822a-664c45260aea" />

---


#### Build Photos
![WhatsApp Image 2026-02-22 at 10 40 07 AM](https://github.com/user-attachments/assets/6dfd9ab7-49ac-42ff-a457-302e8bd84b43)
![WhatsApp Image 2026-02-22 at 10 38 04 AM](https://github.com/user-attachments/assets/1881c6f9-4f6c-44c5-afd4-5b33b9924943)
![WhatsApp Image 2026-02-22 at 10 41 48 AM](https://github.com/user-attachments/assets/1d4b1ec9-65c5-47ee-afab-fb65f0945e5e)
![WhatsApp Image 2026-02-22 at 10 37 50 AM](https://github.com/user-attachments/assets/990fce36-733e-4a1a-8054-d6eb66dd4d11)



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
[https://youtu.be/rVzudrmxjnI]

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

