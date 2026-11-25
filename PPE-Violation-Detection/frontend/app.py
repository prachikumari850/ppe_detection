import requests
import streamlit as st
from pathlib import PurePosixPath


API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="PPE Violation Detection",
    page_icon="🦺",
    layout="wide",
)

st.markdown("""
<style>
    .main-title {
        font-size: 30px;
        font-weight: 700;
        color: #1e293b;
    }
    .subtitle {
        color: #64748b;
        margin-bottom: 25px;
    }
    .status-violation {
        background: #fee2e2;
        color: #b91c1c;
        padding: 14px;
        border-radius: 8px;
        font-weight: 700;
    }
    .status-safe {
        background: #dcfce7;
        color: #15803d;
        padding: 14px;
        border-radius: 8px;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)


def get_image_url(image_path):
    filename = PurePosixPath(image_path.replace("\\", "/")).name
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


st.markdown(
    '<div class="main-title">PPE Violation Detection System</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">AI-powered construction site safety monitoring</div>',
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.title("PPE Monitor")
    st.markdown("---")
    st.write("**Dashboard**")
    st.caption("Upload an image to detect PPE violations.")
    st.markdown("---")
    st.caption("Detection model: YOLO")
    st.caption("Backend: FastAPI")
    st.caption("Database: SQLite")


# Image upload
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
                    st.success("PPE detection completed successfully.")
                else:
                    st.error("Detection could not be completed.")

            except requests.RequestException as error:
                st.error(f"API request failed: {error}")


# Latest detection result
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

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
    "Persons Detected",
    summary["total_persons_detected"],
    )
    col2.metric(
        "No-Helmet Detections",
        summary["missing_helmets_detected"],
    )
    col3.metric(
        "No-Vest Detections",
        summary["missing_vests_detected"],
    )
    col4.metric(
        "Total Violation Detections",
        summary["total_violations_detected"],
    )

    st.markdown("### Annotated Image")

    image_url = get_image_url(result["annotated_image"])

    try:
        image_response = requests.get(image_url, timeout=15)
        image_response.raise_for_status()
        st.image(
            image_response.content,
            caption="AI detection output",
            use_container_width=True,
        )
    except requests.RequestException:
        st.warning("Unable to load the annotated image.")

    st.markdown("### Violation Details")

    if result["violations"]:
        for index, violation in enumerate(result["violations"], start=1):
            st.write(
                f"{index}. **{violation['description']}** "
                f"— Confidence: {violation['confidence']:.2%}"
            )
    else:
        st.info("No violation detections found.")


# Detection history
st.markdown("---")
st.subheader("Detection History")

history = get_history()

if history is None:
    st.warning("Unable to connect to the detection history API.")
elif not history:
    st.info("No detection records available yet.")
else:
    st.caption(f"Total records: {len(history)}")

    for record in history:
        with st.expander(
            f"Record #{record['id']} | {record['status']} | "
            f"{record['created_at'][:19].replace('T', ' ')}"
        ):
            col1, col2 = st.columns([1, 2])

            with col1:
                st.write(f"**Image:** {record['image_name']}")
                st.write(f"**Status:** {record['status']}")

            with col2:
                summary = record["summary"]
                st.write(
                    f"Persons detected: {summary['total_persons_detected']}  |  "
                    f"No-helmet detections: {summary['missing_helmets_detected']}  |  "
                    f"No-vest detections: {summary['missing_vests_detected']}"
                )
                st.write(
                    f"Total detected violations: "
                    f"{summary['total_violations_detected']}"
                )

            image_url = get_image_url(record["annotated_image"])

            try:
                image_response = requests.get(image_url, timeout=15)
                image_response.raise_for_status()
                st.image(
                    image_response.content,
                    caption="Detection result",
                    width=500,
                )
            except requests.RequestException:
                st.caption("Annotated image unavailable.")
