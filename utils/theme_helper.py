"""Theme detection and adaptive styling utilities."""

import streamlit as st
from typing import Dict, Any


def get_theme_colors() -> Dict[str, str]:
    """Get theme-adaptive colors for visualizations.
    
    Returns:
        Dictionary with color values that adapt to current theme
    """
    # Try to detect theme from Streamlit's session state or config
    try:
        # Check if we can access theme info
        theme = st.get_option("theme.base")
        is_dark = theme == "dark"
    except:
        # Fallback: assume light theme if detection fails
        is_dark = False
    
    if is_dark:
        return {
            'background': 'rgba(0,0,0,0)',
            'paper_bg': 'rgba(0,0,0,0)', 
            'text_primary': '#FAFAFA',
            'text_secondary': '#CCCCCC',
            'edge_color': 'rgba(200,200,200,0.6)',
            'grid_color': 'rgba(255,255,255,0.1)',
            'node_border': '#FFFFFF',
            'hover_bg': 'rgba(255,255,255,0.1)'
        }
    else:
        return {
            'background': 'rgba(0,0,0,0)',
            'paper_bg': 'rgba(0,0,0,0)',
            'text_primary': '#262730',
            'text_secondary': '#6C6C6C', 
            'edge_color': 'rgba(100,100,100,0.6)',
            'grid_color': 'rgba(0,0,0,0.1)',
            'node_border': '#FFFFFF',
            'hover_bg': 'rgba(0,0,0,0.05)'
        }


def get_node_colors() -> Dict[str, str]:
    """Get theme-adaptive node colors.
    
    Returns:
        Dictionary with node colors that work in both themes
    """
    return {
        'class': '#4A90E2',      # Blue
        'function': '#7ED321',   # Green  
        'method': '#9013FE',     # Purple
        'variable': '#F5A623',   # Orange
        'external': '#D0021B',   # Red
        'root': '#2E8B57',       # Sea Green
        'middle': '#4682B4',     # Steel Blue
        'leaf': '#9370DB',       # Medium Purple
        'isolated': '#DAA520'    # Goldenrod
    }


def get_theme_layout() -> Dict[str, Any]:
    """Get theme-adaptive layout settings.
    
    Returns:
        Dictionary with layout settings for Plotly figures
    """
    colors = get_theme_colors()
    
    return {
        'plot_bgcolor': colors['background'],
        'paper_bgcolor': colors['paper_bg'],
        'font': {
            'color': colors['text_primary'],
            'family': 'Arial, sans-serif'
        },
        'xaxis': {
            'showgrid': False,
            'zeroline': False, 
            'showticklabels': False,
            'showline': False,
            'color': colors['text_secondary']
        },
        'yaxis': {
            'showgrid': False,
            'zeroline': False,
            'showticklabels': False, 
            'showline': False,
            'color': colors['text_secondary']
        },
        'margin': {'l': 20, 'r': 20, 't': 60, 'b': 20}
    }