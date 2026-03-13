"""Main Streamlit application for Python code analysis and visualization."""

import streamlit as st
import logging
from typing import Any, Dict

from config.config import APP_CONFIG, ANALYSIS_CONFIG, LOGGING_CONFIG, ERROR_MESSAGES, SUCCESS_MESSAGES
from config.exceptions import FileSizeError, UnsupportedFileError, FileProcessingError
from utils.file_handler import FileHandler
from core.parser import PythonParser
from core.analyzer import CodeAnalyzer
from ui import (
    render_sidebar,
    render_metrics_panel,
    render_node_details,
    render_search_panel,
    render_visualizations,
    render_export_panel
)

logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format']
)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title=APP_CONFIG['page_title'],
    page_icon=APP_CONFIG['page_icon'],
    layout=APP_CONFIG['layout']
)


def initialize_session_state() -> None:
    """Initialize Streamlit session state variables."""
    defaults: Dict[str, Any] = {
        'files': None,
        'analyzer': None,
        'parse_result': None,
        'selected_node': None,
        'sort_by': ANALYSIS_CONFIG['default_sort_by']
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_session_state() -> None:
    """Clear session state when uploading new files."""
    keys_to_clear = ['files', 'analyzer', 'parse_result', 'selected_node']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def process_uploaded_files(uploaded_files: list) -> None:
    """Process uploaded files and build analysis graph."""
    clear_session_state()
    
    try:
        with st.spinner("Extracting files..."):
            files = FileHandler.extract_files(uploaded_files)
        
        with st.spinner("Parsing code..."):
            parser = PythonParser()
            parse_result = parser.parse_files(files)
        
        with st.spinner("Building analysis graph..."):
            analyzer = CodeAnalyzer(parse_result)
        
        st.session_state.update({
            'files': files,
            'parse_result': parse_result,
            'analyzer': analyzer
        })
        
        st.success(SUCCESS_MESSAGES['analysis_complete'].format(
            len(files), analyzer.graph.number_of_nodes()
        ))
        
        if parse_result.errors:
            st.warning(SUCCESS_MESSAGES['parsing_warning'].format(len(parse_result.errors)))
            with st.expander("View parsing errors"):
                for filepath, error in parse_result.errors.items():
                    st.error(f"**{filepath}**: {error}")
    
    except (FileSizeError, UnsupportedFileError, FileProcessingError) as e:
        st.error(f"❌ {str(e)}")
        logger.error(f"File processing error: {e}")
    except Exception as e:
        st.error(ERROR_MESSAGES['processing_error'].format(str(e)))
        logger.error(f"Unexpected error: {e}", exc_info=True)


def render_welcome_screen() -> None:
    """Render welcome screen when no files are loaded."""
    st.info("👆 Upload Python files using the sidebar to get started")
    
    with st.expander("📖 How to use CodeMesh"):
        st.markdown("""
        1. **Upload Files**: Use the sidebar to upload .py files or .zip archives
        2. **Analyze**: Click "Analyze Code" to process your files
        3. **Explore**: Use the interactive visualizations to understand your code structure
        4. **Filter**: Use sidebar filters to focus on specific files or complexity levels
        5. **Export**: Download analysis results as JSON or CSV
        """)


def main() -> None:
    """Main application entry point."""
    initialize_session_state()
    
    selected_file, max_depth, display_limit = render_sidebar(
        process_uploaded_files,
        clear_session_state
    )
    
    st.title("🔍 CodeMesh - Python Code Analyzer")
    st.markdown("Analyze Python code structure, dependencies, and complexity with interactive visualizations.")
    
    analyzer = st.session_state.get('analyzer')
    
    if not analyzer or not analyzer.graph or analyzer.graph.number_of_nodes() == 0:
        render_welcome_screen()
        return
    
    render_metrics_panel(analyzer)
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_node = render_search_panel(analyzer)
        if selected_node:
            st.session_state.selected_node = selected_node
    
    with col2:
        render_export_panel(analyzer)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_visualizations(analyzer, selected_file, max_depth)
    
    with col2:
        if st.session_state.get('selected_node'):
            st.markdown("### 📍 Node Details")
            render_node_details(analyzer, st.session_state.selected_node, display_limit)
        else:
            st.info("Click on a node in the visualization or use search to view details")


if __name__ == "__main__":
    main()
