import streamlit as st
import os
from pdf_processor import PDFProcessor
from summarizer import PDFSummarizer
from utils import (
    validate_api_key,
    estimate_processing_time,
    display_processing_status,
    format_summary_display,
    export_summary_to_text,
    create_summary_dataframe,
)

import time
from langdetect import detect

TEXTS = {
    "en": {
        "title": "PDF Reader + AI Summarizer",
        "subtitle": "Upload a PDF document and get intelligent summaries powered by OpenAI.",
        "settings": "Settings",
        "summary_type": "Summary Type",
        "max_tokens": "Max Tokens per Chunk",
        "analysis": "Show Document Analysis",
        "quotes": "Extract Key Quotes",
        "upload_label": "Choose a PDF file",
        "file_uploaded": "File uploaded",
        "process_pdf": "Process PDF",
        "analyzing_metadata": "Analyzing PDF metadata...",
        "extracting_text": "Extracting text from PDF...",
        "cleaning_text": "Cleaning and processing text...",
        "chunking_text": "Splitting text into chunks...",
        "analyzing_document": "Analyzing document structure...",
        "generating_summaries": "Generating summaries...",
        "extracting_quotes": "Extracting key quotes...",
        "document_analysis": "Document Analysis",
        "key_quotes": "Key Quotes",
        "summary_results": "Summary Results",
        "export_options": "Export Options",
        "download_text": "Download as Text",
        "download_csv": "Download Statistics as CSV",
        "processing_stats": "Processing Statistics",
        "pages": "Pages",
        "title_label": "Title",
        "author": "Author",
        "subject": "Subject",
        "estimated_time": "Estimated processing time",
        "success_summaries": "Summaries generated successfully!",
        "analysis_failed": "Could not analyze document structure",
    },
    "fr": {
        "title": "Lecteur PDF + Resume IA",
        "subtitle": "Telechargez un document PDF et obtenez des resumes intelligents via OpenAI.",
        "settings": "Parametres",
        "summary_type": "Type de resume",
        "max_tokens": "Nombre max de tokens par bloc",
        "analysis": "Afficher l'analyse du document",
        "quotes": "Extraire les citations cles",
        "upload_label": "Choisissez un fichier PDF",
        "file_uploaded": "Fichier telecharge",
        "process_pdf": "Traiter le PDF",
        "analyzing_metadata": "Analyse des metadonnees du PDF...",
        "extracting_text": "Extraction du texte du PDF...",
        "cleaning_text": "Nettoyage et traitement du texte...",
        "chunking_text": "Decoupage du texte en blocs...",
        "analyzing_document": "Analyse de la structure du document...",
        "generating_summaries": "Generation des resumes...",
        "extracting_quotes": "Extraction des citations cles...",
        "document_analysis": "Analyse du document",
        "key_quotes": "Citations cles",
        "summary_results": "Resultats du resume",
        "export_options": "Options d'export",
        "download_text": "Telecharger en texte",
        "download_csv": "Telecharger les statistiques en CSV",
        "processing_stats": "Statistiques de traitement",
        "pages": "Pages",
        "title_label": "Titre",
        "author": "Auteur",
        "subject": "Sujet",
        "estimated_time": "Temps de traitement estime",
        "success_summaries": "Resumes generes avec succes !",
        "analysis_failed": "Impossible d'analyser la structure du document",
    },
}

def detect_document_language(text: str) -> str:
    try:
        lang = detect(text[:3000])
        if lang.startswith("fr"):
            return "fr"
        return "en"
    except Exception:
        return "en"

st.set_page_config(
    page_title="PDF AI Summarizer",
    page_icon="📄",
    layout="wide",
)

