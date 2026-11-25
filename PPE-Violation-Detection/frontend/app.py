
import requests
import streamlit as st
from pathlib import PurePosixPath
from textwrap import dedent


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="PPE Violation Detection",
    page_icon="🦺",
    layout="wide",
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>
    .stApp {
        background: #F4F6FF;
    }

    .main-title {
        font-size: 32px;
        font-weight: 800;
        color: #172554;
    }

    .subtitle {
        color: #64748B;
        margin-bottom: 28px;
    }

    h2, h3 {
        color: #243B80 !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #E0E7FF, #F3E8FF);
        border-right: 1px solid #DDD6FE;
    }

    [data-testid="stMetric"] {
        background: white;
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #E0E7FF;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.07);
    }

    [data-testid="stMetricValue"] {
        color: #4338CA;
        font-weight: 800;
    }

    [data-testid="stFileUploader"] {
        background: #E0F2FE;
        padding: 16px;
        border: 1px dashed #38BDF8;
        border-radius: 14px;
    }

    .status-violation {
        background: #FEE2E2;
        color: #B91C1C;
        padding: 15px;
        border-left: 5px solid #EF4444;
        border-radius: 10px;
        font-weight: 700;
    }

    .status-safe {
        background: #D1FAE5;
        color: #047857;
        padding: 15px;
        border-left: 5px solid #10B981;
        border-radius: 10px;
        font-weight: 700;
    }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #2563EB, #7C3AED);
        color: white;
        border: none;
        border-radius: 9px;
        font-weight: 700;
    }

    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(90deg, #1D4ED8, #6D28D9);
        color: white;
    }

    [data-testid="stExpander"] {
        background: white;
        border: 1px solid #DDD6FE;
        border-radius: 12px;
    }

    hr {
        border-color: #D8DEEF;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def get_image_url(image_path):
    filename = PurePosixPath(
        image_path.replace("\\", "/")
    ).name

    return f"{API_URL}/processed/{filename}"


def get_history():
    try:
        response = requests.get(
            f"{API_URL}/api/history",
            timeout=15,
        )

        response.raise_for_status()

        return response.json().get("data", [])

    except requests.RequestException:
        return None


def delete_history(record_id):
    try:
        response = requests.delete(
            f"{API_URL}/api/history/{record_id}",
            timeout=15,
        )

        response.raise_for_status()

        result = response.json()

        return (
            result.get("success", False),
            result.get(
                "message",
                "Record deleted successfully."
            )
        )

    except requests.RequestException as error:
        return False, f"Unable to delete record: {error}"


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title">PPE Violation Detection System</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">AI-powered construction site safety monitoring</div>',
    unsafe_allow_html=True,
)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.title("PPE Monitor")
    st.markdown("---")

    st.write("**Dashboard**")
    st.caption("Upload an image to detect PPE violations.")

    st.markdown("---")

    st.caption("Detection model: YOLO")
    st.caption("Backend: FastAPI")
    st.caption("Database: SQLite")


# --------------------------------------------------
# IMAGE UPLOAD
# --------------------------------------------------

st.subheader("Upload Site Image")

uploaded_file = st.file_uploader(
    "Choose an image",
    type=["jpg", "jpeg", "png", "webp"],
)

if uploaded_file:

    st.image(
        uploaded_file,
        caption="Uploaded image",
        width=500,
    )

    if st.button("Run PPE Detection", type="primary"):

        with st.spinner("Analyzing image..."):

            try:
                response = requests.post(
                    f"{API_URL}/api/detect",
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type,
                        )
                    },
                    timeout=180,
                )

                response.raise_for_status()

                result = response.json()

                if result.get("success"):

                    st.session_state["last_result"] = result["data"]

                    st.success(
                        "PPE detection completed successfully."
                    )

                else:
                    st.error(
                        "Detection could not be completed."
                    )

            except requests.RequestException as error:
                st.error(f"API request failed: {error}")


# --------------------------------------------------
# LATEST DETECTION RESULT
# --------------------------------------------------

