from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.database import Base


class DetectionRecord(Base):

    __tablename__ = "detection_records"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    image_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    annotated_image: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    total_persons_detected: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    helmets_detected: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    missing_helmets_detected: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    vests_detected: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    missing_vests_detected: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    total_violations_detected: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
