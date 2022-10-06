from asyncio import gather, to_thread as as_async
from os.path import exists
from pathlib import Path
from os import mkdir
import json

from ..schemas import PvpDataSchema, WowClassSchema, WowSpecsSchema
from ..fetcher.fetch_pvp_data import PvpDataType
from ..constants import BASE_DIR


async def dump_data(pvp_data: PvpDataType, wow_classes: list[WowClassSchema], wow_specs: list[WowSpecsSchema]) -> None:
    """Dumps data to a json file"""

    def write_to_json(data, filename: Path) -> None:
        with open(file=filename, mode="w", encoding="utf-8") as f:
            f.write(json.dumps(data))

    def make_dir(directory: Path) -> None:
        if not exists(directory):
            mkdir(directory)

    _wow_classes = [el.dict() for el in wow_classes]
    _wow_specs = [el.dict() for el in wow_specs]
    _pvp_data = {
        "_2s": [el.dict() for el in pvp_data["_2s"]],
        "_3s": [el.dict() for el in pvp_data["_3s"]],
        "rbg": [el.dict() for el in pvp_data["rbg"]],
    }

    JSON_DIR = BASE_DIR / "json_data"

    await as_async(make_dir, JSON_DIR)
    await gather(
        as_async(write_to_json, data=_pvp_data, filename=JSON_DIR / "pvp_data.json"),
        as_async(write_to_json, data=_wow_classes, filename=JSON_DIR / "wow_classes.json"),
        as_async(write_to_json, data=_wow_specs, filename=JSON_DIR / "wow_specs.json"),
    )


async def read_data() -> tuple[PvpDataType, list[WowClassSchema], list[WowSpecsSchema]]:
    """Reads data from json files"""

    def read_pvp_data(path: Path) -> PvpDataType:
        with open(file=path, mode="r", encoding="utf-8") as f:
            json_data = json.load(fp=f)
            return {
                "_2s": [PvpDataSchema(**el) for el in json_data["_2s"]],
                "_3s": [PvpDataSchema(**el) for el in json_data["_3s"]],
                "rbg": [PvpDataSchema(**el) for el in json_data["rbg"]],
            }

    def read_wow_classes_data(path: Path) -> list[WowClassSchema]:
        with open(file=path, mode="r", encoding="utf-8") as f:
            json_data = json.load(fp=f)
            return [WowClassSchema(**el) for el in json_data]

    def read_wow_specs_data(path: Path) -> list[WowSpecsSchema]:
        with open(file=path, mode="r", encoding="utf-8") as f:
            json_data = json.load(fp=f)
            return [WowSpecsSchema(**el) for el in json_data]

    JSON_DIR = BASE_DIR / "json_data"

    return await gather(
        as_async(read_pvp_data, JSON_DIR / "pvp_data.json"),
        as_async(read_wow_classes_data, JSON_DIR / "wow_classes.json"),
        as_async(read_wow_specs_data, JSON_DIR / "wow_specs.json"),
    )
