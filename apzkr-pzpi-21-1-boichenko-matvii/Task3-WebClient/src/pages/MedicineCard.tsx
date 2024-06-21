import { MedicineResponseDto } from "@api/client";
import React from 'react';
import { Button, Text, VStack } from '@chakra-ui/react';
import { Colors } from '@styles/colors';

export type Medicine = MedicineResponseDto;

interface MedicineCardProps {
  medicine: Medicine;
  onAddToCart: () => void;
}

export const MedicineCard: React.FC<MedicineCardProps> = ({medicine, onAddToCart}) => {
  return (
    <VStack h='full'
            p={5}
            align={'start'}
            shadow='md'
            borderWidth='1px'
            borderRadius='md'
            bg={Colors.primaryBeige}
            _hover={{bg: Colors.middleBeige}}
            gap={3}>
      <Text fontSize='xl' fontWeight='bold'>{medicine.name}</Text>
      <Text>{medicine.description}</Text>
      <Text>Price: {medicine.price} {medicine.currency}</Text>
      {/*<Text>Type: {medicine.type}</Text>*/}
      <Text>Prescription Needed: {medicine.prescription_needed ? 'Yes' : 'No'}</Text>
      <Button mt={'auto'} colorScheme='green' onClick={onAddToCart} justifySelf={'end'}>
        Add to Cart
      </Button>
    </VStack>
  );
};
