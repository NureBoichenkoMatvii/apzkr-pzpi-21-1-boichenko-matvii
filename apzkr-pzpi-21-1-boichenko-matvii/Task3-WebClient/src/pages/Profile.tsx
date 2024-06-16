import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Flex,
  FormControl,
  FormErrorMessage,
  FormLabel,
  HStack,
  Input,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  Spinner,
  Stack,
  Switch,
  Text,
  useDisclosure,
  useToast
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { Colors } from '@styles/colors';
import { PasswordChangeData } from './Auth/types.ts';
import * as ApiClient from '@api/client';
import { AppStore } from "@stores/index.ts";
import { UserRole } from "@stores/User/types.ts";
import { useMutation } from "@tanstack/react-query";

const Profile = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [passwordChangeData, setPasswordChangeData] =
    useState<PasswordChangeData>({oldPassword: '', newPassword: '', newPasswordConfirm: ''});
  const {isOpen, onOpen, onClose} = useDisclosure();
  const toast = useToast();
  const navigate = useNavigate();
  const {user, onSignOut, setUser} = AppStore.useUserStore();
  const {mutate: fetchUser} = useMutation({
    mutationFn: async () => await ApiClient.usersCurrentUserApiV1UsersMeGet(),
    onSuccess: (res) => {
      setUser(res);
    },
    onError: error => {
      console.log('fetchUser err', error)
      toast({
        title: 'Error fetching user data',
        status: 'error',
        duration: 2000,
        isClosable: true,
      });
      navigate('/login');
    },
  });

  useEffect(() => {
    fetchUser();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (user) {
      const {name, value} = e.target;
      setUser({...user, [name]: value});
    }
  };

  const handleSave = async () => {
    try {
      if (user) {
        const updateUserBody = {
          ...user,
          birthdate: user.birthdate ? new Date(user.birthdate).toISOString() : null,
        };
        const updatedUser = await ApiClient.usersPatchCurrentUserApiV1UsersMePatch(
          {requestBody: updateUserBody});
        setUser(updatedUser);
        setIsEditing(false);
        toast({
          title: 'User updated successfully',
          status: 'success',
          duration: 2000,
          isClosable: true,
        });
      }
    } catch (error) {
      toast({
        title: 'Error updating user data',
        status: 'error',
        duration: 2000,
        isClosable: true,
      });
    }
  };

  const handleLogout = () => {
    onSignOut();
    navigate('/login');
    toast({
      title: 'Logged out successfully',
      status: 'success',
      duration: 2000,
      isClosable: true,
    });
  };

  const handlePasswordChange = async () => {
    // Change user password via API
    try {
      if (passwordChangeData.newPassword !== passwordChangeData.newPasswordConfirm) {
        toast({
          title: 'Passwords do not match',
          status: 'error',
          duration: 2000,
          isClosable: true,
        });
        return;
      }
      if (user) {
        await ApiClient.usersPatchCurrentUserApiV1UsersMePatch(
          {requestBody: {password: passwordChangeData.newPassword}});
        toast({
          title: 'Password changed successfully',
          status: 'success',
          duration: 2000,
          isClosable: true,
        });
        onClose();
      }
    } catch (error) {
      toast({
        title: 'Error changing password',
        status: 'error',
        duration: 2000,
        isClosable: true,
      });
    }
  };

  const handlePasswordChangeInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const {name, value} = e.target;
    setPasswordChangeData({...passwordChangeData, [name]: value});
  };

  if (!user) {
    return (
      <Box bg={Colors.background} minH='100vh' display='flex' justifyContent='center' alignItems='center'>
        <Spinner size='xl' />
      </Box>
    );
  }

  return (
    <Box bg={Colors.background} h='full' py={12} px={6}>
      <Box maxW='md' mx='auto' p={8} bg={Colors.primaryBeige} borderRadius='md' boxShadow='lg'>
        <Text fontSize='2xl' mb={6} textAlign='center' color={Colors.textRegular}>Profile</Text>
        {isEditing ? (
          <form>
            <Stack spacing={4}>
              <FormControl id='first_name' isRequired>
                <FormLabel>First Name</FormLabel>
                <Input type='text' name='first_name' value={user.first_name} onChange={handleChange} />
              </FormControl>
              <FormControl id='last_name' isRequired>
                <FormLabel>Last Name</FormLabel>
                <Input type='text' name='last_name' value={user.last_name} onChange={handleChange} />
              </FormControl>
              <FormControl id='email' isRequired>
                <FormLabel>Email</FormLabel>
                <Input type='email' name='email' value={user.email} onChange={handleChange} />
              </FormControl>
              <FormControl id='birthdate'>
                <FormLabel>Birthdate</FormLabel>
                <Input type='date'
                       name='birthdate'
                       value={user.birthdate ? new Date(user.birthdate).toISOString().split('T')[0] : ''}
                       onChange={handleChange} />
              </FormControl>
              <FormControl id='role'>
                <Flex justifyContent='start' alignItems='center' gap='15px'>
                  <Text>Is Deliverer</Text>
                  <Switch colorScheme='green' isChecked={user.role === UserRole.Deliverer} onChange={(e) =>
                    setUser({...user, role: e.target.checked ? UserRole.Deliverer : UserRole.Customer})} />
                </Flex>
              </FormControl>
              <HStack w='full' gap='20px'>
                <Button flex={1} variant='outline' onClick={() => setIsEditing(false)}>Cancel</Button>
                <Button flex={1} onClick={handleSave} colorScheme='green' bg={Colors.primaryGreen}>Save</Button>
              </HStack>
            </Stack>
          </form>
        ) : (
          <Stack spacing={4}>
            <Text><strong>First Name:</strong> {user.first_name}</Text>
            <Text><strong>Last Name:</strong> {user.last_name}</Text>
            <Text><strong>Email:</strong> {user.email}</Text>
            <Text><strong>Birthdate:</strong> {user.birthdate ? new Date(user.birthdate).toISOString().split('T')[0] : ''}
            </Text>
            <Text><strong>Role:</strong> {user.role === UserRole.Customer ? 'Customer' : 'Deliverer'}</Text>
            <Button onClick={() => setIsEditing(true)} colorScheme='green' variant='outline' width='full'>Edit
              Profile</Button>
            <Button onClick={onOpen} colorScheme='customBlack' variant='outline' width='full'>Change Password</Button>
            <Button onClick={handleLogout} colorScheme='red' variant='outline' width='full'>Logout</Button>
          </Stack>
        )}
        <Modal isCentered isOpen={isOpen} onClose={onClose}>
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>Change Password</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <FormControl id='new_password' isRequired mt={4}>
                <FormLabel>New Password</FormLabel>
                <Input type='password'
                       name='newPassword'
                       value={passwordChangeData.newPassword}
                       onChange={handlePasswordChangeInput} />
              </FormControl>
              <FormControl id='new_password_confirm' isRequired mt={4}
                // isInvalid={!!passwordChangeData.newPasswordConfirm && passwordChangeData.newPasswordConfirm !== passwordChangeData.newPassword}>
              >
                <FormLabel>Confirm New Password</FormLabel>
                <Input name='newPasswordConfirm'
                       type='password'
                       value={passwordChangeData.newPasswordConfirm}
                       onChange={handlePasswordChangeInput} />
                <FormErrorMessage>
                  Passwords don't match
                </FormErrorMessage>
              </FormControl>
            </ModalBody>
            <ModalFooter>
              <Button variant='outline' mr={3} onClick={onClose}>Cancel</Button>
              <Button colorScheme='green' bg={Colors.primaryGreen} onClick={handlePasswordChange}>Submit</Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </Box>
    </Box>
  );
};

export default Profile;
