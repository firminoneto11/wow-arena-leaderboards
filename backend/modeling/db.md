# Modelagem da base

## Tabela 'WowClasses'

**id** -> Integer

**blizz_id** -> Integer

**class_name** -> String(50)

**class_icon** -> Text

**updated_at** -> DateTime

## Tabela 'WowSpecs'

**id** -> Integer

**blizz_id** -> Integer

**spec_name** -> String(50)

**spec_icon** -> Text

**class_id** -> ForeignKey

**updated_at** -> DateTime

## Tabela PvpData

**id** -> Integer

**blizz_id** -> Integer

**name** -> String(100)

**class_id** -> Integer

**spec_id** -> Integer

**global_rank** -> Integer

**cr** -> Integer

**played** -> Integer

**wins** -> Integer

**losses** -> Integer

**faction_name** -> String(50)

**realm** -> String(50)

**updated_at** -> DateTime

### Processo de fetching (Implementado ou não)

-   [x] WowClasses
-   [x] SpecsWowClasses
