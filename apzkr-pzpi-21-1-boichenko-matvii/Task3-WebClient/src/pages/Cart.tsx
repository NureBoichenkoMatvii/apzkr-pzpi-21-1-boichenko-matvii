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

type MedicineInfoDto = {
  id: string;
  count: number;
};

const Cart = () => {
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
        title: 'Error fetching pickup points',
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
        title: 'Error fetching machines',
        status: 'error',
        duration: 2000,
        isClosable: true,
      });
    },
  });

  const handleCreateOrder = async () => {
    if (!pickupPoint) {
      toast({
        title: 'Please select a pickup point',
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
        title: 'Order created successfully',
        status: 'success',
        duration: 2000,
        isClosable: true,
      });
      clearCart();
      navigate('/profile/orders');
    } catch (error) {
      console.error('Error creating order', error);
      toast({
        title: 'Error creating order',
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
          Cart
        </Text>
        <Stack gap={4} w='full' textAlign='start' align='stretch' borderRadius='md' bg={Colors.background} p={4}>
          <HStack>
            <Text flex={2}>Name</Text>
            <Text flex={1}>Price</Text>
            <Text flex={1}>Count</Text>
            <Text flex={1}>Actions</Text>
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
                Delete
              </Button></Box>
            </HStack>
          )) : <Text>No Items</Text>}
        </Stack>
        <HStack>
          <Text>Pickup Point: {pickupPoint?.location?.country} {pickupPoint?.location?.address}</Text>
          <Button colorScheme='customBlack' onClick={onOpen}>
            Change
          </Button>
        </HStack>
        {/*<HStack>*/}
        {/*  <Text>Machine (Optional): {machine?.name}</Text>*/}
        {/*  <Button colorScheme='customBlack' onClick={onMachineOpen}>*/}
        {/*    Change*/}
        {/*  </Button>*/}
        {/*</HStack>*/}
        <Text>Total price: {(cart.medicines || []).reduce((totalSum, cur) => {
          return totalSum + cur.count * cur.price;
        }, 0).toFixed(2)} {cart.payment_currency}</Text>
        <Button isDisabled={cart.medicines && cart.medicines.length < 1}
                w='full'
                colorScheme='green'
                onClick={handleCreateOrder}
                isLoading={isLoading}>
          Create Order
        </Button>

        {/* Pickup Point Modal */}
        <Modal isOpen={isOpen} onClose={onClose} isCentered>
          <ModalOverlay />
          <ModalContent w={'90%'}>
            <ModalHeader>Choose Pickup Point</ModalHeader>
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
                             title: 'Pickup point selected',
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
            <ModalHeader>Choose Machine</ModalHeader>
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
                           title: 'Machine selected',
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
                Clear selection
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </VStack>
    </Center>
  );
};

export default Cart;
