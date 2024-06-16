import React, { useEffect, useState } from 'react';
import {
  Box,
  Drawer,
  DrawerBody,
  DrawerCloseButton,
  DrawerContent,
  DrawerHeader,
  DrawerOverlay,
  Table,
  Tbody,
  Td,
  Text,
  Th,
  Thead,
  Tr,
  useToast,
} from '@chakra-ui/react';
import { Colors } from '@styles/colors';
import * as ApiClient from '@api/client';
import { GetOrderByIdResponseDto, OrderResponseDto } from '@api/client';
import { AppStore } from '@stores/index';

const orderStatuses = ['Created', 'Payed', 'In preparing'/*'Preorder'*/, 'In delivery', 'Completed', 'Canceled', 'Failed'];

const ProfileOrders = () => {
  const [orders, setOrders] = useState<OrderResponseDto[]>([]);
  const [selectedOrder, setSelectedOrder] =
    useState<GetOrderByIdResponseDto | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const toast = useToast();
  const {user} = AppStore.useUserStore();

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const data = await ApiClient.searchOrdersApiV1OrdersSearchPost(
          {requestBody: {user_id: user?.id || ''}});
        setOrders(data);
      } catch (error) {
        console.error('Error fetching orders', error);
        toast({
          title: 'Error fetching orders',
          status: 'error',
          duration: 2000,
          isClosable: true,
        });
      }
    };

    if (user?.id) {
      fetchOrders();
    }
  }, [user, toast]);

  const openDrawer = (order: OrderResponseDto) => {
    const fetchOrders = async () => {
      try {
        const data = await ApiClient.getOrderApiV1OrdersOrderIdGet(
          {orderId: order.id});
        setSelectedOrder(data);
        setIsDrawerOpen(true);
      } catch (error) {
        console.error('Error getting order by id', error);
        toast({
          title: 'Error getting order by id',
          status: 'error',
          duration: 2000,
          isClosable: true,
        });
      }
    };
    fetchOrders();
  };

  const closeDrawer = () => {
    setSelectedOrder(null);
    setIsDrawerOpen(false);
  };

  return (
    <Box px={4}>
      <Text bg={Colors.primaryBeige} fontSize='2xl' color={Colors.textRegular} py={4} textAlign={'center'}>Order
        History</Text>
      <Table variant='simple'>
        <Thead>
          <Tr>
            <Th>ID</Th>
            <Th>Status</Th>
            <Th>Price</Th>
            <Th>Created At</Th>
            <Th>Updated At</Th>
          </Tr>
        </Thead>
        <Tbody>
          {orders.map(order => (
            <Tr key={order.id}
                onClick={() => openDrawer(order)}
                cursor='pointer'
                _hover={{border: `solid ${Colors.middleBeige}`}}>
              <Td>{order.id}</Td>
              <Td>{orderStatuses[order.status]}</Td>
              <Td>{`${order.payment_amount} ${order.payment_currency}`}</Td>
              <Td>{new Date(order.created_at).toLocaleString()}</Td>
              <Td>{new Date(order.updated_at).toLocaleString()}</Td>
            </Tr>
          ))}
        </Tbody>
      </Table>

      <Drawer isOpen={isDrawerOpen} placement='right' onClose={closeDrawer}>
        <DrawerOverlay />
        <DrawerContent>
          <DrawerCloseButton />
          <DrawerHeader>Order Details</DrawerHeader>
          <DrawerBody>
            {selectedOrder && (
              <>
                <Text><strong>ID:</strong> {selectedOrder.id}</Text>
                <Text><strong>Status:</strong> {orderStatuses[selectedOrder.status]}</Text>
                <Text><strong>Price:</strong> {`${selectedOrder.payment_amount} ${selectedOrder.payment_currency}`}
                </Text>
                <Text><strong>Created At:</strong> {new Date(selectedOrder.created_at).toLocaleString()}</Text>
                <Text><strong>Updated At:</strong> {new Date(selectedOrder.updated_at).toLocaleString()}</Text>
                <Text><strong>Medicines:</strong></Text>
                {selectedOrder.order_medicines.map(medicine => (
                  <Box key={medicine.id} ml={4}>
                    <Text>Name: {medicine.medicine?.name}</Text>
                    <Text>Count: {medicine.medicine_count}</Text>
                  </Box>
                ))}
                <Text><strong>Pickup Point:</strong></Text>
                <Box ml={4}>
                  <Text>Country: {selectedOrder.pickup_point.location.country}</Text>
                  <Text>Address: {selectedOrder.pickup_point.location.address}</Text>
                </Box>
                <Text><strong>Machine: </strong> {selectedOrder.machine?.name || 'N/A'}</Text>
                <Text><strong>Arrival At: </strong>
                  {selectedOrder.machine_pickup_point?.arrival_at
                    ? new Date(selectedOrder.machine_pickup_point.arrival_at).toLocaleString() : 'N/A'}
                </Text>
              </>
            )}
          </DrawerBody>
        </DrawerContent>
      </Drawer>
    </Box>
  );
};

export default ProfileOrders;
