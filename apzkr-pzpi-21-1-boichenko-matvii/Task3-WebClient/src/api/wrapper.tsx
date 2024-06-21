import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactNode } from 'react';

export const queryClient = new QueryClient();

type ApiProviderProps = {
  children: ReactNode;
};

// Api provider is used to provide the react-query client to the whole app
export const ApiProvider = ({children}: ApiProviderProps): JSX.Element => {
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
};
