from asyncio import gather


async def create_default_data() -> None:
    from apps.brackets.models.brackets import Brackets, BracketsEnum

    brackets: list[str] = [BracketsEnum[el].value for el in BracketsEnum._member_names_]
    await gather(*[Brackets.objects.get_or_create({"name": bracket}) for bracket in brackets])
