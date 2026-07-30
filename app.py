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

if "result" not in st.session_state:
    st.session_state.result = None

if "ulds" not in st.session_state:
    st.session_state.ulds = None


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

        st.session_state.result = result
        st.session_state.ulds = ulds

    st.success("Optimization completed!")

if st.session_state.result is not None:

    result = st.session_state.result
    ulds = st.session_state.ulds

    summary = result["summary"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Cost", summary["total_cost"])
    col2.metric("Packed Packages", summary["total_packed_packages"])
    col3.metric("Priority ULDs", summary["number_of_priority_ulds"])
    col4.metric("Feasible", "Yes" if summary["is_feasible"] else "No")

    # ... then keep ALL your existing code:
    # Step-by-Step Placement
    # Current Placement
    # Package Report
    # Download Button

    st.header("📦 Step-by-Step Placement")

    selected_uld = st.selectbox(
        "Select ULD",
        [u.id for u in ulds]
    )

    current_uld = next(u for u in ulds if u.id == selected_uld)

    num_packages = len(current_uld.placed_packages)

    if num_packages == 0:
        st.warning("No packages placed in this ULD.")
    else:

        step = st.slider(
            "Placement Step",
            1,
            num_packages,
            num_packages
        )

        st.write(f"Showing first **{step}** of **{num_packages}** packages.")

        fig = create_figure(current_uld, step)

        st.plotly_chart(fig, use_container_width=True)

        current_package = current_uld.placed_packages[step - 1]

        st.subheader("Current Placement")

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Package:** {current_package.id}")
            st.write(f"**ULD:** {current_uld.id}")
            st.write(f"**Type:** {current_package.package_type}")
            st.write(f"**Weight:** {current_package.weight}")

        with col2:
            st.write(
                f"**Position:** "
                f"({current_package.pos[0]}, "
                f"{current_package.pos[1]}, "
                f"{current_package.pos[2]})"
            )

            st.write(
                f"**Orientation:** "
                f"{current_package.ori[0]} × "
                f"{current_package.ori[1]} × "
                f"{current_package.ori[2]}"
            )

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
