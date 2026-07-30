import streamlit as st
import torch
import tempfile
import os

from input import load
from solver import solve
from output import write_single
from model import AI
from visualize import create_figure

st.set_page_config(
    page_title="Cargo Packing Optimizer",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Intelligent Cargo Packing & Spatial Neuro-Optimization")
st.write("Upload a cargo manifest and run the optimizer.")

uploaded_file = st.file_uploader(
    "Upload Manifest CSV",
    type=["csv"]
)

if uploaded_file is not None:

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(uploaded_file.getbuffer())
        csv_path = tmp.name

    try:
        packages, ulds, K = load(csv_path)

        st.success("✅ Manifest loaded successfully!")

        st.write(f"**Packages:** {len(packages)}")
        st.write(f"**ULDs:** {len(ulds)}")

    except Exception as e:
        st.error(f"Manifest validation failed:\n\n{e}")
        st.stop()

    # Load AI model
    model = AI()
    model.load_state_dict(torch.load("pretrained.pt", map_location="cpu"))
    model.eval()

st.divider()

if st.button("🚀 Run Optimization"):

    with st.spinner("Running optimization..."):
        result, pct_store = solve(packages, ulds, K, model)
        write_single(result, out_dir="output")

    st.success("Optimization completed!")

    summary = result["summary"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Cost", summary["total_cost"])
    col2.metric("Packed Packages", summary["total_packed_packages"])
    col3.metric("Priority ULDs", summary["number_of_priority_ulds"])
    col4.metric("Feasible", "Yes" if summary["is_feasible"] else "No")

    st.header("📦 3D Cargo Placement")

    for uld in ulds:
        st.subheader(f"ULD: {uld.id}")
        fig = create_figure(uld)
        st.plotly_chart(fig, use_container_width=True)

    st.header("Package Report")

    tab1, tab2 = st.tabs(["Packed", "Unpacked"])

    with tab1:
        st.dataframe(result["placements"], use_container_width=True)

    with tab2:
        st.dataframe(result["unpacked"], use_container_width=True)

    with open("output/solution.txt", "rb") as f:
        st.download_button(
            "⬇ Download solution.txt",
            data=f,
            file_name="solution.txt",
            mime="text/plain"
        )
