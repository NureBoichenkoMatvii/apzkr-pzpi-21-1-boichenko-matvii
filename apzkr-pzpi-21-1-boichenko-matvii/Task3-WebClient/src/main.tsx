import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'
import { Router } from './router.tsx';
import { theme } from './styles/theme.ts';
import { RouterProvider } from 'react-router-dom';
import { ChakraProvider, ColorModeScript } from '@chakra-ui/react';
import { ApiProvider } from "@api/wrapper.tsx";


export const RootComponent = () => {
  console.log(import.meta.env)
  console.log(process.env)

  const rootJSX = <>
    <ColorModeScript />
    <ChakraProvider theme={theme}>
      <ApiProvider>
        <RouterProvider router={Router} />
      </ApiProvider>
    </ChakraProvider>
  </>

  if (process.env.NODE_ENV === 'development') {
    return <React.StrictMode>
      {rootJSX}
    </React.StrictMode>
  }

  return rootJSX;
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <RootComponent />,
)
