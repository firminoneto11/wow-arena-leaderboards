import { Navbar } from "@mantine/core";
import { Link } from "react-router-dom";
import Button from "../Button/Button";
import { HandThreeFingers } from 'tabler-icons-react';
import { HandTwoFingers } from "tabler-icons-react";
import { ThreeDCubeSphere } from 'tabler-icons-react';


export const NavBar = () => {

    return (
        <Navbar width={{ base: 200 }} p="xs">
            <Button icon={<HandTwoFingers />} color="" label="2s" component={Link} to="/2s" />
            <Button icon={<HandThreeFingers />} color="" label="3s" component={Link} to="/" />
            <Button icon={<ThreeDCubeSphere />} color="" label="RBG" component={Link} to="/rbg" />
        </Navbar>
    );
}
