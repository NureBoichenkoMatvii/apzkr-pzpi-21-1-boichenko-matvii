import { Stack, VStack } from '@chakra-ui/react';
import { Outlet, useNavigate } from 'react-router-dom';
import { Colors } from '@styles/colors.ts';
import { Header } from '@components/Header';
import { Footer } from "@components/Footer";
import { useEffect } from "react";
import { OpenAPI } from "@api/client";
import { HttpStatusCode } from "axios";
import { AppStore } from "@stores/index.ts";


export function Main(props: unknown) {
  const userStore = AppStore.useUserStore();
  const navigate = useNavigate();
  useEffect(() => {
    if (!OpenAPI.TOKEN) {
      OpenAPI.TOKEN = userStore.token || '';
    }
    OpenAPI.BASE = process.env.API_URL!;
    OpenAPI.interceptors.request.use((config) => {
      if (!config.headers?.Authorization) {
        config.headers = {...config.headers, Authorization: `Bearer ${OpenAPI.TOKEN}`};
      }
      return config;
    });
    OpenAPI.interceptors.response.use((resp) => {
      if (resp.status === HttpStatusCode.Unauthorized) {
        userStore.onSignOut();
        navigate('/login');
      }
      return resp;
    });
  }, []);

  return <VStack minHeight={'100vh'} bg={Colors.background} gap={0} textStyle='body'>
    <Header />
    <Stack flex={1} h='full' width='100%' direction='column' pt={{base: '72px', lg: '70px'}}>
      <Outlet />
    </Stack>
    <Footer />
  </VStack>
}
