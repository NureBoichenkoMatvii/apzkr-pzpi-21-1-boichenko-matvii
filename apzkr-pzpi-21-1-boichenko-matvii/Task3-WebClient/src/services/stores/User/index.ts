import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import { MedicineResponseDto, OpenAPI } from "@api/client";
import { Cart, User } from "@stores/User/types.ts";

interface UserState {
  isSignedIn: boolean;
  language: string;
  token: string | null;
  refresh_token?: string | null;
  cart: Cart;
  user?: User;
}

type Actions = {
  setLanguage: (language: string) => void;
  onSignOut: () => void;
  authorize: (token: string, refresh_token?: string) => void;
  addToCart: (medicine: MedicineResponseDto, count: number) => void;
  changeCartMedicineCount: (medicineId: string, count: number) => void;
  deleteMedicineFromCart: (medicineId: string) => void;
  clearCart: () => void;
  setUser: (user: User) => void;
};

const initialState: UserState = {
  isSignedIn: false,
  language: 'en',
  token: null,
  refresh_token: null,
  cart: {
    payment_currency: 'EUR',
    medicines: []
  },
};

// User store for global state management by Zustand
export const useUserStore = create(
  persist(
    immer<UserState & Actions>((set) => ({
      ...initialState,
      setLanguage: (language) =>
        set((state) => {
          state.language = language;
        }),
      onSignOut: () => {
        console.log('onSignOut')
        OpenAPI.TOKEN = undefined;
        set((state) => {
          state.token = null;
          state.refresh_token = null;
          state.isSignedIn = false;
          state.user = undefined;
        });
      },
      authorize: (token, refresh_token) => {
        OpenAPI.TOKEN = token;
        set((state) => {
          state.token = token;
          state.refresh_token = refresh_token;
          state.isSignedIn = true;
        });
      },
      addToCart: (medicine, count) =>
        set((state) => {
          const existingIndex = state.cart.medicines.findIndex(m => m.id === medicine.id);
          if (existingIndex === -1) {
            state.cart.medicines.push({...medicine, count: count});
          } else {
            state.cart.medicines[existingIndex] = {
              ...medicine, count: count
            }
          }
        }),
      changeCartMedicineCount: (medicineId, count) =>
        set((state) => {
          for (const o of state.cart.medicines)
            if (o.id === medicineId) {
              o.count = count;
              break;
            }
        }),
      deleteMedicineFromCart: (medicineId) =>
        set((state) => {
          state.cart.medicines = state.cart.medicines.filter(m => m.id != medicineId);
        }),
      clearCart: () =>
        set((state) => {
          state.cart = {medicines: []};
        }),
      setUser: (user) => set((state) => {
        state.user = user;
      }),
    })),
    {name: 'user'},
  ),
);
