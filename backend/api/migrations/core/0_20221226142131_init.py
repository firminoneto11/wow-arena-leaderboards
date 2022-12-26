from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE "sessions" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "session" INT NOT NULL
);
CREATE TABLE "wow_classes" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "blizzard_id" BIGINT NOT NULL,
    "name" VARCHAR(100) NOT NULL,
    "icon_url" TEXT
);
CREATE TABLE "wow_specs" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "blizzard_id" BIGINT NOT NULL,
    "name" VARCHAR(100) NOT NULL,
    "icon_url" TEXT
);
CREATE TABLE "pvp_data" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "blizzard_id" BIGINT NOT NULL,
    "name" VARCHAR(100) NOT NULL,
    "global_rank" INT NOT NULL,
    "cr" INT NOT NULL,
    "played" INT NOT NULL,
    "wins" INT NOT NULL,
    "losses" INT NOT NULL,
    "faction_name" VARCHAR(100) NOT NULL,
    "realm" VARCHAR(100) NOT NULL,
    "bracket" VARCHAR(10) NOT NULL,
    "avatar_icon" TEXT,
    "session_id" INT NOT NULL REFERENCES "sessions" ("id") ON DELETE CASCADE,
    "wow_class_id" INT REFERENCES "wow_classes" ("id") ON DELETE SET NULL,
    "wow_spec_id" INT REFERENCES "wow_specs" ("id") ON DELETE SET NULL
);
CREATE TABLE "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
