import { Title, Header as MantineHeader } from "@mantine/core";


export const Header = () => {

    const setHeaderTitleColor = (theme) => {
        return {
            color: theme.colorScheme === 'dark' ? theme.colors.gray[0] : theme.colors.dark[8]
        }
    }

    return (
        <MantineHeader height={60} p="xs">
            <Title sx={setHeaderTitleColor} order={1}>Leaderboards BR</Title>
        </MantineHeader>
    );
}
