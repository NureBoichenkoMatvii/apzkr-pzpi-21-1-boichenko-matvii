import React from 'react';
import { Box, Center, Text } from '@chakra-ui/react';
import { Colors } from '@styles//colors';

const NotFound = () => (
  <Center bg={Colors.primaryBeige} p={4}>
    <Text fontSize="2xl" color={Colors.error}>404 Not Found</Text>
  </Center>
);

export default NotFound;
