"""Node details UI component."""

import streamlit as st
from core.analyzer import CodeAnalyzer
from utils.validation import validate_node_id, sanitize_display_limit
from config.exceptions import ValidationError


def render_node_details(analyzer: CodeAnalyzer, node_id: str, display_limit: int = 20) -> None:
    """Render detailed information about a selected node."""
    try:
        validate_node_id(node_id)
    except ValidationError as e:
        st.warning(str(e))
        return
    
    if node_id not in analyzer.graph:
        st.warning("Node not found")
        return
    
    display_limit = sanitize_display_limit(display_limit)
    node_data = analyzer.graph.nodes[node_id]
    
    st.subheader(f"📍 {node_data['name']}")
    
    _render_node_info(node_data)
    _render_relationships(analyzer, node_id, display_limit)


def _render_node_info(node_data: dict) -> None:
    """Render node information section."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Type:** {node_data['type']}")
        st.write(f"**File:** {node_data['file']}")
        st.write(f"**Line:** {node_data['line']}")
        
        if node_data.get('params'):
            st.write(f"**Parameters:** `{', '.join(node_data['params'])}`")
        
        if node_data.get('decorators'):
            st.write(f"**Decorators:** `@{', @'.join(node_data['decorators'])}`")
    
    with col2:
        if node_data.get('parent_class'):
            st.write(f"**Parent Class:** {node_data['parent_class']}")
        
        if node_data.get('base_classes'):
            st.write(f"**Base Classes:** {', '.join(node_data['base_classes'])}")
        
        st.write(f"**Complexity:** {node_data.get('complexity', 1)}")
        
        if node_data.get('external_refs'):
            st.write(f"**External Files:** {', '.join(node_data['external_refs'])}")


def _render_relationships(analyzer: CodeAnalyzer, node_id: str, display_limit: int) -> None:
    """Render node relationships section."""
    callers = analyzer.get_callers(node_id)
    callees = analyzer.get_callees(node_id)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if callers:
            st.write(f"**Called by ({len(callers)}):**")
            for caller in callers[:display_limit]:
                caller_name = analyzer.graph.nodes[caller]['name']
                caller_file = analyzer.graph.nodes[caller]['file'].split('/')[-1].split('\\\\')[-1]
                st.text(f"  • {caller_name} ({caller_file})")
            if len(callers) > display_limit:
                st.text(f"  ... and {len(callers) - display_limit} more")
    
    with col2:
        if callees:
            st.write(f"**Calls ({len(callees)}):**")
            for callee in callees[:display_limit]:
                callee_name = analyzer.graph.nodes[callee]['name']
                callee_file = analyzer.graph.nodes[callee]['file'].split('/')[-1].split('\\\\')[-1]
                st.text(f"  • {callee_name} ({callee_file})")
            if len(callees) > display_limit:
                st.text(f"  ... and {len(callees) - display_limit} more")
