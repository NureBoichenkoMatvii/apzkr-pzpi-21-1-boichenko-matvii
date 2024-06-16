import {FC} from 'react';
import { Box, Center, HStack, Link, VStack } from '@chakra-ui/react';
import { Colors } from "@styles/colors.ts";

export const Footer: FC = () => {
    return (
        <VStack textStyle={'footer'} w='100%' h={'50px'} bg={Colors.white} align={'center'} justify={'space-around'}>
          <Box p={'4px'}>
            © 2024 Copyright:&nbsp;
            <Link textStyle='h6' href='https://google.com/'>
              MedMobile.com
            </Link>
          </Box>
        </VStack>
    );
}