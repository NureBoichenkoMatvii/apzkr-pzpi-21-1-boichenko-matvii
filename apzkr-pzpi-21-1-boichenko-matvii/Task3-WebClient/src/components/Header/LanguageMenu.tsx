import React, { useEffect } from 'react';
import { AppStore } from "@stores/index.ts";
import { useTranslation } from "react-i18next";
import {
  Box,
  Collapse,
  Flex,
  HStack,
  Icon,
  Link,
  Popover,
  PopoverContent,
  PopoverTrigger,
  Stack,
  Text,
  useBreakpointValue,
  useDisclosure,
  Wrap
} from "@chakra-ui/react";
import { ChevronDownIcon, ChevronRightIcon } from "@chakra-ui/icons";
import i18n from "@services/i18n";
import { Colors } from "@styles/colors.ts";

const languages = ['ENG', 'UKR'];

const LanguageMenu = () => {
  const {t} = useTranslation();
  const {setLanguage, language} = AppStore.useUserStore();
  const {isOpen, onToggle, onOpen, onClose} = useDisclosure();

  const isDesktop = useBreakpointValue({base: false, lg: true})!;
  const handleLanguageItemClick = (selectedLanguage: string | 'ENG' | 'UKR') => {
    console.log("selectedLanguage", selectedLanguage);
    i18n.changeLanguage(selectedLanguage.toLowerCase());
    setLanguage(selectedLanguage);
  };

  if (!isDesktop) {
    return (<Stack w='100%' spacing={4}
                   {...{onClick: onToggle, onMouseEnter: onOpen, onMouseLeave: onClose}} p='0px 16px'>
      <HStack py='8px' justify={'space-between'} align={'center'} _hover={{textDecoration: 'none'}}>
        <Wrap>
          <Text>{t(language.toUpperCase())}</Text>
        </Wrap>
        <Icon as={ChevronDownIcon}
              transition={'all .25s ease-in-out'}
              transform={isOpen ? 'rotate(180deg)' : ''}
              boxSize='24px' />
      </HStack>

      <Collapse in={isOpen} animateOpacity style={{marginTop: '0!important'}}>
        <Stack align={'start'}>
          {languages.map((name) => (
            <Wrap key={name} py='8px' onClick={() => handleLanguageItemClick(name)}>
              {/*<Image src={child.iconPath} />*/}
              {t(name)}
            </Wrap>
          ))}
        </Stack>
      </Collapse>
    </Stack>);
  } else {
    return (
      <Box>
        <Popover trigger='hover' placement='bottom' isOpen={isOpen} onClose={onClose}>
          <PopoverTrigger>
            <Link p='12px 24px'
                  borderRadius='99px'
                  _hover={{textDecoration: 'none', color: Colors.primaryGreen, bg: Colors.lightBeige}}
                  onMouseEnter={onOpen}
                  onClick={onToggle}
                  display='flex'
                  alignItems='center'
                  gap='6px'
                  textAlign='center'>
              <Wrap>
                <Text>{t(language.toUpperCase())}</Text>
              </Wrap>
              {languages && (
                <Icon as={ChevronDownIcon}
                      transition={'all .25s ease-in-out'}
                      transform={isOpen ? 'rotate(180deg)' : ''}
                      boxSize='24px' />
              )}
            </Link>
          </PopoverTrigger>
          <PopoverContent border={0} boxShadow={'xl'} bg='white' p={4} w='auto' rounded={'xl'}>
            <Stack>
              {languages.map((name) => (
                <Link key={name}
                      role={'group'}
                      display={'block'}
                      p='8px'
                      rounded={'16px'}
                      _hover={{color: Colors.primaryGreen, textDecor: 'none'}}
                      onClick={() => handleLanguageItemClick(name)}>
                  <HStack align={'center'}>
                    <Wrap>
                      {/*<Image src={iconPath} />*/}
                      <Text transition={'all .3s ease'}>
                        {t(name)}
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
              ))}
            </Stack>
          </PopoverContent>
        </Popover>
      </Box>
    );
  }
};

export default LanguageMenu;
