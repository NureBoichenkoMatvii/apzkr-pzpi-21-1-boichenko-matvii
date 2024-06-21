import { Currencies, MedicineResponseDto } from "@api/client";

export enum UserRole {
  Customer = 1,
  Deliverer = 2,
  Admin = 3
}

export interface User {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  birthdate: string | null;
  role: UserRole;
}

export type CartMedicine = MedicineResponseDto & { count: number };

export interface Cart {
  machine_id?: string,
  pickup_point_id?: string,
  payment_currency?: Currencies,
  medicines: CartMedicine[]
}
