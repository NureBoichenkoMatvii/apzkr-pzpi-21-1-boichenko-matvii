import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Flex,
  FormControl,
  FormLabel,
  Grid,
  Input,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  Select,
  Stack,
  Text,
  useDisclosure,
  useToast,
} from '@chakra-ui/react';
import * as ApiClient from '@api/client';
import { MedicineSearchDto } from '@api/client';
import { AppStore } from '@stores/index';
import { Medicine, MedicineCard } from './MedicineCard';
import { Colors } from "@styles/colors.ts";
import { useMutation } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";

const Medicines = () => {
  const {t} = useTranslation();
  const [medicines, setMedicines] = useState<Medicine[]>([]);
  const [filters, setFilters] = useState<MedicineSearchDto>({
    simple_filters: {},
    search_substring: '',
    pagination: {offset: 0, limit: 10},
    order_by: {
      order_by_column: 'name',
      desc: false
    },
  });
  const [selectedMedicine, setSelectedMedicine] = useState<Medicine | null>(null);
  const [quantity, setQuantity] = useState(1);
  const {isOpen, onOpen, onClose} = useDisclosure();
  const toast = useToast();
  const {addToCart} = AppStore.useUserStore();
  const {mutate: fetchMedicines} = useMutation({
    mutationFn: async () => await ApiClient.searchMedicinesApiV1MedicinesSearchPost({
      requestBody: filters,
    }),
    onSuccess: (data) => {
      setMedicines(data);
    },
    onError: error => {
      console.log('fetchMedicines err', error)
      toast({
        title: t('fetch_medicines_error'),
        status: 'error',
        duration: 2000,
        isClosable: true,
      });
    },
  });

  useEffect(() => {
    fetchMedicines();
  }, [filters.pagination]);

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const {name, value, type} = e.target;
    console.log('e.target', type, name, value);
    let newValue: string | undefined = value;
    if (type === 'select-one' && value === 'any')
      newValue = undefined;
    setFilters({
      ...filters,
      simple_filters: {
        ...filters.simple_filters,
        [name]: newValue,
      },
    });
  };

  const handlePaginationChange = (offset: number) => {
    setFilters({
      ...filters,
      pagination: {
        ...filters.pagination,
        offset,
      },
    });
  };

  const handleOrderChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const {name, value} = e.target;
    setFilters({
      ...filters,
      order_by: {
        ...filters.order_by,
        [name]: value === 'true',
      },
    });
  };

  const handleAddToCart = () => {
    if (selectedMedicine) {
      addToCart(selectedMedicine, quantity);
      toast({
        title: t('add_cart_medicine_success'),
        status: 'success',
        duration: 2000,
        isClosable: true,
      });
      onClose();
    }
  };

  return (
    <Box bg={Colors.lightBeige} h='full' px={6}>
      <Box w='full'>
        <Text fontSize='2xl' my={6} textAlign='center' color={Colors.textRegular}>{t('title_medicines')}</Text>
        <Stack direction={{base: 'column', lg: 'row'}}
               spacing={4}
               mb={6}
               bg={Colors.primaryBeige}
               p={8}
               borderRadius='md'
               boxShadow='lg'>
          <FormControl>
            <FormLabel>{t('search_substring_input')}</FormLabel>
            <Input type='text' name='search_substring' onChange={(e) => {
              setFilters({...filters, search_substring: e.target.value,});
            }} value={filters.search_substring || ''} />
          </FormControl>
          <FormControl>
            <FormLabel>{t('prescriptions_needed_label')}</FormLabel>
            <Select name='prescription_needed' onChange={handleFilterChange} defaultValue='any'>
              <option value='true'>{t('y')}</option>
              <option value='false'>{t('n')}</option>
              <option value='any'>{t('any')}</option>
            </Select>
          </FormControl>
          <FormControl>
            <FormLabel>{t('order_by_name_label')}</FormLabel>
            <Select name='desc' onChange={handleOrderChange} value={filters.order_by?.desc + ''}>
              <option value='true'>{t('order_by_descending')}</option>
              <option value='false'>{t('order_by_ascending')}</option>
            </Select>
          </FormControl>
          <Button minW='200px' alignSelf='end' colorScheme='green' onClick={() => fetchMedicines()}>
            {t('search_btn')}
          </Button>
        </Stack>
        <Grid templateColumns='repeat(auto-fill, minmax(250px, 1fr))' gap={6}>
          {medicines.map((medicine) => (
            <MedicineCard key={medicine.id} medicine={medicine} onAddToCart={() => {
              setSelectedMedicine(medicine);
              onOpen();
            }} />
          ))}
        </Grid>
        <Flex align={'center'} justifyContent='center' my={6}>
          <Button w='100px' onClick={() => (filters.pagination?.offset !== undefined
            && handlePaginationChange(filters.pagination.offset - 10))} isDisabled={filters?.pagination?.offset === 0}>
            {t('previous_btn')}
          </Button>
          <Button w='100px' onClick={() => (filters.pagination?.offset !== undefined
            && handlePaginationChange(filters.pagination.offset + 10))} isDisabled={medicines.length < 10}>
            {t('next_btn')}
          </Button>
        </Flex>
      </Box>

      <Modal isOpen={isOpen} onClose={onClose} isCentered>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{t('title_add_to_cart')}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <FormControl>
              <FormLabel>{t('quantity_label')}</FormLabel>
              <Input type='number' value={quantity} onChange={(e) => setQuantity(Number(e.target.value))} min={1} />
            </FormControl>
          </ModalBody>
          <ModalFooter>
            <Button variant='outline' mr={3} onClick={onClose}>{t('cancel_btn')}</Button>
            <Button colorScheme='green' onClick={handleAddToCart}>{t('add_btn')}</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default Medicines;
