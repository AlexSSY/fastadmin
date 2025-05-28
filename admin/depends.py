from fastapi import Query


class PaginationParams:
    per_page = 15

    def __init__(
        self,
        # limit: int = Query(10, ge=1, le=100),
        # offset: int = Query(0, ge=0)
        page: int = Query(1, ge=1)
    ):
        self.limit = PaginationParams.per_page
        self.offset = PaginationParams.per_page * (page - 1)
        self._page = page

    @property
    def page(self):
        return self._page
