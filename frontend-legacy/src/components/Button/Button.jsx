import { UnstyledButton, Group, ThemeIcon, Text } from "@mantine/core";


export default function Button({ icon, color, label, component, to }) {

    const getSettings = (theme) => ({
        display: 'block',
        width: '90%',
        padding: theme.spacing.xs,
        borderRadius: theme.radius.sm,
        color: theme.colorScheme === 'dark' ? theme.colors.dark[0] : theme.black,
        '&:hover': {
            backgroundColor:
                theme.colorScheme === 'dark' ? theme.colors.dark[6] : theme.colors.gray[0],
        },
    });

    return (
        <UnstyledButton component={component} to={to} sx={getSettings}>
            <Group>
                <ThemeIcon color={color} variant="light">
                    {icon}
                </ThemeIcon>
                <Text size="sm">{label}</Text>
            </Group>
        </UnstyledButton>
    );
}
