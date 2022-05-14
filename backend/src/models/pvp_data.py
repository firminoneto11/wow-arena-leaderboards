import orm as models
from connection_layer import objects
from datetime import datetime
from .brackets import Brackets
from utils import PvpDataDataclass


class PvpData(models.Model):
    tablename = "pvp_data"
    registry = objects
    fields = {
        "id": models.Integer(primary_key=True, index=True),  # N tem no PvpDataDataclass
        "blizz_id": models.Integer(),
        "name": models.String(max_length=100),
        "class_id": models.Integer(allow_null=True),
        "spec_id": models.Integer(allow_null=True),
        "global_rank": models.Integer(),
        "cr": models.Integer(),
        "played": models.Integer(),
        "wins": models.Integer(),
        "losses": models.Integer(),
        "faction_name": models.String(max_length=50),
        "realm": models.String(max_length=50),
        "avatar_icon": models.Text(allow_null=True),
        "bracket": models.ForeignKey(to=Brackets, on_delete=models.CASCADE),  # N tem no PvpDataDataclass
        "updated_at": models.DateTime(default=lambda: datetime.now())  # N tem no PvpDataDataclass
    }


async def create_pvp_data(pd: PvpDataDataclass, bracket: Brackets):
    try:
        p_data = await PvpData.objects.get(blizz_id=pd.blizz_id, bracket=bracket)
    except models.NoMatch:
        await PvpData.objects.create(**pd.to_dict(), bracket=bracket)
    except models.MultipleMatches as err:
        print(f"Multiple matches for: {err}")  # Bem raro de ocorrer
    else:

        # Criando dois dicionários: Um contém os valores que estavam no banco e o outro contém os valores que acabaram de ser buscados
        old_values = p_data.__dict__
        new_values = pd.to_dict()

        # Criando um dicionário para guardar apenas os dados que foram alterados
        altered_values = dict()

        # Iterando nos campos antigos
        for key in old_values.keys():

            # Checando se a chave é um campo que existe no 'PvpDataDataclass'
            if key != 'bracket' and key != 'id' and key != 'updated_at':

                # Checando se o valor que está no banco é diferente do que está no 'PvpDataDataclass'
                if old_values[key] != new_values[key]:

                    # Caso seja, atualizar o 'altered_values' dict com o novo valor
                    altered_values[key] = new_values[key]

            elif key == 'updated_at':

                # Mudando o dado no campo 'updated_at'
                altered_values[key] = datetime.now()

        # Atualizando a instância com os dados que foram modificados
        await p_data.update(**altered_values)
