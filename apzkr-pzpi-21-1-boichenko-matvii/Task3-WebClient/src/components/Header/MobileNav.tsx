import { Collapse, HStack, Icon, Image, Link, Stack, Text, useDisclosure, VStack, Wrap } from '@chakra-ui/react';
import { ChevronDownIcon } from '@chakra-ui/icons';
import React from 'react';
import { DeviceSpecificNavbarProps, NavbarItem } from './types.ts';
import { AppStore } from "@stores/index.ts";

export const MobileNav: React.FC<DeviceSpecificNavbarProps> = ({navbarItems}) => {
  const userStore = AppStore.useUserStore();

  return (
    <Stack bg={'white'} w={'100%'} display={{lg: 'none'}} h='calc(100vh - 72px)' position='absolute' overflow='auto'>
      <VStack overflowY='auto' gap='20px' align='flex-start' py='20px'>
        {navbarItems.filter(el => {
          let accessCheckResult = true;
          if (el.isAuthRequired !== undefined)
            accessCheckResult &&= userStore.isSignedIn ? el.isAuthRequired : !el.isAuthRequired;
          if (el.roles)
            accessCheckResult &&= (!!userStore.user && el.roles.includes(userStore.user.role));
          return accessCheckResult;
        }).map((navItem) => (
          <MobileNavItem key={navItem.label} {...navItem} />
        ))}
      </VStack>
    </Stack>
  );
};

const MobileNavItem = ({label, children, href, iconPath}: NavbarItem) => {
  const {isOpen, onToggle, onOpen, onClose} = useDisclosure();

  return (
    <Stack w='100%' spacing={4}
           {...(children && {onClick: onToggle, onMouseEnter: onOpen, onMouseLeave: onClose})} p='0px 16px'>
      <HStack py='8px'
              as={Link}
              href={href}
              justify={'space-between'}
              align={'center'}
              _hover={{textDecoration: 'none',}}>
        <Wrap>
          {iconPath && <Image src={iconPath} />}
          <Text>{label}</Text>
        </Wrap>
        {children && (
          <Icon as={ChevronDownIcon}
                transition={'all .25s ease-in-out'}
                transform={isOpen ? 'rotate(180deg)' : ''}
                boxSize='24px' />
        )}
      </HStack>

      <Collapse in={isOpen} animateOpacity style={{marginTop: '0!important'}}>
        <Stack align={'start'}>
          {children &&
            children.map((child) => (
              <Link key={child.label} py='8px' href={child.href} _hover={{textDecoration: 'none'}}>
                <Wrap>
                  <Image src={child.iconPath} />
                  {child.label}
                </Wrap>
              </Link>
            ))}
        </Stack>
      </Collapse>
    </Stack>
  );
};
