from sqlalchemy import ForeignKey, Date, func, CheckConstraint, String
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from procos.database.models import Base


class Contracts(Base):
    __tablename__ = "contracts"

    id_: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    created_date: Mapped[Date] = mapped_column(Date(),
                                               server_default=func.current_date(),
                                               nullable=False,
                                               )
    signed_date: Mapped[Date] = mapped_column(Date(), nullable=True)
    status: Mapped[str] = mapped_column(default='draft')
    # CheckConstraint(r"contracts.status IN ('draft', 'active', 'closed')"
    project_id_: Mapped[int] = mapped_column(ForeignKey('projects.id_'))
    project: Mapped['Contracts'] = relationship(back_populates='contracts')


class Projects(Base):
    __tablename__ = "projects"

    id_: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    created_date: Mapped[Date] = mapped_column(Date(),
                                               server_default=func.current_date(),
                                               nullable=False,
                                               )
    contracts: Mapped[list['Contracts']] = relationship(back_populates='project')
