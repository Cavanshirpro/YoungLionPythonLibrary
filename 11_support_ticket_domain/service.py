from __future__ import annotations
from repository import TicketRepository


class TicketService:
    def __init__(self, repository: TicketRepository):
        self.repository = repository

    def demo(self):
        urgent = self.repository.where(status="open", priority__ge=4)
        for ticket in urgent:
            if not ticket.assigned: ticket.assign()
        return [(t.id, t.subject, t.assigned, t.requester.tier) for t in urgent]
