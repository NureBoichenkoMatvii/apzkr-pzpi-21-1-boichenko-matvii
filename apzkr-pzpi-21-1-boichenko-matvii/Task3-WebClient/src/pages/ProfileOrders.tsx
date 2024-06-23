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
import { useTranslation } from "react-i18next";

const orderStatuses = ['Created', 'Accounted' /*'Payed'*/, 'In preparing'/*'Preorder'*/, 'In delivery', 'Completed', 'Canceled', 'Failed'];

const ProfileOrders = () => {
  const {t} = useTranslation();
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
          title: t('fetch_orders_error'),
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
          title: t('get_order_by_id_error'),
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
      <Text bg={Colors.primaryBeige} fontSize='2xl' color={Colors.textRegular} py={4} textAlign={'center'}>
        {t('title_order_history')}
      </Text>
      <Table variant='simple'>
        <Thead>
          <Tr>
            <Th>{t('id_label')}</Th>
            <Th>{t('status_label')}</Th>
            <Th>{t('price_label')}</Th>
            <Th>{t('created_at_label')}</Th>
            <Th>{t('updated_at_label')}</Th>
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
          <DrawerHeader>{t('order_details_header')}</DrawerHeader>
          <DrawerBody>
            {selectedOrder && (
              <>
                <Text><strong>{t('id_label')}:</strong> {selectedOrder.id}</Text>
                <Text><strong>{t('status_label')}:</strong> {orderStatuses[selectedOrder.status]}</Text>
                <Text><strong>{t('price_label')}:</strong> {`${selectedOrder.payment_amount} ${selectedOrder.payment_currency}`}
                </Text>
                <Text><strong>{t('created_at_label')}:</strong> {new Date(selectedOrder.created_at).toLocaleString()}
                </Text>
                <Text><strong>{t('updated_at_label')}:</strong> {new Date(selectedOrder.updated_at).toLocaleString()}
                </Text>
                <Text><strong>{t('medicines_label')}:</strong></Text>
                {selectedOrder.order_medicines.map(medicine => (
                  <Box key={medicine.id} ml={4}>
                    <Text>{t('name_label')}: {medicine.medicine?.name}</Text>
                    <Text>{t('count_label')}: {medicine.medicine_count}</Text>
                  </Box>
                ))}
                <Text><strong>{t('pickup_point_label')}:</strong></Text>
                <Box ml={4}>
                  <Text>{t('country_label')}: {selectedOrder.pickup_point.location.country}</Text>
                  <Text>{t('address_label')}: {selectedOrder.pickup_point.location.address}</Text>
                </Box>
                <Text><strong>{t('machine_label')}: </strong> {selectedOrder.machine?.name || 'N/A'}</Text>
                <Text><strong>{t('arrival_at_label')}: </strong>
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
