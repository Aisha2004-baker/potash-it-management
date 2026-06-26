import streamlit as st
import base64
import pandas as pd
import sqlite3
from datetime import datetime
import smtplib
from email.message import EmailMessage
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO


def send_ticket_notification(it_email, ticket_id, requester,Category, problem, priority, it_name):
    
    SENDER_EMAIL = "aisha-helpdesk@gmail.com"
    SENDER_PASSWORD = "your-app-password-here" 
    
    subject = f" New Ticket Assigned: #{ticket_id}"
    body = f"""
    Hello {it_name},
    
    A new service ticket has been assigned to you.
    
    Ticket Details:
    --------------------------------------
    Ticket ID   : {ticket_id}
    Requester   : {requester}
    Device      : {Category }
    Problem     : {problem}
    Priority    : {priority}
    Created At  : {datetime.now().strftime("%Y-%m-%d %H:%M")}
    --------------------------------------
    
    Please log in to the APC System to start processing the request.
    
    Best Regards,
    APC Help Desk System
    """

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = it_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        
        print(f"Email Error: {e}")
        return False


DB_PATH = "APC.db"

def run_query(query, params=(), is_select=True):
  
    with sqlite3.connect(DB_PATH, timeout=20) as conn:
        if is_select:
            return pd.read_sql_query(query, conn, params=params)
        else:
            curr = conn.cursor()
            curr.execute(query, params)
            conn.commit()
            return None


st.set_page_config(page_title="APC Management System", layout="wide")

def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except: return ""

logo_path = "Controware-APC-SLA.jpg"
img_64 = get_base64(logo_path)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'u_id' not in st.session_state:
    st.session_state.u_id = "" 
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'show_profile' not in st.session_state: 
    st.session_state.show_profile = False
if 'dept' not in st.session_state:
    st.session_state.dept = "Dashboard"
if 'page' not in st.session_state:
    st.session_state.page = "Overview"

st.markdown(f"""
<style>
    .stApp {{
        background: linear-gradient(rgba(10,15,25,0.92), rgba(10,15,25,0.92)),
                    url("data:image/jpg;base64,{img_64}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    .profile-card {{
        background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(25px);
        padding: 30px; border-radius: 25px; border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center; color: white; margin: 40px auto; max-width: 600px;
    }}
    .metric-card {{
        background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 15px;
        border-top: 4px solid #16a085; text-align: center; color: white;
    }}
    .main-h1 {{ color: white; font-size: 2.8rem; font-weight: 800; }}
</style>
""", unsafe_allow_html=True)

if not st.session_state.logged_in:
    st.markdown("<div style='text-align:center; margin-top:60px;'><h1 style='color:white; font-size:3.2rem;'>Help Desk Management</h1></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form"):
            u = st.text_input("", placeholder="Employee ID")
            p = st.text_input("", type="password", placeholder="🔒 Password")
            if st.form_submit_button("LOG IN", use_container_width=True):
                user_df = run_query("SELECT * FROM Apc_EMP WHERE EMP_ID = ? AND EMP_password = ?", (u, p))
                if not user_df.empty:
                    st.session_state.logged_in = True
                    st.session_state.u_id = u
                    st.session_state.user_data = user_df.iloc[0]
                    role = str(user_df.iloc[0]['EMP_Role']).strip().lower()
                    if role == 'admin':
                        st.session_state.dept, st.session_state.page = "Dashboard", "Overview"
                    else:
                        st.session_state.dept, st.session_state.page = "Worker", "Problems"
                    st.rerun()
                else: st.error("Wrong ID or PASSWORD")

