import { AppShell } from '@mantine/core';
import { Header } from '../components/Header/Header';
import { NavBar } from '../components/NavBar/NavBar';


export default function Base({ children }) {

    const returnStyles = (theme) => {
        return {
            main: { backgroundColor: theme.colorScheme === 'dark' ? theme.colors.dark[8] : theme.colors.gray[0] }
        }
    }

    return (
        <AppShell padding="md" header={<Header />} navbar={<NavBar />} styles={returnStyles}>
            {children}
        </AppShell>
    );
}
