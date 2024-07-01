from _datetime import datetime

from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database.database import Base


class CommonCode(Base):
    __tablename__ = "tb_notify_common_codes"
    code = Column(String(30), primary_key=True)
    code_name = Column(String(20), nullable=False)
    type = Column(String(20), nullable=False)


class Notification(Base):
    __tablename__ = "tb_notify_notifications"
    notification_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    notification_code = Column(String(30), ForeignKey("tb_notify_common_codes.code"))
    data = Column(JSONB, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    reg_dtm = Column(DateTime, nullable=False, default=datetime.now)
    type_common_code = relationship("CommonCode")
    is_del = Column(Boolean, nullable=False, default=False)
