import React, { useState } from 'react';
import { Box, Button, FormControl, FormLabel, Input, Stack, Text, useToast } from '@chakra-ui/react';
import { Colors } from '@styles/colors.ts';
import { useNavigate } from 'react-router-dom';
import { LoginData } from './types.ts';
import * as ApiClient from '@api/client';
import { AppStore } from "@stores/index.ts";
import { useTranslation } from "react-i18next";

const Login = () => {
  const [loginData, setLoginData] = useState<LoginData>({username: '', password: ''});
  const toast = useToast();
  const navigate = useNavigate();
  const userStore = AppStore.useUserStore();
  const {t} = useTranslation();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const {name, value} = e.target;
    setLoginData({...loginData, [name]: value});
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    let data;
    try {
      data = await ApiClient.authJwtLoginApiV1AuthJwtLoginPost(
        {formData: loginData});
    } catch (e) {
      console.log(e);
    }
    const isSuccessful = !!data;
    if (isSuccessful) {
      userStore.authorize(data.access_token);
      toast({
        title: t('login_success'),
        status: 'success',
        duration: 2000,
        isClosable: true,
      });
      navigate('/profile');
    } else {
      toast({
        title: t('login_fail'),
        status: 'error',
        duration: 2000,
        isClosable: true,
      });
    }
  };

  return (
    <Box bg={Colors.background} h='full' py={12} px={6}>
      <Box maxW='md' mx='auto' p={8} bg={Colors.primaryBeige} borderRadius='md' boxShadow='lg'>
        <Text fontSize='2xl' mb={6} textAlign='center' color={Colors.textRegular}>{t('login_title')}</Text>
        <form onSubmit={handleSubmit}>
          <Stack spacing={4}>
            <FormControl id='email' isRequired>
              <FormLabel>{t('username_input')}</FormLabel>
              <Input type='username' name='username' value={loginData.username} onChange={handleChange} />
            </FormControl>
            <FormControl id='password' isRequired>
              <FormLabel>{t('password_input')}</FormLabel>
              <Input type='password' name='password' value={loginData.password} onChange={handleChange} />
            </FormControl>
            <Button type='submit' colorScheme='green' bg={Colors.primaryGreen} width='full'>{t('login_cta')}</Button>
          </Stack>
        </form>
      </Box>
    </Box>
  );
};

export default Login;