if "last_result" in st.session_state:

    result = st.session_state["last_result"]
    summary = result["summary"]

    st.markdown("---")
    st.subheader("Detection Results")

    if result["status"] == "VIOLATION DETECTED":

        st.markdown(
            '<div class="status-violation">VIOLATION DETECTED</div>',
            unsafe_allow_html=True,
        )

    elif result["status"] == "NO VIOLATION DETECTED":

        st.markdown(
            '<div class="status-safe">NO VIOLATION DETECTED</div>',
            unsafe_allow_html=True,
        )

    else:
        st.warning("NO PERSON DETECTED")

    st.write("")

    # ----------------------------------------------
    # METRIC CARDS
    # ----------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    metrics = [
        (
            col1,
            "Persons Detected",
            summary["total_persons_detected"],
            "#DBEAFE",
            "#1D4ED8",
            "#2563EB",
        ),
        (
            col2,
            "No-Helmet Detections",
            summary["missing_helmets_detected"],
            "#FFEDD5",
            "#C2410C",
            "#F97316",
        ),
        (
            col3,
            "No-Vest Detections",
            summary["missing_vests_detected"],
            "#F3E8FF",
            "#7E22CE",
            "#9333EA",
        ),
        (
            col4,
            "Total Violation Detections",
            summary["total_violations_detected"],
            "#FCE7F3",
            "#BE185D",
            "#DB2777",
        ),
    ]

    for column, label, value, bg, color, accent in metrics:

        with column:

            card_html = dedent(f"""
                <div style="
                    background:{bg};
                    border-left:5px solid {accent};
                    padding:20px;
                    border-radius:12px;
                    min-height:105px;
                    box-shadow:0 3px 10px rgba(0,0,0,0.04);
                ">
                    <div style="
                        color:{color};
                        font-size:13px;
                        font-weight:600;
                    ">
                        {label}
                    </div>

                    <div style="
                        color:{color};
                        font-size:30px;
                        font-weight:800;
                        margin-top:8px;
                    ">
                        {value}
                    </div>
                </div>
            """)

            st.html(card_html)

    # ----------------------------------------------
    # DETECTION ANALYSIS
    # ----------------------------------------------

    st.markdown("### Detection Analysis")

    image_col, details_col = st.columns(
        [2, 1],
        gap="large",
    )

    image_url = get_image_url(
        result["annotated_image"]
    )

    with image_col:

        st.markdown("#### Annotated Image")

        try:
            image_response = requests.get(
                image_url,
                timeout=15,
            )

            image_response.raise_for_status()

            st.image(
                image_response.content,
                width="stretch",
                caption="YOLO PPE detection output",
            )

        except requests.RequestException:
            st.warning(
                "Unable to load the annotated image."
            )

    with details_col:

        st.markdown("#### Violation Details")

        if result["violations"]:

            for index, violation in enumerate(
                result["violations"],
                start=1,
            ):

                violation_html = dedent(f"""
                    <div style="
                        background:#FFF1F2;
                        border-left:4px solid #E11D48;
                        border-radius:9px;
                        padding:13px;
                        margin-bottom:12px;
                    ">
                        <div style="
                            color:#9F1239;
                            font-weight:700;
                        ">
                            {index}. {violation['description']}
                        </div>

                        <div style="
                            color:#64748B;
                            font-size:13px;
                            margin-top:5px;
                        ">
                            Confidence: {violation['confidence']:.2%}
                        </div>
                    </div>
                """)

                st.html(violation_html)

        else:
            st.success(
                "No violation detections found!"
            )

        st.markdown("---")
        st.markdown("**Detection Summary**")

        st.write(
            f"Persons: {summary['total_persons_detected']}"
        )

        st.write(
            f"Helmet detections: {summary['helmets_detected']}"
        )

        st.write(
            f"Vest detections: {summary['vests_detected']}"
        )


# --------------------------------------------------
# DETECTION HISTORY
# --------------------------------------------------

st.markdown("---")
st.markdown("## Detection History")

st.caption(
    "View and manage previously processed images."
)

history = get_history()

if history is None:

    st.warning(
        "Unable to connect to detection history API."
    )

elif not history:

    st.info(
        "No detection records available yet."
    )

else:

    st.caption(
        f"Total records: {len(history)}"
    )

    for record in history:

        record_id = record["id"]

        with st.expander(
            f"Record #{record_id} | {record['status']} | "
            f"{record['created_at'][:19].replace('T', ' ')}"
        ):

            col1, col2 = st.columns([1, 2])

            with col1:

                st.write(
                    f"**Image:** {record['image_name']}"
                )

                st.write(
                    f"**Status:** {record['status']}"
                )

            with col2:

                summary = record["summary"]

                st.write(
                    f"Persons: {summary['total_persons_detected']}"
                )

                st.write(
                    f"No-Helmet Detections: "
                    f"{summary['missing_helmets_detected']}"
                )

                st.write(
                    f"No-Vest Detections: "
                    f"{summary['missing_vests_detected']}"
                )

                st.write(
                    f"Total Violations: "
                    f"{summary['total_violations_detected']}"
                )

            # --------------------------------------
            # ANNOTATED HISTORY IMAGE
            # --------------------------------------

            image_url = get_image_url(
                record["annotated_image"]
            )

            try:
                image_response = requests.get(
                    image_url,
                    timeout=15,
                )

                image_response.raise_for_status()

                st.image(
                    image_response.content,
                    caption="Annotated Detection Image",
                    width=500,
                )

            except requests.RequestException:
                st.warning(
                    "Annotated image unavailable."
                )

            st.markdown("---")

            # --------------------------------------
            # DELETE CONFIRMATION
            # --------------------------------------

            confirm_key = f"confirm_delete_{record_id}"

            if st.session_state.get(confirm_key, False):

                st.warning(
                    f"Are you sure you want to permanently "
                    f"delete Record #{record_id}?"
                )

                confirm_col, cancel_col = st.columns(2)

                with confirm_col:

                    if st.button(
                        "Yes, Delete",
                        key=f"yes_delete_{record_id}",
                        type="primary",
                        use_container_width=True,
                    ):

                        success, message = delete_history(
                            record_id
                        )

                        if success:

                            st.session_state.pop(
                                confirm_key,
                                None,
                            )

                            st.success(message)
                            st.rerun()

                        else:
                            st.error(
                                f"Deletion failed: {message}"
                            )

                with cancel_col:

                    if st.button(
                        "Cancel",
                        key=f"cancel_delete_{record_id}",
                        use_container_width=True,
                    ):

                        st.session_state.pop(
                            confirm_key,
                            None,
                        )

                        st.rerun()

            else:

                if st.button(
                    "Delete Record",
                    key=f"delete_{record_id}",
                    type="secondary",
                ):

                    st.session_state[confirm_key] = True
                    st.rerun()