def main():
    if "language" not in st.session_state:
        st.session_state.language = "en"

    if "pdf_processor" not in st.session_state:
        st.session_state.pdf_processor = PDFProcessor()

    if "summarizer" not in st.session_state:
        st.session_state.summarizer = PDFSummarizer()

    ui = TEXTS[st.session_state.language]

    st.title(f"📄 {ui['title']}")
    st.markdown(ui["subtitle"])

    if not validate_api_key():
        st.stop()

    st.sidebar.header(f"⚙ {ui['settings']}")

    summary_type = st.sidebar.selectbox(
        ui["summary_type"],
        ["brief", "detailed", "bullet_points", "executive"],
        index=1,
    )

    max_tokens = st.sidebar.slider(
        ui["max_tokens"],
        4000,
        10000,
        8000,
    )

    show_analysis = st.sidebar.checkbox(
        ui["analysis"],
        value=True,
    )

    show_quotes = st.sidebar.checkbox(
        ui["quotes"],
        value=False,
    )

    uploaded_file = st.file_uploader(
        ui["upload_label"],
        type="pdf",
    )

    if uploaded_file is not None:
        st.success(f"✅ {ui['file_uploaded']}: {uploaded_file.name}")

        with st.spinner(ui["analyzing_metadata"]):
            metadata = st.session_state.pdf_processor.get_pdf_metadata(uploaded_file)

        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📄 {ui['pages']}: {metadata.get('num_pages', 'Unknown')}")
            st.info(f"📝 {ui['title_label']}: {metadata.get('title', 'Unknown')}")
        with col2:
            st.info(f"👤 {ui['author']}: {metadata.get('author', 'Unknown')}")
            st.info(f"📋 {ui['subject']}: {metadata.get('subject', 'Unknown')}")

        if st.button(f"🚀 {ui['process_pdf']}", type="primary"):
            process_pdf(uploaded_file, summary_type, max_tokens, show_analysis, show_quotes)


def process_pdf(uploaded_file, summary_type, max_tokens, show_analysis, show_quotes):
    ui = TEXTS[st.session_state.language]

    with st.spinner(ui["extracting_text"]):
        try:
            raw_text = st.session_state.pdf_processor.extract_text_from_pdf(uploaded_file)
            st.success(f"✅ Extracted {len(raw_text)} characters")
        except Exception as e:
            st.error(f"❌ Error extracting text: {str(e)}")
            return

    with st.spinner(ui["cleaning_text"]):
        clean_text = st.session_state.pdf_processor.clean_text(raw_text)
        st.session_state.language = detect_document_language(clean_text)
        ui = TEXTS[st.session_state.language]
        token_count = st.session_state.pdf_processor.count_tokens(clean_text)
        st.success(f"✅ Cleaned text: {len(clean_text)} characters, ~{token_count} tokens")

    with st.spinner(ui["chunking_text"]):
        chunks = st.session_state.pdf_processor.chunk_text(clean_text, max_tokens)
        st.success(f"✅ Created {len(chunks)} chunks")
        estimated_time = estimate_processing_time(len(chunks))
        st.info(f"⏱ {ui['estimated_time']}: {estimated_time}")

    if show_analysis:
        with st.spinner(ui["analyzing_document"]):
            analysis = st.session_state.summarizer.analyze_document_structure(
                clean_text,
                st.session_state.language,
            )
            if analysis["status"] == "success":
                st.subheader(f"📊 {ui['document_analysis']}")
                st.write(analysis["analysis"])
            else:
                st.warning(f"⚠ {ui['analysis_failed']}")

    with st.spinner(ui["generating_summaries"]):
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            summary_data = st.session_state.summarizer.summarize_chunks(
                chunks,
                summary_type,
                st.session_state.language,
            )
            progress_bar.progress(1.0)
            status_text.success(f"✅ {ui['success_summaries']}")
        except Exception as e:
            st.error(f"❌ Error generating summaries: {str(e)}")
            return

    if show_quotes:
        with st.spinner(ui["extracting_quotes"]):
            quotes = st.session_state.summarizer.extract_key_quotes(
                clean_text[:5000],
                st.session_state.language
            )
            st.subheader(f"💬 {ui['key_quotes']}")
            for i, quote in enumerate(quotes, 1):
                st.write(f"{i}. *\"{quote}\"*")

    st.header(f"📋 {ui['summary_results']}")
    format_summary_display(summary_data)

    st.subheader(f"📤 {ui['export_options']}")
    col1, col2 = st.columns(2)

    with col1:
        summary_text = export_summary_to_text(summary_data, uploaded_file.name)
        st.download_button(
            label=f"📄 {ui['download_text']}",
            data=summary_text,
            file_name=f"{uploaded_file.name}_summary.txt",
            mime="text/plain",
        )

    with col2:
        summary_df = create_summary_dataframe(summary_data)
        csv_data = summary_df.to_csv(index=False)
        st.download_button(
            label=f"📊 {ui['download_csv']}",
            data=csv_data,
            file_name=f"{uploaded_file.name}_stats.csv",
            mime="text/csv",
        )

    with st.expander(f"📈 {ui['processing_stats']}"):
        st.dataframe(summary_df)
        avg_compression = summary_df["Compression Ratio"].mean()
        st.metric("Average Compression Ratio", f"{avg_compression:.2f}")
        success_rate = (summary_df["Status"] == "Success").mean() * 100
        st.metric("Success Rate", f"{success_rate:.1f}%")


if __name__ == "__main__":
    main()