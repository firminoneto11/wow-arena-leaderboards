from asyncio import run, create_task, gather
from connection_layer import objects
from services.brackets_service import BracketsService as Bs, BracketsEnum
from services.sessions_service import SessionsService as Ss


async def main():

    await objects.create_all()

    tasks = []

    # Criando brackets
    tasks.append(
        create_task(Bs.create_bracket(bracket_type=BracketsEnum.twos.name))
    )

    tasks.append(
        create_task(Bs.create_bracket(bracket_type=BracketsEnum.thres.name))
    )

    tasks.append(
        create_task(Bs.create_bracket(bracket_type=BracketsEnum.rbg.name))
    )

    # Criando sessions
    tasks.append(
        create_task(Ss.create_session(session=32))
    )

    tasks.append(
        create_task(Ss.create_session(session=31))
    )

    tasks.append(
        create_task(Ss.create_session(session=30))
    )

    await gather(*tasks)

    brackets = await Bs.all_brackets()
    sessions = await Ss.all_sessions()

    print(brackets)
    print(sessions)


if __name__ == "__main__":
    run(main())
