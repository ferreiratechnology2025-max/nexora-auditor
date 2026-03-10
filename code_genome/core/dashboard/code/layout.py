import streamlit as st

class NexoraDashboard:
    def __init__(self, title="Nexora SaaS"):
        st.set_page_config(page_title=title, layout="wide")
        self.title = title

    def render_sidebar(self, menu_options):
        st.sidebar.title(self.title)
        return st.sidebar.radio("Navegação", menu_options)

    def render_metrics(self, metrics_dict):
        cols = st.columns(len(metrics_dict))
        for i, (label, value) in enumerate(metrics_dict.items()):
            cols[i].metric(label, value)

    def render_footer(self):
        st.divider()
        st.caption("Gerado por Nexora Agente - [Drive D: Local]")
