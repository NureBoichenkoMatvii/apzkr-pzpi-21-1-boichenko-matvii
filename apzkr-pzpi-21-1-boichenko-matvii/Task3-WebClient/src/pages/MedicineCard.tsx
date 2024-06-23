import { MedicineResponseDto } from "@api/client";
import React from 'react';
import { Button, Text, VStack } from '@chakra-ui/react';
import { Colors } from '@styles/colors';
import { useTranslation } from "react-i18next";

export type Medicine = MedicineResponseDto;

interface MedicineCardProps {
  medicine: Medicine;
  onAddToCart: () => void;
}

export const MedicineCard: React.FC<MedicineCardProps> = ({medicine, onAddToCart}) => {
  const {t} = useTranslation();

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
      <Text>{t('cart_column_price')}: {medicine.price} {medicine.currency}</Text>
      {/*<Text>Type: {medicine.type}</Text>*/}
      <Text>{t('prescriptions_needed_label')}: {medicine.prescription_needed ? t('y') : t('n')}</Text>
      <Button mt={'auto'} colorScheme='green' onClick={onAddToCart} justifySelf={'end'}>
        {t('title_add_to_cart')}
      </Button>
    </VStack>
  );
};
