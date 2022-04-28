# Modelagem da base

## Tabela 'WowClasses'

**id** -> Integer

**blizz_id** -> Integer

**class_name** -> String(50)

**class_icon** -> Text

## Tabela 'SpecsWowClasses'

**id** -> Integer

**blizz_id** -> Integer

**spec_name** -> String(50)

**spec_icon** -> Text

**class_id** -> ForeignKey

### Processo de fetching (Implementado ou não)

-   [x] WowClasses
-   [] SpecsWowClasses
