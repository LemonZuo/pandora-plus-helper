import apiClient from '../apiClient';
import {UserInfo} from "#/entity.ts";

// import {UserInfo, UserToken} from '#/entity';

export interface SignInReq {
  password: string;
  token?: string
}

// export type SignInRes = UserToken & {user: UserInfo};
export type SignInRes = {
  type: number
  accessToken: string
  user: UserInfo
  loginUrl: string
};

export enum UserApi {
  SignIn = 'login2',
  // SignIn = '/auth/signin',
  Logout = '/auth/logout',
}

const signin = (data: SignInReq) => apiClient.post<SignInRes>({ url: UserApi.SignIn, data });
const logout = () => apiClient.get({ url: UserApi.Logout });

export default {
  signin,
  logout,
};
