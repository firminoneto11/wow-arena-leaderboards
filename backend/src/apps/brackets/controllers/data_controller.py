# from asyncio import gather

from fastapi import Request


class DataController:

    # __req: Request
    # __wow_classes: List[WowClasses]
    # __wow_specs: List[WowSpecs]

    # def __init__(self, req: Request):
    #     self.__req = req

    # def find_spec_or_class(self, tp: str, player: PvpData) -> Union[WowClassSchema, WowSpecSchema, None]:
    #     if tp == "class":
    #         for klass in self.__wow_classes:
    #             if klass.blizz_id == player.class_id:
    #                 return WowClassSchema(
    #                     id=klass.id, blizz_id=klass.blizz_id, class_name=klass.class_name, class_icon=klass.class_icon
    #                 )
    #     else:
    #         for spec in self.__wow_specs:
    #             if spec.blizz_id == player.spec_id:
    #                 return WowSpecSchema(
    #                     id=spec.id, blizz_id=spec.blizz_id, spec_name=spec.spec_name, spec_icon=spec.spec_icon
    #                 )

    # def mount_data(self, player: PvpData) -> PlayerSchema:

    #     wow_class = self.find_spec_or_class(tp="class", player=player)
    #     wow_spec = self.find_spec_or_class(tp="spec", player=player)

    #     return PlayerSchema(
    #         id=player.id,
    #         blizz_id=player.blizz_id,
    #         name=player.name,
    #         global_rank=player.global_rank,
    #         cr=player.cr,
    #         played=player.played,
    #         wins=player.wins,
    #         losses=player.losses,
    #         faction_name=player.faction_name,
    #         realm=player.realm,
    #         avatar_icon=player.avatar_icon,
    #         wow_class=wow_class,
    #         wow_spec=wow_spec,
    #     )

    # async def fetch_data_from_db(self, bracket: Brackets) -> Union[List[PlayerSchema], List]:

    #     wow_player_schema_list = []

    #     pvp_data, wow_classes, wow_specs = await gather(
    #         PvpData.objects.filter(bracket=bracket).all(), WowClasses.objects.all(), WowSpecs.objects.all()
    #     )

    #     if pvp_data and wow_classes and wow_specs:

    #         self.__wow_classes = wow_classes
    #         self.__wow_specs = wow_specs

    #         for player in pvp_data:
    #             wow_player_schema_list.append(self.mount_data(player))

    #     return wow_player_schema_list

    # async def get(self, tp: str) -> WowDataSchema:
    #     bracket = await Brackets.objects.get(type=tp)
    #     data = await self.fetch_data_from_db(bracket=bracket)
    #     return WowDataSchema(bracket_id=bracket.id, bracket_type=bracket.type, data=data, total=len(data))

    @classmethod
    async def handle(cls, request: Request, bracket: str) -> dict:
        ...
