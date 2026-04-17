import streamlit as st
from streamlit_option_menu import option_menu
from pages import home, Visual, About  # import your app modules here

st.set_page_config(page_title="Road Accident Analysis", layout="wide")


apps = [
    {"func": home.app, "title": "Home", "icon": "house"},
    {"func": Visual.app, "title": "Visual", "icon": "camera"},
    {"func": About.app, "title": "About", "icon": "info"},
    
]

titles = [app["title"] for app in apps]
titles_lower = [title.lower() for title in titles]
icons = [app["icon"] for app in apps]

try:
    # Streamlit >= 1.30
    page_param = st.query_params.get("page")
except Exception:
    # Fallback for older Streamlit releases
    params = st.experimental_get_query_params()
    page_param = params.get("page", [None])[0] if "page" in params else None

if isinstance(page_param, list):
    page_param = page_param[0] if page_param else None

if page_param and str(page_param).lower() in titles_lower:
    default_index = titles_lower.index(str(page_param).lower())
else:
    default_index = 0

with st.sidebar:
    selected = option_menu(
        "Main Menu",
        options=titles,
        icons=icons,
        menu_icon="cast",
        default_index=default_index,
    )

    # st.sidebar.title("Contact")
    # st.sidebar.info(
    #     """
    #     git
    #     contact
    #     facebook
    # """
    # )

for app in apps:
    if app["title"] == selected:
        app["func"]()
        break