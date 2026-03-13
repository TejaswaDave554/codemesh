"""Metrics panel UI component."""

import streamlit as st
from core.analyzer import CodeAnalyzer
from core.metrics import MetricsCalculator


def render_metrics_panel(analyzer: CodeAnalyzer) -> None:
    """Render top metrics summary panel."""
    if not analyzer or not analyzer.graph or analyzer.graph.number_of_nodes() == 0:
        return
    
    metrics_calc = MetricsCalculator(analyzer.graph)
    summary = metrics_calc.get_summary_metrics()
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("📊 Functions", summary['total_functions'])
    with col2:
        st.metric("🏛️ Classes", summary['total_classes'])
    with col3:
        st.metric("⚙️ Methods", summary['total_methods'])
    with col4:
        st.metric("🔗 Total Nodes", summary['total_nodes'])
    with col5:
        max_depth = metrics_calc.get_max_call_depth()
        st.metric("📏 Max Depth", max_depth)
    with col6:
        complexity_stats = metrics_calc.get_complexity_stats()
        st.metric("🧮 Avg Complexity", f"{complexity_stats['avg']:.1f}")
