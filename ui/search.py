"""Search panel UI component."""

import streamlit as st
from typing import Optional
from core.analyzer import CodeAnalyzer
from config.config import UI_CONFIG, ERROR_MESSAGES


def render_search_panel(analyzer: CodeAnalyzer) -> Optional[str]:
    """Render search functionality."""
    if not analyzer or not analyzer.graph or analyzer.graph.number_of_nodes() == 0:
        return None
    
    search_term = st.text_input("🔍 Search functions/classes", placeholder="Enter function or class name")
    
    if search_term:
        matches = _find_matches(analyzer, search_term)
        
        if matches:
            st.write(f"Found {len(matches)} matches:")
            return _render_matches(matches)
        else:
            st.info(ERROR_MESSAGES['no_matches'])
    
    return None


def _find_matches(analyzer: CodeAnalyzer, search_term: str) -> list:
    """Find nodes matching search term."""
    matches = []
    search_lower = search_term.lower()
    
    for node_id, data in analyzer.graph.nodes(data=True):
        if search_lower in data['name'].lower():
            matches.append((node_id, data))
    
    return matches


def _render_matches(matches: list) -> Optional[str]:
    """Render search matches and return selected node."""
    for node_id, data in matches[:UI_CONFIG['search_results_limit']]:
        file_short = data['file'].split('/')[-1].split('\\\\')[-1]
        if st.button(f"{data['name']} ({data['type']}) - {file_short}", key=f"search_{node_id}"):
            return node_id
    
    return None
