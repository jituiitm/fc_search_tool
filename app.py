import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import math
import taxonomy 
from supabase import create_client, Client
from google import genai

# --- 1. SECURITY & AUTHENTICATION ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Recruiter OS Login")
    pwd = st.text_input("Enter Password", type="password")
    if pwd == st.secrets["APP_PASSWORD"]:
        st.session_state.authenticated = True
        st.rerun()
    elif pwd:
        st.error("Access Denied")
    st.stop()

# --- 2. CONFIGURATION ---
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

AI_MODEL = "gemini-2.0-flash" 
PAGE_SIZE = 50 

@st.cache_resource
def init_clients():
    return create_client(SUPABASE_URL, SUPABASE_KEY), genai.Client(api_key=GEMINI_API_KEY)

supabase, gemini_client = init_clients()

# --- DATABASE ACTIONS ---
def delete_candidate(c_id):
    try:
        supabase.table("candidates").delete().eq("id", c_id).execute()
        st.toast(f"Candidate {c_id} deleted successfully!", icon="🗑️")
        st.rerun()
    except Exception as e:
        st.error(f"Error deleting: {e}")

def get_candidates(filters=None, list_id=None, page=1):
    query = supabase.table("candidates").select("*", count="exact")
    
    if list_id:
        relations = supabase.table("list_candidates").select("candidate_id").eq("list_id", list_id).execute().data
        if not relations: return [], 0
        ids = [r['candidate_id'] for r in relations]
        query = query.in_("id", ids)
    elif filters:
        if filters.get('name_search'): query = query.ilike("full_name", f"%{filters['name_search']}%")
        if filters.get('campaign_search'): query = query.ilike("campaign_name", f"%{filters['campaign_search']}%")
        if filters['types']: query = query.overlaps("founder_types", filters['types'])
        if filters['funcs']: query = query.overlaps("functions_overseen", filters['funcs'])
        if filters['inds']: query = query.overlaps("industry_experience", filters['inds'])
        if filters['skills']: query = query.overlaps("skills", filters['skills'])
        if filters['roles']: query = query.overlaps("suitable_roles", filters['roles'])
        if filters['stages']: query = query.overlaps("startup_stage_experience", filters['stages'])
        query = query.gte("total_experience", filters['min_exp'])
        query = query.gte("founder_experience_years", filters['min_founder_exp'])
        if filters['location']: query = query.ilike("current_location", f"%{filters['location']}%")
    
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE - 1
    query = query.range(start, end).order("id", desc=True)
    
    response = query.execute()
    return response.data, response.count

def ask_ai_about_list(candidates, question):
    if not candidates: return "List is empty."
    context_text = "".join([f"- {c['full_name']} (ID:{c['id']}): {c['resume_summary']} [Tags: {c['founder_types']}, {c['skills']}]\n" for c in candidates])
    
    prompt = f"""You are a Recruiting Analyst. You are looking at a filtered list of {len(candidates)} candidates.
    CANDIDATE DATA: {context_text}
    USER QUESTION: "{question}"
    INSTRUCTIONS: Identify specific candidates match the question. Cite experience. Be concise."""
    
    response = gemini_client.models.generate_content(model=AI_MODEL, contents=prompt)
    return response.text

# --- HELPER FUNCTIONS ---
def get_lists(): return supabase.table("lists").select("*").order("name").execute().data
def create_list(name): supabase.table("lists").insert({"name": name}).execute(); st.rerun()
def add_to_list(lid, cid): supabase.table("list_candidates").insert({"list_id": lid, "candidate_id": cid}).execute(); st.toast("Added!", icon="✅")
def remove_from_list(lid, cid): supabase.table("list_candidates").delete().eq("list_id", lid).eq("candidate_id", cid).execute(); st.rerun()
def update_candidate(cid, updates): supabase.table("candidates").update(updates).eq("id", cid).execute(); st.toast("Updated!", icon="💾"); st.rerun()

# --- UI STATE ---
if 'page' not in st.session_state: st.session_state.page = 1
if 'messages' not in st.session_state: st.session_state.messages = []
def reset_page(): st.session_state.page = 1

# --- UI LAYOUT ---
st.set_page_config(page_title="Recruiter OS", layout="wide", page_icon="🕵️‍♂️")

