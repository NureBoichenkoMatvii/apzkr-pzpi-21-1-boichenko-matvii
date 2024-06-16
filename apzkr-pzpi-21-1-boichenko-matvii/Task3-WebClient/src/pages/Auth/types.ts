//  Login/Register
import { UserRole } from "@api/client";

export interface LoginData {
  username: string;
  password: string;
}

export interface RegisterData {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  birthdate?: string;
  role: UserRole;
}

export interface PasswordChangeData {
  oldPassword?: string;
  newPassword: string;
  newPasswordConfirm: string;
}
