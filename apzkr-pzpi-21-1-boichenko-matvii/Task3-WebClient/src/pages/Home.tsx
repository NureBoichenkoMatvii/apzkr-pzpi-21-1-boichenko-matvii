import React from 'react';
import { Box, Text } from '@chakra-ui/react';
import { Colors } from '@styles/colors';
import { useTranslation } from "react-i18next";

const Home = () => {
  const {t} = useTranslation();

  return (<Box bg={Colors.primaryBeige} p={4}>
      <Text fontSize='2xl' color={Colors.textRegular} textAlign='center'>{t('home_title')}</Text>
    </Box>
  )
};

export default Home;
