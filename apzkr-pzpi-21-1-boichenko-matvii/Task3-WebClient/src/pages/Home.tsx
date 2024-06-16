import React from 'react';
import { Box, Text } from '@chakra-ui/react';
import { Colors } from '@styles/colors';

const Home = () => (
  <Box bg={Colors.primaryBeige} p={4}>
    <Text fontSize="2xl" color={Colors.textRegular} textAlign='center'>Welcome to MedMobile Home</Text>
  </Box>
);

export default Home;
