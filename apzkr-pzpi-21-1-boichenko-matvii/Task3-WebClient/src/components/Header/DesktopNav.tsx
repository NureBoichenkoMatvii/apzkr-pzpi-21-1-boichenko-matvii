import React from 'react';
import {
  Box,
  Flex,
  HStack,
  Icon,
  Image,
  Link,
  Popover,
  PopoverContent,
  PopoverTrigger,
  Stack,
  Text,
  useDisclosure,
  Wrap
} from '@chakra-ui/react';
import { Colors } from '@styles/colors.ts';
import { ChevronDownIcon, ChevronRightIcon } from '@chakra-ui/icons';
import { DeviceSpecificNavbarProps, NavbarItem, NavbarItemAuthRequirement } from './types.ts';
import { AppStore } from "@stores/index.ts";

export const DesktopNav: React.FC<DeviceSpecificNavbarProps> = ({navbarItems}) => {
  const userStore = AppStore.useUserStore();

  return <HStack gap='16px'>
    {navbarItems.filter(el => {
      let accessCheckResult = true;
      if (el.isAuthRequired !== undefined)
        accessCheckResult &&= userStore.isSignedIn ? el.isAuthRequired : !el.isAuthRequired;
      if (el.roles)
        accessCheckResult &&= (!!userStore.user && el.roles.includes(userStore.user.role));
      return accessCheckResult;
    }).map((navItem) =>
      <DesktopNavItem navItem={navItem} key={navItem.label} />)}
  </HStack>
};

const DesktopNavItem: React.FC<{ navItem: NavbarItem }> = ({navItem}) => {
  const {isOpen, onOpen, onClose, onToggle} = useDisclosure();

  return (
    <Box>
      <Popover trigger='hover' placement='bottom' isOpen={isOpen} onClose={onClose}>
        <PopoverTrigger>
          <Link p='12px 24px'
                borderRadius='99px'
                href={navItem.href}
                _hover={{textDecoration: 'none', color: Colors.primaryGreen, bg: Colors.lightBeige}}
                onMouseEnter={onOpen}
                onClick={onToggle}
                display='flex'
                alignItems='center'
                gap='6px'
                textAlign='center'>
            {navItem.label}
            {navItem.children && (
              <Icon as={ChevronDownIcon}
                    transition={'all .25s ease-in-out'}
                    transform={isOpen ? 'rotate(180deg)' : ''}
                    boxSize='24px' />
            )}
          </Link>
        </PopoverTrigger>

        {navItem.children && (
          <PopoverContent border={0} boxShadow={'xl'} bg='white' p={4} w='170px' rounded={'xl'}>
            <Stack>
              {navItem.children.map((child) => (
                <DesktopSubNavItem key={child.label} {...child} />
              ))}
            </Stack>
          </PopoverContent>
        )}
      </Popover>
    </Box>
  );
};

const DesktopSubNavItem = ({label, href, iconPath}: NavbarItem) => {
  return (
    <Link href={href}
          role={'group'}
          display={'block'}
          p='8px'
          rounded={'16px'}
          _hover={{color: Colors.primaryGreen, textDecor: 'none'}}>
      <HStack align={'center'}>
        <Wrap>
          <Image src={iconPath} />
          <Text transition={'all .3s ease'}>
            {label}
          </Text>
        </Wrap>
        <Flex transition={'all .3s ease'}
              transform={'translateX(-10px)'}
              opacity={0}
              _groupHover={{opacity: '100%', transform: 'translateX(0)'}}
              justify={'flex-end'}
              align={'center'}
              flex={1}>
          <Icon color={Colors.primaryGreen} w={5} h={5} as={ChevronRightIcon} />
        </Flex>
      </HStack>
    </Link>
  );
};