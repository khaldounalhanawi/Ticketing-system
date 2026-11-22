from enum import Enum

from pydantic import BaseModel, Field


class Category(str, Enum):
	billing = "billing"
	technical = "technical"
	account = "account"
	other = "other"


class Priority(str, Enum):
	low = "low"
	medium = "medium"
	high = "high"


class TicketTriage(BaseModel):
	"""The validated result ScoutBot must produce for every ticket."""

	category: Category
	priority: Priority
	suggested_owner: str = Field(
		description="Team or person who should handle this ticket, e.g. 'billing-team'."
	)
