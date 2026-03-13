"""Export panel UI component."""

import streamlit as st
import json
import pandas as pd
from datetime import datetime
from core.analyzer import CodeAnalyzer
from core.metrics import MetricsCalculator


def render_export_panel(analyzer: CodeAnalyzer) -> None:
    """Render export functionality."""
    if not analyzer or not analyzer.graph or analyzer.graph.number_of_nodes() == 0:
        return
    
    st.subheader("📥 Export Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        _render_json_export(analyzer)
    
    with col2:
        _render_csv_export(analyzer)


def _render_json_export(analyzer: CodeAnalyzer) -> None:
    """Render JSON export button."""
    if st.button("📄 Export as JSON"):
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'nodes': dict(analyzer.graph.nodes(data=True)),
            'edges': list(analyzer.graph.edges(data=True)),
            'metrics': MetricsCalculator(analyzer.graph).get_summary_metrics()
        }
        
        st.download_button(
            "💾 Download JSON",
            json.dumps(export_data, indent=2),
            "codemesh_analysis.json",
            "application/json"
        )


def _render_csv_export(analyzer: CodeAnalyzer) -> None:
    """Render CSV export button."""
    if st.button("📊 Export Metrics CSV"):
        metrics_data = []
        for node_id, data in analyzer.graph.nodes(data=True):
            metrics_data.append({
                'name': data['name'],
                'type': data['type'],
                'file': data['file'],
                'complexity': data.get('complexity', 1),
                'callers': len(analyzer.get_callers(node_id)),
                'callees': len(analyzer.get_callees(node_id))
            })
        
        df = pd.DataFrame(metrics_data)
        csv = df.to_csv(index=False)
        
        st.download_button(
            "💾 Download CSV",
            csv,
            "codemesh_metrics.csv",
            "text/csv"
        )