else:
    user = st.session_state.user_data
    is_admin = str(user['EMP_Role']).strip().lower() == 'admin'

    with st.sidebar:
        st.markdown(f"<h3 style='color:white;'>Welcome, {user['EMP_Name']}</h3>", unsafe_allow_html=True)
        if st.button("My Profile", use_container_width=True): 
            st.session_state.show_profile = True
            st.rerun()
        if st.button("Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        st.markdown("---")
        if is_admin:
            dept_options = ["Dashboard", "Call Operations", "Assets Management"] 
            current_index = dept_options.index(st.session_state.dept) if st.session_state.dept in dept_options else 0
            st.session_state.dept = st.sidebar.selectbox("Department", dept_options, index=current_index)
            
          
            if st.session_state.dept == "Call Operations":
                st.session_state.page = "Call Information"
            elif st.session_state.dept == "Assets Management":
                st.session_state.page = "Devices"
            else:
                st.session_state.page = "Overview"
    
            

    if st.session_state.show_profile:
        st.markdown(f"""
            <div class='profile-card'>
                <h2>User Profile</h2>
                <div class='info-row'><span class='info-label'>Name:</span><span>{user['EMP_Name']}</span></div>
                <div class='info-row'><span class='info-label'>ID:</span><span>{user['EMP_ID']}</span></div>
                <div class='info-row'><span class='info-label'>Email:</span><span>{user['EMP_Email']}</span></div>
                <div class='info-row'><span class='info-label'>Role:</span><span>{user['EMP_Role']}</span></div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("⬅ Back"): st.session_state.show_profile = False; st.rerun()

    elif st.session_state.dept == "Dashboard" and is_admin:
        st.markdown("<h1 class='main-h1'>IT Operations Dashboard</h1>", unsafe_allow_html=True)
        
       
        df_all = run_query("SELECT * FROM APC_Tickets")
        
        if not df_all.empty:
            
            m1, m2, m3, m4 = st.columns(4)
            total_t = len(df_all)
            open_t = len(df_all[df_all['STATUS'].isin(['Active', 'In Progress'])])
            closed_t = len(df_all[df_all['STATUS'] == 'Closed'])
            
            m1.metric("Total Tickets", total_t)
            m2.metric("Pending/Open", open_t, delta_color="inverse")
            m3.metric("Resolved", closed_t)
            m4.metric("Success Rate", f"{(closed_t/total_t*100):.1f}%" if total_t > 0 else "0%")

            st.markdown("---")
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1.5, 1])
            with col_btn2:
                if st.button("Create New Service Ticket", use_container_width=True, type="primary"):
                    st.session_state.dept, st.session_state.page = "Call Operations", "Call Information"
                    st.rerun()

            st.markdown("---")

           
            g1, g2 = st.columns(2)

            with g1:
                st.markdown("####  Support Status (Pie Chart)")
                fig_status = px.pie(df_all, names='STATUS', hole=0.4, 
                                    color_discrete_map={'Closed':'#27ae60', 'Active':'#e74c3c', 'In Progress':'#f1c40f'})
                st.plotly_chart(fig_status, use_container_width=True)

            with g2:
                st.markdown("#### Tickets by Issue Type (Bar Chart)")
                fig_prob = px.bar(df_all.groupby('Problem').size().reset_index(name='count'), 
                                  x='Problem', y='count', color='Problem', template="plotly_dark")
                st.plotly_chart(fig_prob, use_container_width=True)

            st.markdown("---")
            
            
            st.markdown("###  Professional Reports Generation")
            
            report_choice = st.selectbox("Select Report Type", 
                                        ["All calls between Two dates (Summary)", 
                                         "All calls between Two dates (Detailed)", 
                                         "Calls By help desk User"])

            
            def to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Sheet1')
                return output.getvalue()

            if "Two dates" in report_choice:
                c1, c2 = st.columns(2)
                start_date = c1.date_input("Start Date", datetime.now())
                end_date = c2.date_input("End Date", datetime.now())
                
                if st.button("Generate Date Range Report"):
                   
                    df_all['CREATED_AT_DT'] = pd.to_datetime(df_all['CREATED_AT'], dayfirst=True, errors='coerce').dt.date
                    filtered_df = df_all[(df_all['CREATED_AT_DT'] >= start_date) & (df_all['CREATED_AT_DT'] <= end_date)]
                    
                    if not filtered_df.empty:
                        if "Summary" in report_choice:
                            
                            summary = filtered_df.groupby('EMP_Name').agg(
                                Total_Tickets=('TICKET_ID', 'count'),
                                Closed=('STATUS', lambda x: (x == 'Closed').sum()),
                                Open=('STATUS', lambda x: (x != 'Closed').sum())
                            ).reset_index()
                            st.table(summary)
                            st.download_button(" Download Summary Excel", to_excel(summary), "Summary_Report.xlsx")
                        else:
                            
                            detailed_cols = ['Service ID', 'START_TIME', 'END_TIME', 'EMP_ID', 'EMP_Name', 
                                             'PRIORITY', 'Ticket_for', 'Problem', 'DESCRIPTION', 'STATUS']
                            st.dataframe(filtered_df[detailed_cols], use_container_width=True)
                            st.download_button(" Download Detailed Excel", to_excel(filtered_df[detailed_cols]), "Detailed_Report.xlsx")
                    else:
                        st.warning("No data found for the selected range.")

            elif report_choice == "Calls By help desk User":
                col_u, col_s = st.columns(2)
                user_list = run_query("SELECT DISTINCT EMP_Name FROM Apc_EMP")['EMP_Name'].tolist()
                sel_user = col_u.selectbox("Help Desk User", user_list)
                sel_status = col_s.selectbox("Status", ["All", "Active", "In Progress", "Closed"])
                
                if st.button("Filter User Report"):
                    user_df = df_all[df_all['EMP_Name'] == sel_user]
                    if sel_status != "All":
                        user_df = user_df[user_df['STATUS'] == sel_status]
                    
                    st.dataframe(user_df, use_container_width=True)
                    st.download_button(" Download User Report", to_excel(user_df), f"{sel_user}_Report.xlsx")

        else:
            st.info("No tickets found in the database. Charts will appear once tickets are created.")
    elif st.session_state.page == "Call Information" and is_admin:
        st.markdown("""
            <style>
                div[data-testid="stWidgetLabel"] p { font-size: 18px !important; font-weight: 600 !important; }
                div[data-testid="stSelectbox"] div[data-baseweb="select"] > div { font-size: 14px !important; }
                .thin-line { border: 0; height: 1px; background: #e0e0e0; margin: 20px 0; opacity: 0.5; }
                .stExpander details summary p { font-size: 16px !important; color: #ff4b4b !important; }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("<h1 class='main-h1'>Call Information</h1>", unsafe_allow_html=True)
        
        if 'current_problem' not in st.session_state: st.session_state.current_problem = "Problems"
        if 'tree_key' not in st.session_state: st.session_state.tree_key = 0 
        
        emp_data_df = run_query("SELECT EMP_ID, Name, Department FROM Employees")
        final_requester = "Select Name"

        if not emp_data_df.empty:
            search_options = ["Select Requester"] + [f"{row['EMP_ID']} | {row['Name']}" for _, row in emp_data_df.iterrows()]
            selected_option = st.selectbox("Ticket For", search_options, key="mega_search_box")
            
            if selected_option != "Select Requester":
                sel_id = selected_option.split(" | ")[0]
                sel_name = selected_option.split(" | ")[1]
                
               
                dept_name = emp_data_df[emp_data_df['EMP_ID'].astype(str) == sel_id]['Department'].values[0]
                st.success(f" Verified: {sel_name} | ID: {sel_id} | Dept: {dept_name}")
                final_requester = sel_name 

              
                dev_query = "SELECT Category, Model, Device_ID FROM APC_Devices WHERE EMP_ID = ?"
                user_devices = run_query(dev_query, (sel_id,))

                if not user_devices.empty:
                  
                    device_options = [f"{d['Category']} ({d['Model']})" for _, d in user_devices.iterrows()]
                    selected_device = st.selectbox("Identify the problem device", device_options)
                else:
                    st.warning("There are no recorded devices for this employee.")
        
        st.markdown("<div class='thin-line'></div>", unsafe_allow_html=True)

        dept_choice = st.selectbox("Assign to IT Department", ["ERP", "Development", "Technical IT Support"])
        staff_df = run_query("SELECT EMP_Name, EMP_ID, EMP_Email FROM Apc_EMP WHERE EMP_dep = ?", (dept_choice,))
        staff_dict = dict(zip(staff_df['EMP_Name'], staff_df['EMP_ID'])) if not staff_df.empty else {}
        selected_it_staff = st.selectbox("Select IT Employee", list(staff_dict.keys()) if staff_dict else ["No staff"])

        st.markdown("<div class='thin-line'></div>", unsafe_allow_html=True)

        with st.expander(f" Choose The Problem : {st.session_state.current_problem}", expanded=False):
            issue_categories = {
                "Hardware Issues": ["Computer not turning on", "Printer not responding", "Overheating devices"],
                "Network Problems": ["No internet connection", "Wi-Fi not connecting", "Slow performance"],
                "Software Issues": ["Application crashes", "Operating system errors", "Installation fails"]
            }
            for cat, subs in issue_categories.items():
                with st.expander(f"🔴 {cat}"):
                    for s in subs:
                        if st.button(f"▪ {s}", key=f"btn_{s}_{st.session_state.tree_key}", use_container_width=True):
                            st.session_state.current_problem = s
                            st.session_state.tree_key += 1
                            st.rerun()

        if st.session_state.current_problem != "Problems":
            st.success(f" Selected Issue: **{st.session_state.current_problem}**")

        with st.form("call_entry_final"):
            prio = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
            loc = st.selectbox("Location", ["Amman", "Aqaba", "Gawr As-Safi"])
            desc = st.text_area("Description")
            
            if st.form_submit_button("    SAVE TO DATABASE"):
                it_eid = staff_dict.get(selected_it_staff)
                if it_eid and st.session_state.current_problem != "Problems" and final_requester != "Select Name":
                    try:
                        last_id_df = run_query("SELECT [Service ID] FROM APC_Tickets ORDER BY [Service ID] DESC LIMIT 1")
                        new_sid = int(last_id_df.iloc[0]['Service ID']) + 1 if not last_id_df.empty else 1001

                        query = """
                            INSERT INTO APC_Tickets 
                            (TICKET_ID, EMP_ID, PRIORITY, STATUS, LOCATION, DESCRIPTION, CREATED_AT, 
                             START_TIME, END_TIME, Solution, [Service ID], Ticket_for, EMP_Name, Problem) 
                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                            """
                        params = (new_sid, it_eid, prio, "Active", loc, desc, datetime.now().strftime("%Y-%m-%d %H:%M"), 
                                  None, None, None, new_sid, final_requester, selected_it_staff, st.session_state.current_problem)
                        
                        run_query(query, params, is_select=False)
                    except Exception as e:
                           st.error(f"Database Error: {e}")
                           new_sid = None    
                        
                    try:
                            it_email = staff_df[staff_df['EMP_ID'] == it_eid]['EMP_Email'].values[0]
                            email_sent = send_ticket_notification(it_email, new_sid, final_requester, st.session_state.current_problem, prio, selected_it_staff)
                    except:
                            email_sent = False
                        
                    msg = f" Saved! Ticket #{new_sid}"
                    if email_sent: st.success(msg + f" & Email sent to {selected_it_staff}")
                    else: st.warning(msg + " (Check App Password for Email)")
                        
                    st.session_state.current_problem = "Problems"
                    st.session_state.tree_key += 1
                    st.rerun()

        
        with st.expander(" Register New Device"):
            with st.form("add_device_form"):
                d_cat = st.selectbox("Device Category", ["laptop", "desktop", "printer", "scanner", "other"])
                d_model = st.text_input("Model Name (e.g. HP ProBook 450)")
                d_sn = st.text_input("Serial Number")
                d_emp = st.text_input("Assign to Employee ID")
                d_status = st.selectbox("Status", ["Active", "Maintenance", "Stored"])
                
                if st.form_submit_button("Add Device to Inventory"):
                    if d_model and d_sn and d_emp:
                        try:
                           
                            last_id = run_query("SELECT Device_ID FROM APC_Devices ORDER BY Device_ID DESC LIMIT 1")
                            new_id = int(last_id.iloc[0]['Device_ID']) + 1 if not last_id.empty else 1001
                            
                            add_query = "INSERT INTO APC_Devices (Device_ID, Category, Model, Serial_Number, EMP_ID, Status) VALUES (?,?,?,?,?,?)"
                            run_query(add_query, (new_id, d_cat, d_model, d_sn, d_emp, d_status), is_select=False)
                            st.success(f"Device {d_model} added successfully!")
                            st.rerun()
                        except Exception as e: st.error(f"Error: {e}")
                    else: st.warning("Please fill in all details.")
        # ------------------------------------------------------------
      
        # ------------------------------------------------------------

    else:
        worker_id = st.session_state.u_id
        st.markdown(f"<h1 class='main-h1'>Worker Panel: {user['EMP_Name']}</h1>", unsafe_allow_html=True)

        
        st.markdown("""
            <style>
                .ticket-container {
                    background-color: rgba(255, 255, 255, 0.05);
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                }
                .info-row { margin-bottom: 8px; font-size: 16px; color: white; display: flex; align-items: center; }
                .info-label { font-weight: bold; color: #ffffff; margin-right: 8px; min-width: 100px; }
                
                .contact-email { 
                    color: #2ecc71 !important; 
                    font-family: 'Courier New', Courier, monospace !important; 
                    font-weight: bold;
                    font-size: 17px;
                    letter-spacing: 0.5px;
                }
                
                .stButton > button { width: 100%; border-radius: 5px; transition: 0.3s; }
                .stButton > button:hover { background-color: #2ecc71; color: white; }
            </style>
        """, unsafe_allow_html=True)

        worker_nav = st.sidebar.radio(" Menu", ["Current Problems", "Solutions History"])

        if worker_nav == "Current Problems":
            st.markdown(f"<h1 class='main-h1'>Assigned Tickets</h1>", unsafe_allow_html=True)
            
            
            query = "SELECT * FROM APC_Tickets WHERE EMP_ID = ? AND STATUS != 'Closed' ORDER BY CREATED_AT DESC"
            active_df = run_query(query, (worker_id,))
            

            if not active_df.empty:
                for index, row in active_df.iterrows():
                    t_id = row['Service ID']
                    t_started = row['START_TIME'] is not None
                    
                    

                    
                    with st.expander(f" Ticket #{t_id} | {row['LOCATION']} | For: {row['Ticket_for']}", expanded=False):
                        
                        

                        html_content = f"""
                        <div class="info-row"><span class="info-label"> Requester:</span> {row['Ticket_for']}</div>                                                                                                
                        <div class="info-row"><span class="info-label"> Contact:</span> <span class="contact-email">support@apc.com.jo</span></div>
                        <div style="margin:10px 0; border-bottom:1px solid rgba(255,255,255,0.2);"></div>
                        <div class="info-row"><span class="info-label"> Problem:</span> {row['Problem']}</div>
                        <div class="info-row"><span class="info-label"> Description:</span> {row['DESCRIPTION']}</div>
                        """
                        
                        st.markdown(html_content, unsafe_allow_html=True)
                        st.markdown("---")
                        
                        
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            if st.button(" Start Progress", key=f"start_{t_id}", disabled=t_started):
                                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                                run_query("UPDATE APC_Tickets SET STATUS = 'In Progress', START_TIME = ? WHERE [Service ID] = ?", (now, t_id), is_select=False)
                                st.rerun()
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        
                        sol_input = st.text_area("Solution Detail:", key=f"sol_in_{t_id}", placeholder="Describe how you fixed it...")

                        if st.button(" Finish & Close", key=f"close_{t_id}", disabled=not t_started):
                            if sol_input.strip():
                                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                                run_query("UPDATE APC_Tickets SET STATUS = 'Closed', Solution = ?, END_TIME = ? WHERE [Service ID] = ?", (sol_input, now, t_id), is_select=False)
                                st.success(f" Ticket #{t_id} closed successfully!")
                                st.rerun()
                            else:
                                st.warning(" Please describe the solution before closing.")
            else:
                st.info(" No active tickets assigned to you right now.")

        elif worker_nav == "Solutions History":
            st.markdown(f"<h1 class='main-h1'>My Solutions Archive</h1>", unsafe_allow_html=True)
            
            history_query = """
                SELECT [Service ID] as 'ID', Ticket_for as 'Requester', Problem, Solution, START_TIME as 'Started', END_TIME as 'Finished'
                FROM APC_Tickets 
                WHERE EMP_ID = ? AND STATUS = 'Closed' 
                ORDER BY END_TIME DESC
            """
            history_df = run_query(history_query, (worker_id,))
            
            if not history_df.empty:
                st.dataframe(history_df, use_container_width=True)
                st.write(f" Total Tickets Solved: **{len(history_df)}**")
            else:
                st.warning(" Your history is empty.")