import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Center,
  HStack,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  NumberDecrementStepper,
  NumberIncrementStepper,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  Stack,
  Text,
  useDisclosure,
  useToast,
  VStack,
  Wrap,
} from '@chakra-ui/react';
import * as ApiClient from '@api/client';
import { CreateOrderDto, MachineResponseDto, PickupPointResponseDto } from '@api/client';
import { AppStore } from '@stores/index';
import { Colors } from '@styles/colors';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

type MedicineInfoDto = {
  id: string;
  count: number;
};

const Cart = () => {
  const {t} = useTranslation();
  const {user, cart, changeCartMedicineCount, deleteMedicineFromCart, clearCart} = AppStore.useUserStore();
  const [pickupPoint, setPickupPoint] = useState<PickupPointResponseDto | null>(null);
  const [machine, setMachine] = useState<MachineResponseDto | null>(null);
  const [pickupPoints, setPickupPoints] =
    useState<PickupPointResponseDto[]>([]);
  const [machines, setMachines] =
    useState<MachineResponseDto[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const {isOpen, onOpen, onClose} = useDisclosure();
  const {isOpen: isMachineOpen, onOpen: onMachineOpen, onClose: onMachineClose} = useDisclosure();
  const toast = useToast();
  const navigate = useNavigate();

  const {mutate: fetchPickupPoints} = useMutation({
    mutationFn: async () => await ApiClient.searchPointsApiV1PickupPointsSearchPost({
      requestBody: {},
    }),
    onSuccess: (data) => {
      setPickupPoints(data);
    },
    onError: (error) => {
      console.error('Error fetching pickup points', error);
      toast({
        title: t('pickup_points_fetch_error'),
        status: 'error',
        duration: 2000,
        isClosable: true,
      });
    },
  });

  const {mutate: fetchMachines} = useMutation({
    mutationFn: async () => await ApiClient.searchMachinesApiV1MachinesSearchPost({
      requestBody: {simple_filters: {}, medicines: {}, order_by: null},
    }),
    onSuccess: (data) => {
      setMachines(data);
    },
    onError: (error) => {
      console.error('Error fetching machines', error);
      toast({
        title: t('fetch_machines_error'),
        status: 'error',
        duration: 2000,
        isClosable: true,
      });
    },
  });

  const handleCreateOrder = async () => {
    if (!pickupPoint) {
      toast({
        title: t('unselected_pickup_point_error'),
        status: 'error',
        duration: 2000,
        isClosable: true,
      });
      return;
    }

    setIsLoading(true);

    const medicines: MedicineInfoDto[] = (cart.medicines || []).map((m) => ({
      id: m.id,
      count: m.count,
    }));

    const orderData: CreateOrderDto = {
      user_id: user?.id || '',
      machine_id: machine ? machine.id : null,
      pickup_point_id: pickupPoint.id,
      status: machine ? 2 : 1, // In preparing if machine specified, just payed if not
      payment_currency: 'EUR',
      medicines,
    };

    try {
      await ApiClient.createOrderApiV1OrdersPost({requestBody: orderData});
      toast({
        title: t('create_order_success'),
        status: 'success',
        duration: 2000,
        isClosable: true,
      });
      clearCart();
      navigate('/profile/orders');
    } catch (error) {
      console.error('Error creating order', error);
      toast({
        title: t('create_order_error'),
        status: 'error',
        duration: 2000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPickupPoints();
    fetchMachines();
  }, []);

  return (
    <Center w='full' h='full'>
      <VStack bg={Colors.primaryBeige}
              align={'start'}
              gap={'20px'}
              h='full'
              w={{base: '90%', lg: '60%'}}
              p={8}
              my='30px'
              borderRadius='md'
              boxShadow='lg'>
        <Text fontSize='2xl' w={'full'} mb={6} textAlign='center' color={Colors.textRegular}>
          {t('title_cart')}
        </Text>
        <Stack gap={4} w='full' textAlign='start' align='stretch' borderRadius='md' bg={Colors.background} p={4}>
          <HStack>
            <Text flex={2}>{t('cart_column_name')}</Text>
            <Text flex={1}>{t('cart_column_price')}({cart.payment_currency})</Text>
            <Text flex={1}>{t('cart_column_count')}</Text>
            <Text flex={1}>{t('cart_column_actions')}</Text>
          </HStack>
          {cart.medicines && cart.medicines.length > 0 ? cart.medicines.map((med) => (
            <HStack key={med.id}>
              <Text flex={2}>{med.name}</Text>
              <Text flex={1}>{med.price}</Text>
              <NumberInput value={med.count}
                           flex={1}
                           min={1}
                           onChange={(valueString) => changeCartMedicineCount(med.id, Number(valueString))}>
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
              <Box flex={1}><Button colorScheme='red' variant='solid' onClick={() => deleteMedicineFromCart(med.id)}>
                {t('delete_btn')}
              </Button></Box>
            </HStack>
          )) : <Text>{t('cart_no_items_msg')}</Text>}
        </Stack>
        <HStack>
          <Text>{t('cart_pickup_point_text')} {pickupPoint?.location?.country} {pickupPoint?.location?.address}</Text>
          <Button colorScheme='customBlack' onClick={onOpen}>
            {t('change_btn')}
          </Button>
        </HStack>
        {/*<HStack>*/}
        {/*  <Text>Machine (Optional): {machine?.name}</Text>*/}
        {/*  <Button colorScheme='customBlack' onClick={onMachineOpen}>*/}
        {/*    Change*/}
        {/*  </Button>*/}
        {/*</HStack>*/}
        <Text>{t('cart_total_price_text')} {(cart.medicines || []).reduce((totalSum, cur) => {
          return totalSum + cur.count * cur.price;
        }, 0).toFixed(2)} {cart.payment_currency}</Text>
        <Button isDisabled={cart.medicines && cart.medicines.length < 1}
                w='full'
                colorScheme='green'
                onClick={handleCreateOrder}
                isLoading={isLoading}>
          {t('create_order_btn')}
        </Button>

        {/* Pickup Point Modal */}
        <Modal isOpen={isOpen} onClose={onClose} isCentered>
          <ModalOverlay />
          <ModalContent w={'90%'}>
            <ModalHeader>{t('choose_pickup_point_header')}</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <Wrap gap={4} m={4}>
                {pickupPoints
                  .filter(p => !!p.location.country)
                  .map((point) => (
                    <Box key={point.id}
                         p={4}
                         bg={Colors.lightBeige}
                         borderRadius='md'
                         boxShadow='md'
                         _hover={{bg: Colors.primaryBeige}}
                         cursor='pointer'
                         onClick={() => {
                           setPickupPoint(point);
                           onClose();
                           toast({
                             title: t('select_pickup_point_success'),
                             status: 'success',
                             duration: 2000,
                             isClosable: true,
                           });
                         }}>
                      <Text>{point.location.country}</Text>
                      <Text>{point.location.address}</Text>
                      {/*<Text>{point.location.latitude}</Text>*/}
                      {/*<Text>{point.location.longitude}</Text>*/}
                    </Box>
                  ))}
              </Wrap>
            </ModalBody>
          </ModalContent>
        </Modal>

        {/* Machine Modal */}
        <Modal isOpen={isMachineOpen} onClose={onMachineClose} isCentered>
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>{t('choose_machine_header')}</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <Wrap gap={4} m={4}>
                {machines.map((machine) => (
                  <Box key={machine.id}
                       cursor='pointer'
                       p={4}
                       bg={Colors.lightBeige}
                       borderRadius='md'
                       boxShadow='md'
                       _hover={{bg: Colors.primaryBeige}}
                       onClick={() => {
                         setMachine(machine);
                         onMachineClose();
                         toast({
                           title: t('choose_machine_success'),
                           status: 'success',
                           duration: 2000,
                           isClosable: true,
                         });
                       }}>
                    <Text>{machine.name}</Text>
                  </Box>
                ))}
              </Wrap>
            </ModalBody>
            <ModalFooter>
              <Button variant='outline' mr={3} onClick={() => {
                setMachine(null);
                onMachineClose();
              }}>
                {t('clear_selection_btn')}
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </VStack>
    </Center>
  );
};

export default Cart;