# --- SCROLL TO TOP INJECTION ---
components.html(
    """
    <script>
    const parent = window.parent.document;
    if (!parent.getElementById("st-scroll-btn")) {
        const btn = parent.createElement("button");
        btn.id = "st-scroll-btn";
        btn.innerHTML = "⬆️ Top";
        btn.style.cssText = "display:none; position:fixed; bottom:40px; right:40px; z-index:99999; background:#2e2e38; color:white; border:1px solid #4a4a5a; border-radius:8px; padding:10px 15px; font-weight:bold; cursor:pointer; box-shadow:0 4px 6px rgba(0,0,0,0.3); transition: background 0.2s;";
        
        btn.onclick = () => {
            const scrollContainer = parent.querySelector('.stAppViewMain') || parent.documentElement;
            scrollContainer.scrollTo({top: 0, behavior: 'smooth'});
        };
        
        parent.body.appendChild(btn);
        
        parent.addEventListener('scroll', (e) => {
            if (e.target.scrollHeight > e.target.clientHeight) {
                const scrollPct = e.target.scrollTop / (e.target.scrollHeight - e.target.clientHeight);
                if (scrollPct >= 0.5) {
                    btn.style.display = "block";
                } else {
                    btn.style.display = "none";
                }
            }
        }, true);
    }
    </script>
    """, height=0, width=0
)

# --- SIDEBAR ---
st.sidebar.title("🕵️‍♂️ Recruiter OS")
view_mode = st.sidebar.radio("Navigation", ["🔍 Search Candidates", "📂 Saved Lists"], on_change=reset_page)

filters = {}
selected_list_id = None

if view_mode == "🔍 Search Candidates":
    st.sidebar.divider()
    name_search = st.sidebar.text_input("👤 Name Search", placeholder="Type name...", on_change=reset_page)
    campaign_search = st.sidebar.text_input("🏷️ Campaign Search", placeholder="Ex: Gynoveda...", on_change=reset_page)
    
    st.sidebar.header("Filters")
    sel_types = st.sidebar.multiselect("Founder Type", taxonomy.FOUNDER_TYPES, on_change=reset_page)
    sel_roles = st.sidebar.multiselect("Suitable Roles", taxonomy.SUITABLE_ROLES, on_change=reset_page)
    sel_funcs = st.sidebar.multiselect("Functions", taxonomy.FUNCTIONS, on_change=reset_page)
    sel_inds = st.sidebar.multiselect("Industry", taxonomy.INDUSTRIES, on_change=reset_page)
    sel_skills = st.sidebar.multiselect("Skills", taxonomy.SKILLS, on_change=reset_page)
    
    min_exp = st.sidebar.slider("Total Exp (Yrs)", 0, 25, 0, on_change=reset_page)
    min_found = st.sidebar.slider("Founder Exp (Yrs)", 0, 10, 0, on_change=reset_page)
    loc_search = st.sidebar.text_input("Location", on_change=reset_page)

    filters = {
        "name_search": name_search, "campaign_search": campaign_search,
        "types": sel_types, "roles": sel_roles, "funcs": sel_funcs,
        "inds": sel_inds, "skills": sel_skills, "stages": [],
        "min_exp": min_exp, "min_founder_exp": min_found, "location": loc_search
    }
    st.subheader("🔍 Search Results")

else:
    st.sidebar.divider()
    st.sidebar.header("My Lists")
    new_list = st.sidebar.text_input("New List Name")
    if st.sidebar.button("Create List"): create_list(new_list)
    
    my_lists = get_lists()
    if not my_lists: st.info("No lists yet."); st.stop()
        
    list_map = {l['name']: l['id'] for l in my_lists}
    sel_list_name = st.sidebar.selectbox("Select List", list(list_map.keys()), on_change=reset_page)
    selected_list_id = list_map[sel_list_name]
    st.subheader(f"📂 List: {sel_list_name}")

# --- DATA FETCHING ---
candidates, total_count = get_candidates(filters=filters, list_id=selected_list_id, page=st.session_state.page)

