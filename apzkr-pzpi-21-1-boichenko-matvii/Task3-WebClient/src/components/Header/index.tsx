import { Box, Collapse, Flex, HStack, IconButton, Image, Link, useDisclosure } from '@chakra-ui/react';
import React from 'react';
import { CloseIcon, HamburgerIcon } from '@chakra-ui/icons';
import { Colors } from '@styles/colors.ts';
import { MobileNav } from './MobileNav.tsx';
import { DesktopNav } from './DesktopNav.tsx';
import { NavbarItem } from './types.ts';
import { UserRole } from "@stores/User/types.ts";

export const NavbarItems: Array<NavbarItem> = [
  {label: 'home_header', href: `/home`},
  {label: 'login_header', href: '/login', isAuthRequired: false},
  {label: 'register_header', href: '/register', isAuthRequired: false},
  {label: 'profile_header', href: '/profile', isAuthRequired: true},
  {label: 'medicine_header', href: '/medicines', isAuthRequired: true, roles: [UserRole.Customer]},
  {label: 'cart_header', href: '/card', isAuthRequired: true, roles: [UserRole.Customer]},
  {label: 'my_orders_header', href: '/profile/orders', isAuthRequired: true, roles: [UserRole.Customer]},
  {
    label: 'deliverer_header',
    roles: [UserRole.Deliverer],
    children: [
      {
        label: 'machines_header',
        href: '/deliverer/machines',
        isAuthRequired: true
      },
      {
        label: 'statistics_header',
        href: '/deliverer/statistics',
        isAuthRequired: true
      },
    ]
  },
];

export const Header: React.FC = props => {
  const {isOpen, onToggle} = useDisclosure();

  return (
    <Box w='full' position='sticky' top={0} zIndex={1000} pos='absolute' color={Colors.gray700} textStyle='header'>
      <HStack minH={'72px'}
              w='full'
              px={{base: '16px', lg: '32px'}}
              bg={{base: (isOpen ? 'white' : 'transparent'), lg: 'white'}}
              borderBottom={isOpen ? 1 : 0}
              borderStyle={'solid'}
              borderColor='gray.200'
              align={'center'}
              justify='space-between'>
        <Flex flex={1} align='center' justify={{base: 'start', lg: 'center'}} gap='40px'>
          <Link href='/home'>
            <Image src={'/img/medmobile-logo.png'} objectFit='contain' h='50px' />
          </Link>

          <Flex display={{base: 'none', lg: 'flex'}}>
            <DesktopNav navbarItems={NavbarItems} />
          </Flex>
        </Flex>

        <IconButton id='navbar_menu_button_mobile'
                    _hover={{}}
                    display={{base: 'flex', lg: 'none'}}
                    onClick={onToggle}
                    icon={isOpen ? <CloseIcon boxSize='20px' /> : <HamburgerIcon boxSize='24px' />}
                    variant={'ghost'}
                    aria-label={'Toggle Navigation'} />
      </HStack>

      <Collapse in={isOpen} animateOpacity>
        <MobileNav navbarItems={NavbarItems} />
      </Collapse>
    </Box>
  );
};
