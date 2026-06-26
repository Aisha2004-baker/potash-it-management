#  IT Help Desk & Asset Management System

A professional, full-stack enterprise solution engineered during field training at the **Arab Potash Company**. This application optimizes internal IT infrastructure operations by seamlessly tracking hardware/software assets and automating corporate IT ticketing workflows.

##  Key Features

###  Admin Features (IT Operations Dashboard)
* **Real-time Analytics:** Tracks total, pending, and resolved tickets with dynamic success rate metrics.
* **Interactive Visualizations:** Powered by **Plotly** to represent support status (Pie charts) and issue distributions (Bar charts).
* **Enterprise Reporting:** Generates customized executive summaries and detailed technical reports directly exportable into **Excel (.xlsx)** sheets.
* **Ticket & Inventory Dispatch:** Automates ticket routing to dedicated IT departments (ERP, Development, Technical Support) and manages corporate device deployment.

###  Worker Features (Technical Staff Panel)
* **Dedicated Task Queue:** Displays chronological queues of assigned incidents.
* **SLA Time Tracking:** Manages internal workflow phases ("Start Progress" to "Finish & Close") with granular database timestamping.
* **Solutions Archive:** Historical repository tracking all solved issues per engineer.

---

##  Tech Stack & Architecture

* **Frontend & Web Interface:** [Streamlit](https://streamlit.io/) (Python Web Framework)
* **Database Management:** SQLite3 (Relational Database)
* **Data Engineering & Reports:** Pandas, XlsxWriter
* **Data Visualization:** Plotly Express & Graph Objects
* **Communication Layer:** SMTP via SSL (Automated Email Alerts)

---

##  Database Schema Quick Look

The application relies on a multi-relational database framework consisting of:
1. `Apc_EMP`: Stores technical personnel data, departmental roles, and authentication credentials.
2. `Employees`: Master dataset representing enterprise system users and corporate requisitions.
3. `APC_Devices`: Fleet tracking registry defining hardware specification, status, and assignments.
4. `APC_Tickets`: Incident operational ledger containing logs, priorities, operational durations, and solution mappings.

---

##  How to Run Locally
1. Clone this repository to your workstation:
   ```bash
   git clone [https://github.com/Aisha2004-baker/potash-it-management.git](https://github.com/Aisha2004-baker/potash-it-management.git)