# --- RESULTS DISPLAY ---
if candidates:
    total_pages = math.ceil(total_count / PAGE_SIZE)
    st.caption(f"Showing {len(candidates)} of {total_count} candidates | Page {st.session_state.page} of {total_pages}")
    
    all_lists = get_lists()
    list_lookup = {l['name']: l['id'] for l in all_lists}

    for c in candidates:
        camp_name = c.get('campaign_name') or "General"
        
        # Expanders default to open
        with st.expander(f"🆔 {c['id']} | {c['full_name']} | 🏷️ {camp_name}", expanded=True):
            
            # Row 1: Contact
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                st.markdown(f"**Email:** `{c['email']}`")
                st.markdown(f"**Phone:** `{c['phone']}`")
                ctc_display = f"{c['current_ctc_lakhs']} LPA" if c.get('current_ctc_lakhs') else "N/A"
                st.caption(f"📍 {c['current_location']} | 💰 {ctc_display} | 📅 {c['applied_date']}")
            with c2:
                if c['linkedin_url']: st.markdown(f"🔗 [LinkedIn Profile]({c['linkedin_url']})")
                if c['resume_url']: st.markdown(f"📄 [Resume PDF]({c['resume_url']})")
                st.caption(f"**Source:** {c.get('source', 'Unknown')} | **Campaign:** {camp_name}")
            with c3:
                if view_mode == "🔍 Search Candidates":
                    target = st.selectbox("Add to:", ["Select..."] + list(list_lookup.keys()), key=f"add_sel_{c['id']}")
                    if target != "Select..." and st.button("Add", key=f"btn_add_{c['id']}"):
                        add_to_list(list_lookup[target], c['id'])
                else:
                    if st.button("❌ Remove", key=f"btn_rem_{c['id']}"):
                        remove_from_list(selected_list_id, c['id'])

            st.divider()
            
            # Row 2: Data (Null-safe)
            m1, m2 = st.columns([1, 1])
            with m1:
                st.write(f"**Roles:** {c.get('suitable_roles') or []}")
                st.write(f"**Industry:** {c.get('industry_experience') or []}")
            with m2:
                st.write(f"**Skills:** {c.get('skills') or []}")
            
            st.info(f"**📄 Summary:** {c.get('resume_summary', 'No summary available.')}")

            st.divider()
            
            # Row 3: Admin
            b1, b2 = st.columns([1, 5])
            with b1:
                with st.popover("🗑️ Delete"):
                    st.write("Are you sure?")
                    if st.button("Confirm", key=f"del_{c['id']}", type="primary"): delete_candidate(c['id'])
            with b2:
                with st.popover("✏️ Edit Data"):
                    with st.form(key=f"edit_{c['id']}"):
                        st.write(f"Editing: {c['full_name']}")
                        n_roles = st.multiselect("Roles", taxonomy.SUITABLE_ROLES, default=[x for x in (c.get('suitable_roles') or []) if x in taxonomy.SUITABLE_ROLES])
                        n_inds = st.multiselect("Industries", taxonomy.INDUSTRIES, default=[x for x in (c.get('industry_experience') or []) if x in taxonomy.INDUSTRIES])
                        n_types = st.multiselect("Types", taxonomy.FOUNDER_TYPES, default=[x for x in (c.get('founder_types') or []) if x in taxonomy.FOUNDER_TYPES])
                        if st.form_submit_button("Save"):
                            update_candidate(c['id'], {"suitable_roles": n_roles, "industry_experience": n_inds, "founder_types": n_types})

    # --- PAGINATION ---
    st.divider()
    col_prev, col_info, col_next = st.columns([1, 2, 1])
    with col_prev:
        if st.session_state.page > 1 and st.button("⬅️ Previous"): st.session_state.page -= 1; st.rerun()
    with col_info:
        st.markdown(f"<div style='text-align: center'>Page <b>{st.session_state.page}</b> of <b>{total_pages}</b></div>", unsafe_allow_html=True)
    with col_next:
        if st.session_state.page < total_pages and st.button("Next ➡️"): st.session_state.page += 1; st.rerun()
    
    # --- CHAT ---
    st.divider()
    st.subheader("🤖 Chat with this Page")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.write(msg["content"])

    if user_query := st.chat_input("Ask about these candidates..."):
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"): st.write(user_query)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                ai_response = ask_ai_about_list(candidates, user_query)
                st.write(ai_response)
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

else:
    st.info("No candidates found.")
    if st.session_state.page > 1 and st.button("Back to Start"): st.session_state.page = 1; st.rerun()