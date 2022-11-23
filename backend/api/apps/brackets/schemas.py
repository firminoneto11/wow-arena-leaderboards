from .models import PvpData, Sessions


class BracketsResponseSchema(
    PvpData.get_pydantic(
        exclude={
            "wow_class": {"id", "created_at", "updated_at"},
            "wow_spec": {"id", "created_at", "updated_at"},
        }
    )
):
    session: int | Sessions

    def dict(self, *args, **kwargs) -> dict:
        data = super().dict(*args, **kwargs)
        if isinstance(self.session, Sessions):
            data["session"] = self.session.session
        return data
