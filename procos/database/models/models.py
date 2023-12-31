"""
Database models declaration.
"""

from sqlalchemy import Date, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from procos.database.models import Base


class Contracts(Base):
    __tablename__ = "contracts"

    id_: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    created_date: Mapped[Date] = mapped_column(
        Date(),
        server_default=func.current_date(),
        nullable=False,
    )
    signed_date: Mapped[Date] = mapped_column(Date(), nullable=True)
    status: Mapped[str] = mapped_column(default="draft")
    project_id_: Mapped[int] = mapped_column(ForeignKey("projects.id_"), nullable=True)
    project: Mapped["Projects"] = relationship(
        "Projects", back_populates="contracts", lazy="selectin"
    )

    def __str__(self):
        result = ""
        for k, v in self.__dict__.items():
            result += f"{k}: {v}\n"
        result += "\n"
        return result

    def to_table(self) -> dict:
        """
        Formatting of the model for nice representation in table.
        :return:
        """
        project = f"ID {self.project.id_}: {self.project.title}" if self.project else "-"
        signed = self.signed_date if self.signed_date else "-"
        return {
            "id": self.id_,
            "title": self.title,
            "status": self.status,
            "created, yy-m-d": self.created_date,
            "signed, yy-m-d": signed,
            "project ID, title": project,
        }


class Projects(Base):
    __tablename__ = "projects"

    id_: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    created_date: Mapped[Date] = mapped_column(
        Date(),
        server_default=func.current_date(),
        nullable=False,
    )
    contracts: Mapped[list["Contracts"]] = relationship(
        "Contracts", back_populates="project", lazy="selectin"
    )

    def __str__(self):
        result = ""
        for k, v in self.__dict__.items():
            result += f"{k}: {v}\n"
        result += "\n"
        return result

    def to_table(self) -> dict:
        """
        Formatting of the model for nice representation in table.
        :return:
        """
        contracts = (
            [
                f"ID {contract.id_}: {contract.title} [{contract.status}]"
                for contract in self.contracts
            ]
            if self.contracts
            else "-"
        )
        return {
            "id": self.id_,
            "title": self.title,
            "created, yy-m-d": self.created_date,
            "contracts ID, title, status": "\n".join(contracts),
        }
